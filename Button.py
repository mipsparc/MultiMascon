#coding: utf-8

from DB import DB
from Command import Command
import time
import logging

# 各マスコンのボタンを統一的に扱う
class Button:
    ASSIGN_TYPE_FUNC_ALTERNATE = 2
    ASSIGN_TYPE_ACCESSORY_ALTERNATE = 4
    
    ASSIGN_TYPES = {
        ASSIGN_TYPE_FUNC_ALTERNATE: 'ファンクション',
        ASSIGN_TYPE_ACCESSORY_ALTERNATE: 'アクセサリ',
    }
    
    OHC_PC01A_WHITE = 11
    OHC_PC01A_YELLOW = 12
    
    TYPE2_UP = 21
    #TYPE2_DOWN = 22
    TYPE2_SELECT = 23
    TYPE2_START = 24
    TYPE2_A = 25
    TYPE2_B = 26
    TYPE2_C = 27
    TYPE2_D = 28
    TYPE2_HONE = 29
    
    RYOJOU_UP = 41
    #RYOJOU_DOWN = 42
    RYOJOU_SELECT = 43
    RYOJOU_START = 44
    RYOJOU_SHITEN = 45
    RYOJOU_ANNOUNCE = 46
    RYOJOU_HORN = 47
    RYOJOU_DOOR_R = 48
    RYOJOU_DOOR_L = 49
    
    #PS1_DENGO_SELECT = 61
    PS1_DENGO_START = 62
    
    SW_A = 72
    SW_B = 73
    SW_X = 74
    SW_Y = 75
    SW_HOME = 76
    SW_CIRCLE = 77
    SW_L = 78
    SW_ZL = 79
    SW_R = 80
    SW_ZR = 81
    SW_PLUS = 82
    SW_MINUS = 83
    
    BUTTONS = {
        'title_sanin': '-----サンインマスコン-----',
        OHC_PC01A_WHITE: 'サンインワンハン 白',
        OHC_PC01A_YELLOW: 'サンインワンハン 黄',
        'title_type2': '-----電車でGO Type2-----',
        TYPE2_UP: '電GO Type2ツーハン 上',
        TYPE2_SELECT: '電GO Type2ツーハン SELECT',
        TYPE2_START: '電GO Type2ツーハン START',
        TYPE2_A: '電GO Type2ツーハン A',
        TYPE2_B: '電GO Type2ツーハン B',
        TYPE2_C: '電GO Type2ツーハン C',
        TYPE2_D: '電GO Type2ツーハン D',
        TYPE2_HONE: '電GO Type2ツーハン 警笛',
        'title_ryojo': '-----電車でGO 旅情編-----',
        RYOJOU_UP: '電GO 旅情編ツーハン 上',
        RYOJOU_SELECT: '電GO 旅情編ツーハン SELECT',
        RYOJOU_START: '電GO 旅情編ツーハン START',
        RYOJOU_SHITEN: '電GO 旅情編ツーハン 視点',
        RYOJOU_ANNOUNCE: '電GO 旅情編ツーハン アナウンス',
        RYOJOU_HORN: '電GO 旅情編ツーハン ホーンボタン',
        RYOJOU_DOOR_L: '電GO 旅情編ツーハン 左扉',
        RYOJOU_DOOR_R: '電GO 旅情編ツーハン 右扉',
        'title_ps1_dengo': '-----電車でGO PS1ワンハン・ツーハン-----',
        #PS1_DENGO_SELECT: '電車でGO PS1 SELECT',
        PS1_DENGO_START: '電車でGO PS1 START',
        'title_sw_dengo': '-----電車でGO!! Switchワンハン-----',
        SW_A: '電GO!! Switchワンハン A',
        SW_B: '電GO!! Switchワンハン B',
        SW_X: '電GO!! Switchワンハン X',
        SW_Y: '電GO!! Switchワンハン Y',
        SW_HOME: '電GO!! Switchワンハン ホーム',
        SW_CIRCLE: '電GO!! Switchワンハン ○',
        SW_L: '電GO!! Switchワンハン L',
        SW_ZL: '電GO!! Switchワンハン ZL',
        SW_R: '電GO!! Switchワンハン R',
        SW_ZR: '電GO!! Switchワンハン ZR',
        SW_PLUS: '電GO!! Switchワンハン +',
        SW_MINUS: '電GO!! Switchワンハン -',
    }
    
    # DBから取得したボタンプロファイル
    profile = {}
    # 前回押してあったボタン
    last_buttons = {}
    # 前回のボタン状態(1/0)
    last_state = {}
    # 今回押してあるボタン
    next_pressed_buttons = {}
    
    def getProfile(self):
        self.profile = DB.getButtons()
        
    # 前回も押してあったか判定
    def isStillPressed(self, addr, button_id, mode):
        if f"{mode}-{addr}-{button_id}" in self.last_buttons:
            return True
        
        return False
    
    # 次の出力ステート(1/0)を出す。変化なしの場合はFalse
    def buttonPressed(self, addr, button_id, mode):
        if self.isStillPressed(addr, button_id, mode):
            return False
        
        if f"{mode}-{addr}-{button_id}" in self.last_state:
            last_state = self.last_state[f"{mode}-{addr}-{button_id}"]
        else:
            # 新規のボタンのとき
            self.last_state[f"{mode}-{addr}-{button_id}"] = 0
        
        self.last_state[f"{mode}-{addr}-{button_id}"] = int(not self.last_state[f"{mode}-{addr}-{button_id}"])
        
        return self.last_state[f"{mode}-{addr}-{button_id}"]

    def processButtons(self, buttons_responses, command_queue):
        self.last_buttons = self.next_pressed_buttons
        self.next_pressed_buttons = {}
        
        for buttons_resp in buttons_responses:
            if buttons_resp == {}:
                continue
            addr = buttons_resp['addr']
            loco_id = buttons_resp['loco_id']
            buttons = buttons_resp['buttons']
            for button_id in buttons:
                try:
                    ps = self.profile[loco_id][button_id]
                    assign_type = ps['assign_type']
                    send_key = ps['send_key']
                except KeyError:
                    continue
                
                if assign_type == self.ASSIGN_TYPE_FUNC_ALTERNATE:
                    mode = 'button_func'
                    send_value = self.buttonPressed(addr, button_id, mode)
                    if send_value != False:
                        Command.setLocoFunction(command_queue, addr, send_key, send_value)
                
                elif assign_type == self.ASSIGN_TYPE_ACCESSORY_ALTERNATE:
                    mode = 'button_accessory'
                    send_value = self.buttonPressed(addr, button_id, mode)
                    if send_value != False:
                        Command.setTurnout(command_queue, send_key, send_value)
            
                self.next_pressed_buttons[f"{mode}-{addr}-{button_id}"] = True

    def processPressedKeys(self, pressed_keys, command_queue):
        new_last_buttons = []
        
        for pressed_key in pressed_keys:
            if pressed_key['type'] == 'func':
                mode = 'keyboard_func'
                if self.isStillExistFromLastTime(pressed_key['loco_addr'], pressed_key['func_id'], mode):
                    continue
                send_value = self.buttonPressed(pressed_key['loco_addr'], pressed_key['func_id'], mode)
                if send_value != False:
                    Command.setLocoFunction(command_queue, pressed_key['loco_addr'], pressed_key['func_id'], send_value)
            elif pressed_key['type'] == 'accessory':
                mode = 'keyboard_accessory'
                # button_idはないので0をおく
                send_value = self.buttonPressed(pressed_key['accessory_id'], 0, mode)
                if send_value != False:
                    Command.setTurnout(command_queue, pressed_key['accessory_id'], send_value)
            else:
                raise KeyError
            
        
        

    
