#coding: utf-8

class Mascon:
    speed_level = 0
    last_speed_level = 0
    
    def applyDatabase(self):
        # TODO: SQLiteから取得する
        # demo
        self.addr = 3
        self.speed_profile = [
            [0.0, 0],
            [5.0, 30],
            [15.0, 100],
            [20.0, 200],
            [30.0, 300],
            [40.0, 400],
            [50.0, 500],
            [60.0, 600],
            [90.0, 900],
            [180.0, 900],
            [999.9, None], #dummy
        ]
