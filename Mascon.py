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
    
    #turnout_state = 0
    #last_turnout_rerun = time.time()
    
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
            
        # TODO 変化のあったボタンを取得して、ファンクションを動作させたりする
        #try:
            #if self.white:
                #self.turnout_state = 0
                #Command.setTurnout(command_queue, 1, self.turnout_state)
            #elif self.yellow:
                #self.turnout_state = 1
                #Command.setTurnout(command_queue, 1, self.turnout_state)
                
            ## 定期的にポイントマシンを再駆動してガタを解決する
            #if (time.time() - self.last_turnout_rerun) > 3.0:
                ## デモ用番号
                #Command.setTurnout(command_queue, 1, self.turnout_state)
                #self.last_turnout_rerun = time.time()
        #except AttributeError:
            #pass

    def getSpeedLevel(self):
        if self.invalid:
            return 0
        
        accel_level = Smooth.getValue(self.kph, self.SPEED_ACCEL_PROFILE)
        
        brake_level = (self.brake_knotch / self.BRAKE_KNOTCH_NUM) * 0.5
        self.kph = max(0, self.kph + (self.kph * (accel_level / self.ACCEL_KNOTCH_NUM) * self.accel_knotch) - brake_level)

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
