#coding: utf-8

from DB import DB
from Command import Command
import time

# 各マスコンのボタンとアクションを統一的に扱うIDを管理する
class Button:
    ASSIGN_TYPE_FUNC_MOMENTARY = 1
    ASSIGN_TYPE_FUNC_ALTERNATE = 2

    ASSIGN_TYPE_ACCESSORY_MOMENTARY = 3
    ASSIGN_TYPE_ACCESSORY_ALTERNATE = 4
    
    ASSIGN_TYPES = {
        ASSIGN_TYPE_FUNC_MOMENTARY: '押してワンショットのアクションをするファンクション',
        ASSIGN_TYPE_FUNC_ALTERNATE: '押してON、もう一度押してOFFのアクションをするファンクション',
        ASSIGN_TYPE_ACCESSORY_MOMENTARY: '押してワンショットのアクションをするアクセサリ',
        ASSIGN_TYPE_ACCESSORY_ALTERNATE: '押してON、もう一度押してOFFのアクションをするアクセサリ', 
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
        'title_ps1_dengo': '-----電車でGO PS1ワンハン・ツーハン-----',
        #PS1_DENGO_SELECT: '電車でGO PS1 SELECT',
        PS1_DENGO_START: '電車でGO PS1 START',
    }
    
    last_buttons = {}
    new_last_buttons = {}
    last_state_for_alternate = {}
    profile = {}
    
    # DBから引くのはソフト起動時のみ
    def getProfile(self):
        self.profile = DB.getButtons()
        
    # 前回も押してあったもの
    def isStillExistFromLastTime(self, addr, button_id):
        if f"{addr}-{button_id}" in self.last_buttons:
            return True
        
        return False
    
    def getLastStateForAlternate(self, addr, button_id):
        if f"{addr}-{button_id}" in self.last_state_for_alternate:
            if self.last_state_for_alternate[f"{addr}-{button_id}"] + 0.3 > time.time():
                return 1
            else:
                del(self.last_state_for_alternate[f"{addr}-{button_id}"])
                return 0
        
        self.last_state_for_alternate[f"{addr}-{button_id}"] = time.time()
        return 1

    def processButtons(self, buttons_responses, command_queue):
        new_last_buttons = []
        
        for buttons_resp in buttons_responses:
            if type(buttons_resp) is not dict:
                continue
            addr = buttons_resp['addr']
            loco_id = buttons_resp['loco_id']
            buttons = buttons_resp['buttons']
            for button_id in buttons:
                try:
                    ps = self.profile[loco_id][button_id]
                    assign_type = ps['assign_type']
                    send_key = ps['send_key']
                    # Nullのときは空文字
                    send_value = ps['send_value']
                except KeyError:
                    continue
    
                if self.isStillExistFromLastTime(addr, button_id):
                    continue
                                
                if assign_type == self.ASSIGN_TYPE_FUNC_MOMENTARY:
                    if send_value == '':
                        continue
                    Command.setLocoFunction(command_queue, addr, send_key, send_value)
                    
                elif assign_type == self.ASSIGN_TYPE_FUNC_ALTERNATE:
                    send_value = self.getLastStateForAlternate(addr, button_id)
                    Command.setLocoFunction(command_queue, addr, send_key, send_value)

                elif assign_type == self.ASSIGN_TYPE_ACCESSORY_MOMENTARY:
                    if send_value == '':
                        continue
                    Command.setTurnout(command_queue, send_key, send_value)
                
                elif assign_type == self.ASSIGN_TYPE_ACCESSORY_ALTERNATE:
                    send_value = self.getLastStateForAlternate(addr, button_id)
                    Command.setTurnout(command_queue, send_key, send_value)
                
                new_last_buttons.append(f"{addr}-{button_id}")
                
        self.last_buttons = new_last_buttons
