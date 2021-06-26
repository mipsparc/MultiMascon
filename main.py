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

# Pygameをヘッドレスでも動かせるように対策
os.environ["SDL_VIDEODRIVER"] = "dummy"
# DSAir2のポート
dsair_port = '/dev/ttyUSB0'

excludes = sys.argv[1:]
# ex) python3 main.py log dsair

# 標準エラー出力をログファイルにする
# log が入っていたら普通に出力する
if not 'log' in excludes:
    LOG_DIR = 'log'
    os.makedirs(LOG_DIR, exist_ok=True)
    sys.stderr = open(LOG_DIR + '/' + str(int(time.time())) + '.txt', 'w')
    LogRotate.rotate(LOG_DIR)
    
pygame.init()

mascons = []
# demo code (本来はメインループで取得する)
mascons.append(OHC_PC01A())

command_queue = Queue()

# DSAirとの通信プロセスをつくる
if not 'dsair' in excludes:
    dsair_process = Process(target=DSAir2.Worker, args=(dsair_port, command_queue))
    # 親プロセスが死んだら自動的に終了
    dsair_process.daemon = True
    dsair_process.start()

if not 'raspi' in excludes:
    # TODO RasPiの青ランプつける
    pass

# DCCモード起動
Command.switchToDCC(command_queue)
time.sleep(3)

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

        # メインループにかかった時間(開発用)
        main_loop_time = time.time() - last_loop_time
        if main_loop_time > 0.1:
            print('main loop: ' + str(main_loop_time))

        time.sleep(max(MAIN_LOOP - main_loop_time, 0))
        last_loop_time = time.time()
    
    # 緊急停止時
    except:
        while True:
            try:
                command_queue.get_nowait()
            except queue.Empty:
                break
        
        Command.reset(command_queue)
        time.sleep(0.5)
        # TODO: RasPiの青ランプ消す
        
        dsair_process.kill()
        raise
