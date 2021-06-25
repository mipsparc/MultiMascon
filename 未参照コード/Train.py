#coding: utf-8

# サブプロセスとして、各列車とそれに割り当てられたコントローラ入力の管理をする

import time
import sys
import os
from Smooth import Speed

# メインループを0.1秒おきに回すためのunix timeカウンタ
last_counter = time.time()

try:
    while True:
        # DE10モデルオブジェクトに入力を与える
        # ...
        EC.advanceTime()
        speed = EC.getSpeed()
                
        kph = max(speed * 3600 / 1000, 0)
        
        print('{}km/h  BC: {}'.format(int(kph), int(EC.getBc())))

        if speed <= 0:
            speed_out = 0
        else:
            speed_out = Speed.getValue(kph)
        dsair2.move(speed_out, EC.getWay())

        sleep_time = max(0.1 - (time.time() - last_counter), 0)
        time.sleep(sleep_time)
        last_counter = time.time()

# Ctrl-c押下時
except Exception as e:
    dsair2.move(0, 0)
    dsair2.move(0, 0)
    time.sleep(0.5)

    raise
