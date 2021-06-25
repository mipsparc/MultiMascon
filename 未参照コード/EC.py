#coding: utf8

class EC:
    CARS = {
        'e655': {'desc': 'DCCの交直流特急型電車', 'type': 'dcc', 'addr': 4},
        'e233_dc': {'desc': 'アナログの直流通勤型電車', 'type': 'dc'},
        'de10': {'desc': 'DCCの液体式ディーゼル機関車', 'type': 'dcc', 'addr': 3},
    }
    
    def __init__(self, ectype):
        # 入力値の検証
        if ectype not in self.CARS:
            raise ValueError
        
        self.ectype = ectype
        self.data = self.CARS[ectype]
        self.dcc = self.CARS[ectype]['type'] == 'dcc'
        self.speed_level = 0
        self.last_speed_level = 0
        self.start = False
    
    def isDcc(self):
        return self.dcc
    
    def getCars(self):
        return self.CARS
    
    def getAddr(self):
        if self.dcc:
            return self.data['addr']
        else:
            return False
    
    def calcSpeed(self, accel_knotch, brake_knotch):
        if self.ectype == "e655":
            return self.e655(accel_knotch, brake_knotch)
        elif self.ectype == 'e233_dc':
            return self.e233_dc(accel_knotch, brake_knotch)
        elif self.ectype == 'de10':
            return self.de10(accel_knotch, brake_knotch)
        else:
            raise ValueError
    
    def e655(self, accel_knotch, brake_knotch): 
        BASE_LEVEL = 85
        INIT_LEVEL = 30

        if self.speed_level < 300:
            accel_level = accel_knotch * 0.3
        elif self.speed_level < 500:
            accel_level = accel_knotch * 0.2
        else:
            accel_level = accel_knotch * 0.05
        
        brake_level = brake_knotch * 1
        self.speed_level = self.speed_level + accel_level - brake_level
        
        self.speed_level -= 0.05
        
        if self.speed_level > 0:
            if self.start:
                self.speed_level += INIT_LEVEL
                self.start = False

            level = self.speed_level + BASE_LEVEL
            self.last_speed_level = level
            return level
        elif self.speed_level > 800:
            return 800
        
        self.speed_level = 0
        self.start = True
        return 0
    
    def e233_dc(self, accel_knotch, brake_knotch):
        BASE_LEVEL = 180
        INIT_LEVEL = 30

        if self.speed_level < 70:
            accel_level = accel_knotch * 0.5
        elif self.speed_level < 220:
            accel_level = accel_knotch * 0.3
        elif self.speed_level < 320:
            accel_level = accel_knotch * 0.2
        else:
            accel_level = accel_knotch * 0.05
        
        brake_level = brake_knotch * 0.4
        self.speed_level = self.speed_level + accel_level - brake_level
        
        self.speed_level -= 0.05
        
        if self.speed_level > 0:
            if self.start:
                self.speed_level += INIT_LEVEL
                self.start = False
            level = self.speed_level + BASE_LEVEL
            return level
        elif self.speed_level > 800:
            return 800
        
        self.speed_level = 0
        self.start = True
        return 0
