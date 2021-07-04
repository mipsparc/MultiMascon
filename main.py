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
import EmergencyLed

# Pygameをヘッドレスでも動かせるように対策
os.environ['SDL_VIDEODRIVER'] = 'dummy'

excludes = sys.argv[1:]
# ex) python3 main.py log dsair

# TODO databaseディレクトリにログを記録する
# TODO ログをWebUIから見れるようにする
# 標準エラー出力をログファイルにする
if not 'log' in excludes:
    LOG_DIR = 'log'
    os.makedirs(LOG_DIR, exist_ok=True)
    sys.stderr = open(LOG_DIR + '/' + str(int(time.time())) + '.txt', 'w')
    LogRotate.rotate(LOG_DIR)
    
pygame.init()

mascons = []
# TODO demo code (本来はメインループで取得する)
mascons.append(OHC_PC01A())

command_queue = Queue()

if israspi.is_raspi:
    from gpiozero import LED
    led = LED(15)
    led.on()

# TODO 異常時などステータスを上位にshared memで伝達する
# DSAirとの通信プロセスをつくる
if not 'dsair' in excludes:
    dsair_process = Process(target=DSAir2.Worker, args=(command_queue))
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
while True:
    try:
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
            if time.time() % 1 > 0.5:
                led.on()
            else:
                led.off()

        # メインループにかかった時間(開発用)
        main_loop_time = time.time() - last_loop_time
        if main_loop_time > 0.1:
            print('main loop: ' + str(main_loop_time))
        last_loop_time = time.time()

        #確実に一周がMAIN_LOOP時間とする
        time.sleep(max(MAIN_LOOP - main_loop_time, 0))
    
    # 緊急停止時
    except:
        # 点灯しっぱなしは異常という考え方
        if israspi.is_raspi:
            led.close()
            emg_led_process = Process(target=EmergencyLed.Worker)
            emg_led_process.start()

        while True:
            try:
                command_queue.get_nowait()
            except queue.Empty:
                break
        
        Command.reset(command_queue)
        time.sleep(0.5)
        if not 'dsair' in excludes:
            dsair_process.kill()

        raise
