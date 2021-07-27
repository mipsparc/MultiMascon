#coding: utf-8

# MultiMascon 主プロセス(デーモン)
import os
import LogRotate
from multiprocessing import Process, Queue
import queue
import DSAir2
import time
import sys
import random
from Mascon import Mascon
from Command import Command
import israspi
import pathlib
from subprocess import Popen
import logging
import signal
from USBUtil import USBUtil
from MasconManager import MasconManager
from Button import Button

# 安全にプログラムを終了する
def safe_halt(*args):
    # 高速点滅は異常
    if israspi.is_raspi and not is_no_problem:
        led.close()
        emg_path = os.path.dirname(__file__) + '/EmergencyLed.py'
        Popen(f'sleep 1; python3 {emg_path}', shell=True)

    # 残指令キューをすべて破棄する
    while True:
        try:
            command_queue.get_nowait()
        except queue.Empty:
            break
    
    # DSAirをリセットしてすべての列車を停止する
    Command.reset(command_queue)
    time.sleep(0.5)

    if is_no_problem:
        logger.info('正常終了しました')
        exit()
    else:
        try:
            raise e
        except NameError:
            exit()

# Pygameをヘッドレスでも動かせるように対策
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# 正常終了であればTrue
is_no_problem = True

excludes = sys.argv[1:]
# ex) python3 main.py log

logger = logging.getLogger(__name__)
if not 'log' in excludes:
    if israspi.is_raspi:
        LOG_DIR = '/mnt/database/log/'
    else:
        LOG_DIR = './log/'
    os.makedirs(LOG_DIR, exist_ok=True)
    last_log_filenums = [int(p.stem) for p in pathlib.Path(LOG_DIR).iterdir()]
    if last_log_filenums == []:
        log_filenum = 1
    else:
        log_filenum = max(last_log_filenums) + 1
        
    logging.basicConfig(filename=LOG_DIR + f'/{log_filenum}.txt', level=logging.INFO)
    LogRotate.rotate(LOG_DIR)
else:
    logging.basicConfig(level=logging.INFO)

signal.signal(signal.SIGTERM, safe_halt)

command_queue = Queue()

if israspi.is_raspi:
    # 前回の異常終了警告プロセスがあったら止める
    Popen('pkill -f "EmergencyLed"', shell=True)
    from gpiozero import LED
    led = LED(15)
    led.on()

# DSAirとの通信プロセスをつくる
dsair_process = Process(target=DSAir2.Worker, args=(command_queue, logger))
# 親プロセスが死んだら自動的に終了
dsair_process.daemon = True
dsair_process.start()
time.sleep(1)
    
last_loop_time = time.time()
last_db_check = 0
last_usb_check = 0
last_ping_check = time.time()

# メインループは送信の余裕を持って0.5秒で回す
MAIN_LOOP = 0.5

mascon_manager = MasconManager()

try:
    USBUtil.init()
    USBUtil.startMasconMonitor()

    logger.info('起動完了')
    while True:        
        if not 'dsair' in excludes and not dsair_process.is_alive():
            logger.error('DSAir2プロセスが終了しています')
            raise RuntimeError('DSAir2プロセスが終了しています')
        
        # 10個以上積み上がったコマンドは飛ばす
        for i in range(max(command_queue.qsize() - 15, 0)):
            logger.error('コマンドキューが溢れました')
            try:
                command_queue.get_nowait()
            except queue.Empty:
                break
        
        # 特定のマスコンからの命令だけが処理されないように毎回シャッフルする
        ports = list(mascon_manager.mascons.keys())
        random.shuffle(ports)
        button_responses = []
        for port in ports:
            mascon = mascon_manager.mascons[port]
            button_responses.append(mascon.advanceTime(command_queue))
            
        # button_responsesに基づいてアクションを起こす
        Button.processButtons(button_responses, command_queue)
        
        # 5秒に1回DBに問い合わせて各マスコン(列車)のパラメータを反映
        if (time.time() - last_db_check) > 5.0:
            for port, mascon in mascon_manager.mascons.items():
                mascon.fetchDatabase()
            last_db_check = time.time()
        
        # 1秒に1回pyusbで接続・抜取情報を取得する
        if (time.time() - last_usb_check) > 1.0:
            adds, remove_ports = USBUtil.sumUSBEvents()
            mascon_manager.removeControl(remove_ports, command_queue)
            mascon_manager.addControl(adds)
            last_usb_check = time.time()
        
        # 5秒に1回、なにもなくてもDSAirとの接続を検証する
        if (time.time() - last_ping_check) > 5.0:
            Command.setPing(command_queue)
            last_ping_check = time.time()
        
        if israspi.is_raspi:
            if time.time() % 2 > 1.0:
                led.on()
            else:
                led.off()

        # メインループにかかった時間(開発用)
        main_loop_time = time.time() - last_loop_time
        if main_loop_time > 0.4:
            logger.warning('main loop: ' + str(main_loop_time))

        #確実に一周がMAIN_LOOP時間とする
        time.sleep(max(MAIN_LOOP - main_loop_time, 0))
        
        last_loop_time = time.time()
    
except KeyboardInterrupt:
    pass

except Exception as e:
    logger.warning('異常が発生', exc_info=True)
    is_no_problem = False

# 正常・異常終了時
finally:
    safe_halt()
