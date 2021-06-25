#coding:utf-8

class Command:
    MAX_SPEED = 800
    
    # 3 はデフォルトアドレス
    LOCO_DEFAULT_ADDR = 49152
    
    last_loco_light = False
    
    def __init__(self, dsair, loco_addr):
        self.dsair = dsair
        self.loco_addr = loco_addr
        
    def turnOnLight(self):
        if not self.last_loco_light:
            self.last_loco_light = True
            self.send(f'setLocoFunction({self.loco_addr},{self.LIGHT_FUNC_NUM},1)')
        
    def turnOffLight(self):
        if self.last_loco_light:
            self.last_loco_light = False
            self.send(f'setLocoFunction({self.loco_addr},{self.LIGHT_FUNC_NUM},0)')
        
    # 速度や方向などの状態が変わるときのみ命令を出力する
    def move_dcc(self, speed_level, way):
        if self.last_way != way and way == 0:
            self.turnOffLight()
        elif self.last_way != way:
            self.turnOnLight()
        
        if speed_level > 0 and way != 0:
            out_speed = int(speed_level)
        else:
            # 仮想的な方向 0(切)
            out_speed = 0
        
        if out_speed > self.MAX_SPEED:
            out_speed = self.MAX_SPEED
        if out_speed < 0:
            out_speed = 0
        
        if out_speed != self.last_out_speed:
            self.last_out_speed = out_speed
            self.send(f'setLocoSpeed({self.loco_addr},{out_speed},2)')
        
        if way != self.last_way:
            self.last_way = way
            # 仮想的な方向 0(切) は送信しない
            if way != 0:
                self.send(f'setLocoDirection({self.loco_addr},{way})')
    
    # DC駆動用
    def move_dc(self, speed_level, way):
        if speed_level > 0 and way != 0:
            out_speed = int(speed_level)
        else:
            # 仮想的な方向 0(切)
            out_speed = 0
        
        if out_speed > self.MAX_SPEED:
            out_speed = self.MAX_SPEED
        if out_speed < 0:
            out_speed = 0
        
        if way != self.last_way:
            self.last_way = way
            
        if out_speed != self.last_out_speed:
            self.last_out_speed = out_speed
            self.send(f'DC({out_speed},{way})\n')
            
    def switchToDc(self):
        self.send('setPower(0)')
        time.sleep(0.3)
        self.send('setPower(0)')
        time.sleep(0.3)
        self.send('setPower(0)')
        time.sleep(0.3)
        self.ser.reset_input_buffer()
        
    def switchToDCC(self):
        self.loco_addr = self.LOCO_DEFAULT_ADDR + addr
        self.last_loco_light = False
        # DCC初期化
        self.send('setPower(1)')
        time.sleep(0.5)
        poweron_response = self.ser.read(50)
        print(poweron_response)
        self.ser.reset_input_buffer()
        
        self.send('setPower(1)')
        time.sleep(0.5)
        poweron_response = self.ser.read(50)
        print(poweron_response)
        self.ser.reset_input_buffer()
    
    # 最終的にコマンドを送信する関数
    def send(self, value):
        DSAir2.send(value)
