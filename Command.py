#coding:utf-8

import time

class Command:
    # 49152を車両アドレスに足したものをDSAir2に送信する
    LOCO_DEFAULT_ADDR = 49152
    
    @classmethod
    def setLocoFunction(self, command_queue, loco_addr, func_num, value):
        command_queue.put(f'setLocoFunction({loco_addr + self.LOCO_DEFAULT_ADDR},{func_num},{value})')
        
    @classmethod
    def setLocoSpeed(self, command_queue, loco_addr, speed):
        if speed > 0:
            out_speed = int(speed)
        else:
            out_speed = 0
        
        command_queue.put(f'setLocoSpeed({loco_addr + self.LOCO_DEFAULT_ADDR},{out_speed},2)')
                
    @classmethod
    def setLocoDirection(self, command_queue, loco_addr, way):
        if way in (1, 2):
            command_queue.put(f'setLocoDirection({loco_addr + self.LOCO_DEFAULT_ADDR},{way})')
    
    @classmethod
    def switchToDc(self, command_queue):
        command_queue.put('setPower(0)')
        time.sleep(0.3)        
        command_queue.put('setPower(0)')
        time.sleep(0.3)
        command_queue.put('setPower(0)')
        time.sleep(0.3)
        
    @classmethod
    def switchToDCC(self, command_queue):
        command_queue.put('setPower(1)')
        time.sleep(0.3)        
        command_queue.put('setPower(1)')
        time.sleep(0.3)
        command_queue.put('setPower(1)')
        time.sleep(0.3)
        
    @classmethod
    def reset(self, command_queue):
        command_queue.put('reset()')
    
    # DC駆動用
    #@classmethod
    #def move_dc(self, speed_level, way):
        #if speed_level > 0 and way != 0:
            #out_speed = int(speed_level)
        #else:
            ## 仮想的な方向 0(切)
            #out_speed = 0
        
        #if out_speed > self.MAX_SPEED:
            #out_speed = self.MAX_SPEED
        #if out_speed < 0:
            #out_speed = 0
        
        #if way != self.last_way:
            #self.last_way = way
            
        #if out_speed != self.last_out_speed:
            #self.last_out_speed = out_speed
            #self.send(f'DC({out_speed},{way})\n')
