#coding: utf-8

# サンイン重工 OHC-PC01AコントローラからPythonへ繋ぎこむライブラリ

import pygame
from Joystick import Joystick
from Button import Button
import logging

class OHC_PC01A(Joystick):
    BRAKE_TYPE = Joystick.BRAKE_TYPE_KNOTCH

    ACCEL_KNOTCH_NUM = 5
    BRAKE_KNOTCH_NUM = 9
        
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
        self.buttons = []
        if bool(self.joy.get_button(1)):
            self.buttons.append(Button.OHC_PC01A_WHITE)
        if bool(self.joy.get_button(2)):
            self.buttons.append(Button.OHC_PC01A_YELLOW)
            
        #TODO blackは一旦放置

