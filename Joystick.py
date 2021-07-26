#coding: utf-8

import pygame
import time
from Mascon import Mascon
from Button import Button
import logging

class Joystick(Mascon):
    def __init__(self, loco_id, joystick_num):
        # 切断により無効状態か
        self.invalid = False

        pygame.init()
        pygame.joystick.init()
        wait_start_time = time.time()
        while pygame.joystick.get_count() < 1:
            if (time.time() - wait_start_time) > 2.0:
                logging.error(f'ジョイスティックの再接続にはソフト再起動が必要です')
                self.invalid = True
                break
            time.sleep(0.05)
        
        if type(joystick_num) != type(0):
            logging.error(f'ジョイスティック番号が正常に渡されませんでした {joystick_num}')
            self.invalid = True
        
        if self.invalid == True:
            return
            
        self.joy = pygame.joystick.Joystick(joystick_num)
        self.joy.init()
        pygame.event.get()
        
        self.loco_id = loco_id
