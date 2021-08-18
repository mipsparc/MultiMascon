#coding: utf-8

import Smooth
from Command import Command
from DB import DB
import time
import logging

class Mascon:
    # ノッチ式
    BRAKE_TYPE_KNOTCH = 1
    # 自動空気ブレーキ(緩め↔ブレーキ)
    BRAKE_TYPE_BP = 2
    
    kph = 0
    last_speed_level = 0
    last_way = 0
    # DBから初回情報取得済みかどうか
    fetched = False
    
    accel_knotch = 0
    brake_knotch = 0
    way = 0
    buttons = []
    
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
            return {}
        if not self.fetched:
            return {}
        
        self.loadStatus()
                
        # 方向転換
        if self.last_way != self.way:
            Command.setLocoFunction(command_queue, self.ADDR, self.LIGHT_FUNC_ID, 1)
            Command.setLocoFunction(command_queue, self.ADDR, self.LIGHT_FUNC_ID, 0)
            Command.setLocoDirection(command_queue, self.ADDR, self.way)
            if self.way == 0:
                Command.setLocoFunction(command_queue, self.ADDR, self.LIGHT_FUNC_ID, 0)
            else:
                Command.setLocoFunction(command_queue, self.ADDR, self.LIGHT_FUNC_ID, 1)
            self.last_way = self.way
        
        speed_level = self.getSpeedLevel()
        if self.way == 0:
            self.kph = 0
            speed_level = 0
        
        if self.last_speed_level != speed_level:
            Command.setLocoSpeed(command_queue, self.ADDR, speed_level)
            self.last_speed_level = speed_level
            print(f'loco_id: {self.loco_id}, kph: {max(self.kph - 1, 0)}')
            
        return {'addr':self.ADDR, 'loco_id':self.loco_id, 'buttons':self.buttons}

    def getSpeedLevel(self):
        if self.invalid:
            return 0
        
        accel_level = Smooth.getValue(self.kph, self.SPEED_ACCEL_PROFILE) * self.accel_knotch / self.ACCEL_KNOTCH_NUM
        
        if self.BRAKE_TYPE == self.BRAKE_TYPE_KNOTCH:
            brake_level = (self.brake_knotch / self.BRAKE_KNOTCH_NUM) * self.BRAKE_RATIO
        elif self.BRAKE_TYPE == self.BRAKE_TYPE_BP:
            # 大きくなりすぎないように
            if self.BC < 5.0:
                self.BC += self.brake_pos
            if self.BC < 0:
                self.BC = 0
            brake_level = self.BC * 0.5 * self.BRAKE_RATIO
        else:
            raise ValueError('不正なブレーキ種別です')
            
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
