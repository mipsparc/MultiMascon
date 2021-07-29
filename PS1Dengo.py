#coding: utf-8

# PS1版電車でGOコントローラ(現状ELECOM製変換アダプタ JC-PS201Uにのみ対応)をPythonにつなぐライブラリ
# ワンハンドル、ツーハンドルともに対応しています

# 最初にブレーキゆるめ→非常、0ノッチ→フルノッチを行ってください。
# これにより正しいデータが出力されるようになります

import pygame
import time
from Joystick import Joystick
from Button import Button
import logging

class PS1Dengo(Joystick):
    # ジョイスティックのボタン数
    BUTTON_NUM = 16
    
    BRAKE_TYPE = Joystick.BRAKE_TYPE_KNOTCH
    ACCEL_KNOTCH_NUM = 5
    BRAKE_KNOTCH_NUM = 9
    way = 0

    def loadStatus(self):
        try:
            self.joy
        except:
            self.invalid = True
        
        pygame.event.get()
        buttons = [0] * self.BUTTON_NUM
        for i in range(self.BUTTON_NUM):
            buttons[i] = self.joy.get_button(i)

        self.buttons = []
        result = self.arrangeJoyData(buttons)
        self.accel_knotch = result['mascon']
        self.brake_knotch = result['brake']
        
    def arrangeJoyData(self, buttons):
        if buttons[9]:
            # SELECT
            self.buttons.append(Button.PS1_DENGO_SELECT)
        elif buttons[8]:
            # START
            self.buttons.append(Button.PS1_DENGO_START)
        elif buttons[3]:
            # A
            self.way = 1
        elif buttons[2]:
            # B
            self.way = 0
        elif buttons[1]:
            # C
            self.way = 2
        
        buttons[9] = 0
        buttons[8] = 0
        buttons[3] = 0
        buttons[2] = 0
        buttons[1] = 0
        
        button_value = int(''.join(map(str, buttons)), 2) << 1
        # 最初は-10の値が出る。ガチャガチャしてると正しい値が出る
        if button_value == 4618:
            mascon = 0
            brake = 8
        elif button_value == 5642:
            mascon = 0
            brake = 7
        elif button_value == 2058:
            mascon = 0
            brake = 6
        elif button_value == 3082:
            mascon = 0
            brake = 5
        elif button_value == 6154:
            mascon = 0
            brake = 4
        elif button_value == 7178:
            mascon = 0
            brake = 3
        elif button_value == 2570:
            mascon = 0
            brake = 2
        elif button_value == 3594:
            mascon = 0
            brake = 1
        elif button_value == 6666:
            mascon = 0
            brake = 0
        elif button_value == 72200:
            mascon = 1
            brake = 0
        elif button_value == 6664:
            mascon = 2
            brake = 0
        elif button_value == 72194:
            mascon = 3
            brake = 0
        elif button_value == 6658:
            mascon = 4
            brake = 0
        elif button_value == 72192:
            mascon = 5
            brake = 0
        else:
            mascon = 0
            brake = 9
        
        return {'mascon': mascon, 'brake': brake}

        
if __name__ == '__main__':
    pass
