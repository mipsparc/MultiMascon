#coding: utf-8

# タイトー 電車でGO! コントローラType2 PS2 (USB接続) からPythonに繋ぎこむライブラリ

import usb.core
import usb.util
from Mascon import Mascon

class DENSYA_CON_T01(Mascon):
    CONNECT = 'usb'
    NAME = 'DENSYA_CON_T01'
    
    brake_level = 0
    BR_LEVEL = {0x79: 0, 0x8A: 1, 0x94: 2, 0x9A: 3, 0xA2: 4, 0xA8: 5, 0xAF: 6, 0xB2: 7, 0xB5: 8, 0xB9: 9}
    mascon_level = 0
    MC_LEVEL = {0x81: 0, 0x6D: 1, 0x54: 2, 0x3F: 3, 0x21: 4, 0x00: 5}

    def listDevices(self):
        devices = usb.core.find(find_all=True, idVendor=0x0ae4, idProduct=0x0004)
        for device in devices:
            print(device.serial_number)
            
    def setDevice(self, serial_number):
        devices = usb.core.find(find_all=True, idVendor=0x0ae4, idProduct=0x0004)
        for device in devices:
            if device.serial_number == serial_number:
                self.device = device
                
    def read(self):
        # 3回試行する
        for i in range(3):
            try:
                # 129: 固定されたエンドポイント
                [_01, BR, MC, PD, HT, BT] = self.device.read(129, 10, 10)
                if BR != 0xFF:
                    self.brake_level = self.BR_LEVEL[BR]
                if MC != 0xFF:
                    self.mascon_level = self.MC_LEVEL[MC]
                self.pedal = PD == 0xFF
                
                # TODO: 十字キー、その他ボタンは後で実装
            
            except KeyError:
                pass
            
            except usb.core.USBTimeoutError:
                pass
            # TODO: 接続切れたら当該列車は停止して、全体はそのまま生きる
            except usb.core.USBError:
                raise
            
if __name__ == '__main__':
    controller = DENSYA_CON_T01()
    controller.listDevices()
    controller.setDevice('TCPP20010')
    controller.read()
    print(controller.mascon_level, controller.brake_level)
