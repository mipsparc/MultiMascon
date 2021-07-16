#coding: utf-8

# タイトー 電車でGO! コントローラType2 PS2 (USB接続) からPythonに繋ぎこむライブラリ

import usb.core
from Mascon import Mascon
import logging

class DENSYA_CON_T01(Mascon):
    
    brake_knotch = 0
    BR_LEVEL = {0x79: 0, 0x8A: 1, 0x94: 2, 0x9A: 3, 0xA2: 4, 0xA8: 5, 0xAF: 6, 0xB2: 7, 0xB5: 8, 0xB9: 9}
    accel_knotch = 0
    MC_LEVEL = {0x81: 0, 0x6D: 1, 0x54: 2, 0x3F: 3, 0x21: 4, 0x00: 5}
    way = 0
            
    def __init__(self, loco_id, bus, address):
        devices = usb.core.find(find_all=True, idVendor=0x0ae4, idProduct=0x0004)
        for device in devices:
            if device.bus == bus and device.address == address:
                self.device = device
                self.loco_id = loco_id
                break
        
        # 正しくアサインされたかの検査
        self.device
        
        # 切断などで無効状態か
        self.invalid = False
                
    def loadStatus(self):
        # デバイスがひきつづき存在するかどうか検証する
        try:
            self.device
        except:
            self.invalid = True
            return
        
        # 3回試行する
        for i in range(3):
            try:
                # 129: 固定されたエンドポイント
                [_01, BR, MC, PD, HT, BT] = self.device.read(129, 10, 10)
                if BR != 0xFF:
                    self.brake_knotch = self.BR_LEVEL[BR]
                if MC != 0xFF:
                    self.accel_knotch = self.MC_LEVEL[MC]
                self.pedal = PD == 0xFF
                
                # TODO: 後で再度実装、DBベースで
                # 左ボタンで前進
                if HT == 0x06:
                    self.way = 1
                # 右ボタンで後進
                elif HT == 0x02:
                    self.way = 2
                # 上下ボタンで切
                elif HT == 0x00 or HT == 0x04:
                    self.way = 0
            except KeyError:
                pass
            
            except usb.core.USBTimeoutError:
                pass

            except usb.core.USBError:
                self.invalid = True

if __name__ == '__main__':
    controller = DENSYA_CON_T01()
    controller.read()
    print(controller.mascon_level, controller.brake_level)
