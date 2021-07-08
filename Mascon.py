#coding: utf-8

import Smooth
from Command import Command
from DB import DB

class Mascon:
    kph = 0
    last_speed_level = 0
    last_way = 0
    # DBから初回情報取得済みかどうか
    fetched = False
    
    def fetchDatabase(self):
        #TODO どうにかする
        loco_id = 1
        
        loco = DB.getLocoById(loco_id)
        self.ADDR = loco['address']
        accel_curve_group_id = loco['accel_curve_group_id']
        speed_curve_group_id = loco['speed_curve_group_id']
        self.BASE_LEVEL = loco['base_level']
        self.LIGHT_FUNC_ID = loco['light_func_id']
        
        self.SPEED_OUTPUT_PROFILE = DB.getSpeedOutputCurveById(speed_curve_group_id)
        self.SPEED_ACCEL_PROFILE = DB.getSpeedAccelCurveById(accel_curve_group_id)
        
        self.fetched = True

    def advanceTime(self, command_queue):
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
            print(speed_level)
            
        # TODO 変化のあったボタンを取得して、ファンクションを動作させたりする
       
    def getSpeedLevel(self):
        accel_level = Smooth.getValue(self.kph, self.SPEED_ACCEL_PROFILE)
        print(f'accel: {accel_level}')
        
        brake_level = self.brake_knotch * 0.5
        self.kph = max(0, self.kph + (self.kph * (accel_level / 5.0) * self.accel_knotch) - brake_level)
        if brake_level == 0 and self.accel_knotch > 0 and self.kph < 1:
            self.kph = 1
        
        print(f'kph: {self.kph}')
        speed_level = Smooth.getValue(self.kph, self.SPEED_OUTPUT_PROFILE)
        
        if speed_level > 0:
            level = speed_level + self.BASE_LEVEL
            return level
        
        return 0
