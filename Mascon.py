#coding: utf-8

import Smooth
from Command import Command
from DB import DB
import time
import logging

class Mascon:
    kph = 0
    last_speed_level = 0
    last_way = 0
    # DBから初回情報取得済みかどうか
    fetched = False
    
    def fetchDatabase(self):
        if self.invalid == True:
            return
        
        loco = DB.getLocoById(self.loco_id)
        # 存在しない車両番号の場合
        if loco == None:
            return
        self.ADDR = loco['address']
        accel_curve_group_id = loco['accel_curve_group_id']
        speed_curve_group_id = loco['speed_curve_group_id']
        self.BASE_LEVEL = loco['base_level']
        self.LIGHT_FUNC_ID = loco['light_func_id']
        self.BRAKE_RATIO = loco['brake_ratio']
        
        self.SPEED_OUTPUT_PROFILE = DB.getSpeedOutputCurveById(speed_curve_group_id)
        self.SPEED_ACCEL_PROFILE = DB.getSpeedAccelCurveById(accel_curve_group_id)
        
        self.fetched = True

    def advanceTime(self, command_queue):
        if self.invalid:
            self.stop(command_queue)
        if not self.fetched:
            return
        
        self.loadStatus()
        
        way = self.way
        
        # 方向転換
        if self.last_way != way:
            Command.setLocoFunction(command_queue, self.ADDR, self.LIGHT_FUNC_ID, 1)
            Command.setLocoFunction(command_queue, self.ADDR, self.LIGHT_FUNC_ID, 0)
            Command.setLocoDirection(command_queue, self.ADDR, way)
            if way == 0:
                Command.setLocoFunction(command_queue, self.ADDR, self.LIGHT_FUNC_ID, 0)
            else:
                Command.setLocoFunction(command_queue, self.ADDR, self.LIGHT_FUNC_ID, 1)
            self.last_way = way
        
        speed_level = self.getSpeedLevel()
        if self.last_speed_level != speed_level:
            Command.setLocoSpeed(command_queue, self.ADDR, speed_level)
            self.last_speed_level = speed_level
            print(f'loco_id: {self.loco_id}, kph: {max(self.kph - 1, 0)}')
            
        return {'loco':self.loco_id, 'buttons':self.buttons}

    def getSpeedLevel(self):
        if self.invalid:
            return 0
        
        accel_level = Smooth.getValue(self.kph, self.SPEED_ACCEL_PROFILE) * self.accel_knotch / self.ACCEL_KNOTCH_NUM
        
        brake_level = (self.brake_knotch / self.BRAKE_KNOTCH_NUM) * self.BRAKE_RATIO
        self.kph = max(0, self.kph + accel_level - brake_level)

        if brake_level == 0 and self.accel_knotch > 0 and self.kph < 1:
            self.kph = 1
        
        speed_level = Smooth.getValue(self.kph, self.SPEED_OUTPUT_PROFILE)
        
        if speed_level > 0:
            level = speed_level + self.BASE_LEVEL
            return level
                        
        return 0
    
    def stop(self, command_queue):
        try:
            self.kph = 0
            Command.setLocoSpeed(command_queue, self.ADDR, 0)
        except AttributeError:
            pass
