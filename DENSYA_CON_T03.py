#coding: utf-8

# タイトー 電車でGO! 旅情編コントローラー PS2 (USB接続) からPythonに繋ぎこむライブラリ

import usb.core
from Mascon import Mascon
from Button import Button
import logging
import time

class DENSYA_CON_T03(Mascon):
    BRAKE_TYPE = Mascon.BRAKE_TYPE_BP

    brake_knotch = 0
    accel_knotch = 0
    KNOTCHES = {0: 0, 60: 1, 120: 2, 180: 3, 240: 4}
    way = 0
    BC = 0
    # 重なり
    brake_pos = 0
    ACCEL_KNOTCH_NUM = 4
    
    def __init__(self, loco_id, bus, address):
        devices = usb.core.find(find_all=True, idVendor=0x0ae4, idProduct=0x0007)
        for device in devices:
            if device.bus == bus and device.address == address:
                self.device = device
                self.loco_id = loco_id
                break

        # 正しくアサインされたかの検査
        self.device
        
        # 切断などで無効状態か
        self.invalid = False
        
        self.device.reset()
        time.sleep(0.1)
        self.device.reset()

    def loadStatus(self):
        try:
            self.device
        except:
            self.invalid = True
            return
        
        self.buttons = []
        
        # 3回試行する
        for i in range(3):
            try:
                # 129: 固定されたエンドポイント
                [BRAKE, KNOTCH, _01, HT, BT, _02, _03, _04] = self.device.read(129, 8, 100)
                
                # ブレーキ位置 -0.5(ユルメ)~0(重なり)~+0.5(ブレーキ)
                self.brake_pos = max((BRAKE - 40) / 180, 0) - 0.5
                # 重なり
                if -0.15 < self.brake_pos < 0.03:
                    self.brake_pos = 0

                if KNOTCH != 0xFF:
                    self.accel_knotch = self.KNOTCHES[KNOTCH]
                
                # 左
                if HT == 6:
                    self.way = 1
                # 右
                elif HT == 2:
                    self.way = 2
                
                # 上
                elif HT == 0:
                    self.buttons.append(Button.RYOJOU_UP)
                # 下 (切)
                elif HT == 4:
                    self.way = 0
                    # self.buttons.append(Button.RYOJOU_DOWN)
                
                if BT == 4:
                    self.buttons.append(Button.RYOJOU_SHITEN)
                elif BT == 2:
                    self.buttons.append(Button.RYOJOU_ANNOUNCE)
                elif BT == 1:
                    self.buttons.append(Button.RYOJOU_HORN)
                elif BT == 8:
                    self.buttons.append(Button.RYOJOU_DOOR_R)
                elif BT == 16:
                    self.buttons.append(Button.RYOJOU_DOOR_L)
                elif BT == 32:
                    self.buttons.append(Button.RYOJOU_SELECT)
                elif BT == 64:
                    self.buttons.append(Button.RYOJOU_START)

            except KeyError:
                pass
            
            except usb.core.USBTimeoutError:
                pass

            except usb.core.USBError:
                logging.warning('USB接続失敗', exc_info=True)
                self.invalid = True
                                
            finally:
                self.buttons = list(set(self.buttons))

