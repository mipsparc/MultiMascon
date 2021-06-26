#coding: utf-8

import Smooth

class Mascon:
    kph = 0
    
    def fetchDatabase(self):
        # TODO: SQLiteから取得する
        # demo
        self.ADDR = 3
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
            [91.0, 900],
            [999.9, None], #dummy
        ]
        # demo 動き出す出力値(下駄を履かせる)
        self.BASE_LEVEL = 85

    def advanceTime(self):
        self.loadStatus()
        output = self.getOutput()
        
    def getOutput(self):
        # TODO この部分も管理画面から弄れるようにする
        if self.kph < 30.0:
            accel_level = self.accel_knotch * 0.3
        elif self.kph < 50.0:
            accel_level = self.accel_knotch * 0.2
        else:
            accel_level = self.accel_knotch * 0.1
        
        brake_level = self.brake_knotch * 1.0
        self.kph = self.kph + self.accel_level - brake_level

        # 走行抵抗
        self.kph -= 0.05
        
        speed_level = Smooth.getValue(kph, self.SPEED_OUTPUT_PROFILE)
        
        if speed_level > 0:
            level = speed_level + BASE_LEVEL
            return level
        
        return 0
