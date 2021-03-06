#coding: utf-8

# PS1版電車でGOコントローラ(現状ELECOM製変換アダプタ JC-PS101Uにのみ対応)をPythonにつなぐライブラリ
# ワンハンドル、ツーハンドルともに対応しています

# 最初にブレーキゆるめ→非常、0ノッチ→フルノッチをゆっくりと行ってください。ブレーキ不緩解になったときも同じことをしてください。
# これにより正しいデータが出力されるようになります

import pygame
import time
from Joystick import Joystick
from Button import Button
import logging

class PS1Dengo(Joystick):
    # ジョイスティックのボタン数
    BUTTON_NUM = 12
    
    BRAKE_TYPE = Joystick.BRAKE_TYPE_KNOTCH
    ACCEL_KNOTCH_NUM = 5
    BRAKE_KNOTCH_NUM = 9

    buttons = []

    def loadStatus(self):
        try:
            self.joy
        except:
            self.invalid = True
        
        self.buttons = []
        
        results = []
        
        for i in range(2):
            pygame.event.get()
            buttons = [0] * self.BUTTON_NUM
            for i in range(self.BUTTON_NUM):
                buttons[i] = self.joy.get_button(i)
            ax = self.joy.get_axis(0)
            ax2 = self.joy.get_axis(1)
            
            # 未接続時
            if ax2 >= 0:
                return

            if ax < 0:
                buttons += [1, 1]
            elif ax == 0.0:
                buttons += [0, 0]
            else: # ax > 0
                buttons += [0, 1]
            
            results.append(self.arrangeJoyData(buttons))
        
        # 2回連続で同じ値が取れなかったら無効
        if results[0] != results[1]:
            return

        if result['mascon'] is not None and result['brake'] is not None:
            self.accel_knotch = result['mascon']
            self.brake_knotch = result['brake']
        if result['way'] is not None:
            self.way = result['way']
        
    @classmethod
    def arrangeJoyData(self, buttons):
        way = None
        if buttons[9]:
            # SELECT
            #self.buttons.append(Button.PS1_DENGO_SELECT)
            way = 0
        elif buttons[8]:
            # START
            self.buttons.append(Button.PS1_DENGO_START)
        elif buttons[3]:
            # A
            way = 1
        elif buttons[2]:
            # B
            #self.way = 0
            # たまに勝手に出る
            pass
        elif buttons[1]:
            # C
            way = 2
                        
        buttons[9] = 0
        buttons[8] = 0
        buttons[3] = 0
        buttons[2] = 0
        buttons[1] = 0
        
        button_value = int(''.join(map(str, buttons)), 2) << 1

        if button_value == 6:
            mascon = 0
            brake = 9
        elif button_value == 1158:
            mascon = 0
            brake = 8
        elif button_value == 1414:
            mascon = 0
            brake = 7
        elif button_value == 518:
            mascon = 0
            brake = 6
        elif button_value == 774:
            mascon = 0
            brake = 5
        elif button_value == 1542:
            mascon = 0
            brake = 4
        elif button_value == 1798:
            mascon = 0
            brake = 3
        elif button_value == 646:
            mascon = 0
            brake = 2
        elif button_value == 902:
            mascon = 0
            brake = 1
        elif button_value == 1670:
            mascon = 0
            brake = 0
        elif button_value == 18050:
            mascon = 1
            brake = 0
        elif button_value == 1666:
            mascon = 2
            brake = 0
        elif button_value == 18054:
            mascon = 3
            brake = 0
        elif button_value == 1670:
            mascon = 4
            brake = 0
        elif button_value == 18048:
            mascon = 5
            brake = 0
        else:
            mascon = None
            brake = None
        
        return {'mascon': mascon, 'brake': brake, 'way': way}

        
if __name__ == '__main__':    
    import time
    pygame.init()
    pygame.joystick.init()
    
    joy = pygame.joystick.Joystick(0)
    joy.init()
    
    while True:
        pygame.event.get()
        buttons = [0] * PS1Dengo.BUTTON_NUM
        for i in range(PS1Dengo.BUTTON_NUM):
            buttons[i] = joy.get_button(i)
        ax = joy.get_axis(0)

        if ax < 0:
            buttons += [1, 1]
        elif ax == 0.0:
            buttons += [0,0]
        else: # ax > 0
            buttons += [0, 1]
            
        result = PS1Dengo.arrangeJoyData(buttons)
        
        time.sleep(0.1)
