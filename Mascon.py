#coding: utf-8

import Smooth
from Command import Command

class Mascon:
    kph = 0
    last_speed_level = 0
    last_way = 0
    # DBから情報取得済みかどうか
    fetched = False
    
    def fetchDatabase(self):
        # TODO: SQLiteから取得する
        # demo
        self.fetched = True
        self.ADDR = 4
        # demo 速度(kph)・出力値
        self.SPEED_OUTPUT_PROFILE = [
            [0.0, 0],
            [5.0, 30],
            [15.0, 100],
            [20.0, 200],
            [30.0, 300],
            [40.0, 400],
            [50.0, 500],
            [60.0, 600],
            [90.0, 900],
            [91.0, 901],
            [999.9, None], #dummy
        ]
        # demo 動き出す出力値(下駄を履かせる)
        self.BASE_LEVEL = 85
        # demo ライトファンクション番号
        self.LIGHT_FUNC_NUM = 0

    def advanceTime(self, command_queue):
        if not self.fetched:
            return
        
        self.loadStatus()
        
        way = self.way
        
        if self.last_way != way:
            Command.setLocoDirection(command_queue, self.ADDR, way)
            if way == 0:
                Command.setLocoFunction(command_queue, self.ADDR, self.LIGHT_FUNC_NUM, 0)
            else:
                Command.setLocoFunction(command_queue, self.ADDR, self.LIGHT_FUNC_NUM, 1)
            self.last_way = way
        
        speed_level = self.getSpeedLevel()
        if self.last_speed_level != speed_level:
            Command.setLocoSpeed(command_queue, self.ADDR, speed_level)
            self.last_speed_level = speed_level
            
        # TODO 変化のあったボタンを取得して、ファンクションを動作させたりする
       
    def getSpeedLevel(self):
        # TODO この部分も管理画面から弄れるようにする
        if self.kph < 30.0:
            accel_level = self.accel_knotch * 0.3
        elif self.kph < 50.0:
            accel_level = self.accel_knotch * 0.2
        else:
            accel_level = self.accel_knotch * 0.1
        
        brake_level = self.brake_knotch * 0.5
        self.kph = self.kph + accel_level - brake_level

        # 走行抵抗
        self.kph -= 0.05
        
        if self.kph < 0:
            self.kph = 0
        speed_level = Smooth.getValue(self.kph, self.SPEED_OUTPUT_PROFILE)
        
        if speed_level > 0:
            level = speed_level + self.BASE_LEVEL
            return level
        
        return 0
