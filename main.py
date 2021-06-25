#coding: utf-8

# MultiMascon 主プロセス(デーモン)
import os
import LogRotate
from multiprocessing import Process, Queue
import DSAir2
import time
import sys
import random
from Mascon import Mascon
from OHC_PC01A import OHC_PC01A
from DENSYA_CON_T01 import DENSYA_CON_T01
import pygame

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
# demo code
mascons.append(OHC_PC01A())

command_queue = Queue()

# DSAirとの通信用のプロセスをつくる
if not 'dsair' in excludes:
    dsair_process = Process(target=DSAir2.Worker, args=(dsair_port, command_queue))
    # 親プロセスが死んだら自動的に終了
    dsair_process.daemon = True
    dsair_process.start()

# TODO RasPiの青ランプつける

last_loop_time = time.time()
last_db_check = time.time()
last_usb_check = time.time()
while True:
    try:
        if not 'dsair' in excludes and not dsair_process.is_alive():
            raise ValueError('DSAir2プロセスが起動していません')
        
        # ここまでで処理しきれなかったコマンドは積み上がる一方なので飛ばす
        while True:
            try:
                command_queue.get_nowait()
            except queue.Empty:
                break
            
            # 特定のマスコンからの命令だけが処理されないようにシャッフルする
            random.shuffle(mascons)
            for mascon in mascons:
                #TODO マスコン(列車)からコマンドを受領する
                commands = [] # 追加
                
                # キューに溜まったコマンド数(開発用)
                print('command_queue size: ' + str(command_queue.qsize()))
                for command in commands:
                    command_queue.put(command)
            
            # 5秒に1回SQLiteに問い合わせて各マスコン(列車)のパラメータを反映
            if (time.time() - last_db_check) > 5.0:
                # TODO: SQLite問い合わせ
                last_db_check = time.time()
                pass
            
            # 1秒に一回pyusbで接続・抜取情報を取得する
            if (time.time() - last_usb_check) > 1.0:
                #TODO: pyusbで情報取得してmasconsに入れたり抜いたりする
                last_usb_check = time.time()
                pass

            # メインループにかかった時間(開発用)
            main_loop_time = time.time() - last_loop_time
            print('main loop: ' + str(main_loop_time))
            # メインループは0.05 ~ 0.4秒とする
            time.sleep(max(0.4 - main_loop_time, 0.05))
            last_loop_time = time.time()
    
    # 緊急停止時
    finally:
        dsair_process.close()
        # RasPiの青ランプ消す
