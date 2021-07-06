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
from OHC_PC01A import OHC_PC01A
from DENSYA_CON_T01 import DENSYA_CON_T01
import pygame
from Command import Command
import israspi
import pathlib
from subprocess import Popen

# Pygameをヘッドレスでも動かせるように対策
os.environ['SDL_VIDEODRIVER'] = 'dummy'

excludes = sys.argv[1:]
# ex) python3 main.py log dsair

# TODO ログをWebUIから見れるようにする
# 標準エラー出力をログファイルにする
if not 'log' in excludes:
    if israspi.is_raspi:
        LOG_DIR = '/mnt/database/log/'
    else:
        LOG_DIR = './log/'
    os.makedirs(LOG_DIR, exist_ok=True)
    last_log_files = [str(p) for p in pathlib.Path(LOG_DIR).iterdir()]
    if last_log_files == []:
        last_log_filenum = 0
    else:
        last_log_files.sort()
        last_log_filenum = int(os.path.basename(last_log_files[-1]).split('.', 1)[0])
    sys.stderr = open(LOG_DIR + '/' + str(last_log_filenum + 1) + '.txt', 'w')
    LogRotate.rotate(LOG_DIR)
    
pygame.init()

mascons = []
# TODO demo code (本来はメインループで取得する)
#mascons.append(OHC_PC01A())

command_queue = Queue()

if israspi.is_raspi:
    from gpiozero import LED
    led = LED(15)
    led.on()

# DSAirとの通信プロセスをつくる
if not 'dsair' in excludes:
    dsair_process = Process(target=DSAir2.Worker, args=(command_queue,))
    # 親プロセスが死んだら自動的に終了
    dsair_process.daemon = True
    dsair_process.start()

# DCCモード起動
Command.switchToDCC(command_queue)
time.sleep(1)

last_loop_time = time.time()
last_db_check = 0
last_usb_check = 0

# メインループは送信の余裕を持って0.5秒で回す
MAIN_LOOP = 0.5

print('起動完了')
try:
    while True:
        if not 'dsair' in excludes and not dsair_process.is_alive():
            raise ValueError('DSAir2プロセスが起動していません')
        
        # 5個以上積み上がったコマンドは飛ばす
        for i in range(min(command_queue.qsize() - 5, 0)):
            try:
                command_queue.get_nowait()
                print('dropped queue')
            except queue.Empty:
                break
        
        # 特定のマスコンからの命令だけが処理されないように毎回シャッフルする
        random.shuffle(mascons)
        for mascon in mascons:
            mascon.advanceTime(command_queue)
        
        # 5秒に1回SQLiteに問い合わせて各マスコン(列車)のパラメータを反映
        if (time.time() - last_db_check) > 5.0:
            for mascon in mascons:
                mascon.fetchDatabase()
            last_db_check = time.time()
        
        # 1秒に一回pyusbで接続・抜取情報を取得する
        if (time.time() - last_usb_check) > 1.0:
            #TODO: pyusbで情報取得してmasconsに入れたり抜いたりする
            last_usb_check = time.time()
            pass
        
        if israspi.is_raspi:
            if time.time() % 2 > 1.0:
                led.on()
            else:
                led.off()

        # メインループにかかった時間(開発用)
        main_loop_time = time.time() - last_loop_time
        if main_loop_time > 0.1:
            print('main loop: ' + str(main_loop_time))

        #確実に一周がMAIN_LOOP時間とする
        time.sleep(max(MAIN_LOOP - main_loop_time, 0))
        
        last_loop_time = time.time()
    
except KeyboardInterrupt:
    is_no_problem = True
    
# 緊急停止時
except:
    # 点灯しっぱなしは異常という考え方
    if israspi.is_raspi:
        led.close()
        emg_path = os.path.dirname(__file__) + '/EmergencyLed.py'
        Popen(f'sleep 1; python3 {emg_path}', shell=True)
        
finally:
    while True:
        try:
            command_queue.get_nowait()
        except queue.Empty:
            break
    
    Command.reset(command_queue)
    time.sleep(0.5)
    if not 'dsair' in excludes:
        dsair_process.kill()
        
    if is_no_problem:
        exit()
    else:
        raise
