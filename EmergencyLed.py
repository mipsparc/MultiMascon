#coding:utf-8

# 異常時にLEDを点灯したままプログラムを終了させるためのゾンビプログラム

import time
from gpiozero import LED

def Worker():
    led = LED(15);
    led.on();
    while True:
        time.sleep(1)
