#coding: utf-8

# サンイン重工 OHC-PC01AコントローラからPythonへ繋ぎこむライブラリ

import pygame
import time
from Mascon import Mascon
import logging
import importlib

class OHC_PC01A(Mascon):
    def __init__(self, loco_id, joystick_num):
        # 切断により無効状態か
        self.invalid = False

        pygame.init()
        pygame.joystick.init()
        wait_start_time = time.time()
        while pygame.joystick.get_count() < 1:
            if (time.time() - wait_start_time) > 2.0:
                logging.error(f'ジョイスティックの再接続にはソフトリセットが必要です')
                self.invalid = True
                break
            time.sleep(0.05)
        
        if type(joystick_num) != type(0):
            logging.error(f'OHC_PC01Aにジョイスティック番号が正常に渡されませんでした {joystick_num}')
            self.invalid = True
        
        if self.invalid == True:
            return
            
        self.joy = pygame.joystick.Joystick(joystick_num)
        self.joy.init()
        pygame.event.get()
        
        self.loco_id = loco_id
        
    # 主幹制御器状態から力行ノッチ・ブレーキノッチ指令に変換する
    def convertPosToAccelBrake(self, pos):
        if pos == [1, 0, 0, 1]:
            # [力行ノッチ, ブレーキノッチ]
            return [0, 1]
        if pos == [1, 0, 0, 0]:
            return [0, 2]
        if pos == [0, 1, 1, 1]:
            return [0, 3]
        if pos == [0, 1, 1, 0]:
            return [0, 4]
        if pos == [0, 1, 0, 1]:
            return [0, 5]
        if pos == [0, 1, 0, 0]:
            return [0, 6]
        if pos == [0, 0, 1, 1]:
            return [0, 7]
        if pos == [0, 0, 1, 0]:
            return [0, 8]
        if pos == [0, 0, 0, 1]:
            return [0, 9]
        
        if pos == [1, 0, 1, 1]:
            return [1, 0]
        if pos == [1, 1, 0, 0]:
            return [2, 0]
        if pos == [1, 1, 0, 1]:
            return [3, 0]
        if pos == [1, 1, 1, 0]:
            return [4, 0]
        if pos == [1, 1, 1, 1]:
            return [5, 0]

        return [0,0]

    # 主幹制御器全体の状態を返す
    def loadStatus(self):
        try:
            self.joy
        except:
            self.invalid = True
        
        pygame.event.get()
        
        accel_knotch, brake_knotch = self.convertPosToAccelBrake([
            self.joy.get_button(6),
            self.joy.get_button(7),
            self.joy.get_button(8),
            self.joy.get_button(9)
        ])
                
        ax = self.joy.get_axis(1)
        if ax < 0:
            way = 2
        elif ax == 0.0:
            way = 0
            accel_knotch = 0
            brake_knotch = 0
        elif ax > 0:
            way = 1

        self.accel_knotch = accel_knotch
        self.brake_knotch = brake_knotch
        self.way = way
        self.white = bool(self.joy.get_button(1))
        self.yellow =  bool(self.joy.get_button(2))
        self.zero = bool(self.joy.get_button(0))
        self.three = bool(self.joy.get_button(3))
        self.four = bool(self.joy.get_button(4))
        self.five = bool(self.joy.get_button(5))

if __name__ == '__main__':
    m = OHC_PC01A()
    while True:
        m.loadStatus()
        print('accel', m.accel_knotch)
        print('brake', m.brake_knotch)
        print('way', m.way)
        print('black', m.black)
        print('white', m.white)
        print('yellow', m.yellow)
        time.sleep(0.5)
