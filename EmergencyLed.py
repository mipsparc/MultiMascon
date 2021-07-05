#coding:utf-8

# 異常時にLEDを点灯したままプログラムを終了させるためのゾンビプログラム

import time

def Worker():
    from gpiozero import LED
    led = LED(15);
    led.on();
    while True:
        time.sleep(1)
