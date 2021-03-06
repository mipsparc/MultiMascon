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
import pathlib
from subprocess import Popen
import logging
import signal
from USBUtil import USBUtil
from MasconManager import MasconManager
from Button import Button
from gpiozero import LED
from Keyboard import Keyboard


# 安全にプログラムを終了する
def safe_halt(*args):
    # 高速点滅は異常
    if not is_no_problem:
        led.close()
        emg_path = os.path.dirname(__file__) + '/EmergencyLed.py'
        Popen(f'sleep 1; python3 {emg_path}', shell=True)
    
    Command.reset(command_queue)
    # DSAir2プロセスにより緊急停止が送信されるのを待つ(ふつうはSIGTERMですぐに停止する)
    time.sleep(1)

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
    LOG_DIR = '/mnt/database/log/'
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


# 前回の異常終了警告プロセスがあったら止める
Popen('pkill -f "EmergencyLed"', shell=True)
# ステータスLEDをGPIOに割り付ける
led = LED(15)

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

try:
    mascon_manager = MasconManager()
    button = Button()
    button.getProfile()
    keyboard = Keyboard()
    keyboard.getProfile()
    keyboard.startScan()

    USBUtil.init()
    USBUtil.startMasconMonitor()

    logger.info('起動完了')
    # メインループ
    while True:
        if not dsair_process.is_alive():
            raise RuntimeError('DSAir2プロセスが終了しています')
        
        # 15個以上積み上がったコマンドは飛ばす
        for i in range(max(command_queue.qsize() - 15, 0)):
            logger.error('コマンドキューが溢れました')
            try:
                command_queue.get_nowait()
            except queue.Empty:
                break
        
        # 特定のマスコンからの命令だけが処理されないように毎回シャッフルする
        ports = list(mascon_manager.mascons.keys())
        random.shuffle(ports)
        buttons_responses = []
        for port in ports:
            mascon = mascon_manager.mascons[port]
            # それぞれのマスコンのループを実行する
            buttons_response = mascon.advanceTime(command_queue)
            buttons_responses.append(buttons_response)
        
        # 押されたキー情報を元にファンクション・アクセサリ指令
        pressed_keys = keyboard.getPressed()
        
        button.processButtons(buttons_responses, command_queue)
        button.processPressedKeys(pressed_keys, command_queue)
        
        # button_responsesの中にマスコンで接続されているDCCアドレスがあるためつかう
        keyboard.runControl(buttons_responses, command_queue)
        
        # 5秒に1回DBに問い合わせ
        if (time.time() - last_db_check) > 5.0:
            # 各マスコン(列車)のパラメータを反映
            for port, mascon in mascon_manager.mascons.items():
                mascon.fetchDatabase()

            button.getProfile()
            keyboard.getProfile()
            last_db_check = time.time()
        
        # 1秒に1回pyusbで接続・抜取情報を取得する
        if (time.time() - last_usb_check) > 1.0:
            adds, remove_ports = USBUtil.sumUSBEvents()
            mascon_manager.removeControl(remove_ports, command_queue)
            mascon_manager.addControl(adds)
            last_usb_check = time.time()
        
        # 9秒に1回、なにもなくてもDSAirとの接続を検証する
        if (time.time() - last_ping_check) > 9.0:
            Command.setPing(command_queue)
            last_ping_check = time.time()
        
        if time.time() % 2 > 1.0:
            led.on()
        else:
            led.off()

        # メインループにかかった時間(開発用)
        main_loop_time = time.time() - last_loop_time
        if main_loop_time > 0.4:
            logger.debug('メインループ時間が長いです: ' + str(main_loop_time))

        #確実に一周がMAIN_LOOP時間とする
        time.sleep(max(MAIN_LOOP - main_loop_time, 0))
        
        last_loop_time = time.time()
    
except KeyboardInterrupt:
    pass

except Exception as e:
    logger.exception('異常が発生')
    is_no_problem = False

# 常に列車を停止させる
finally:
    safe_halt()
