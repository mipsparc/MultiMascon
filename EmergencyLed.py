#coding:utf-8

# 異常時にLEDを高速点滅したままプログラムを終了させるためのゾンビプログラム

import time
from gpiozero import LED

led = LED(15);
while True:
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)
    led.on()
