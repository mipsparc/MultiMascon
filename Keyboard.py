#coding: utf-8
import keyboard
from DB import DB
from collections import Counter
from Command import Command

class Keyboard:
    # 特殊な割当キーを定義する
    SCAN_CODES_SPECIAL = {
        41: 'accel',
        2: 'brake',
        3: 'left',
        4: 'off',
        5: 'right',
    }
    
    # 車両選択キーを定義する
    SCAN_CODES_LOCO = {
        6: '車両A',
        7: '車両B',
        8: '車両C',
        9: '車両D',
        10: '車両E',
        11: '車両F',
        12: '車両G',
        13: '車両H',
        124: '車両I',
        14: '車両J',
    }
    
    SCAN_CODES_NORMAL = {
        16: 'Q',
        17: 'W',
        18: 'E',
        19: 'R',
        20: 'T',
        21: 'Y',
        22: 'U',
        23: 'I',
        24: 'O',
        25: 'P',
        26: '@',
        27: '[',
        30: 'A',
        31: 'S',
        32: 'D',
        33: 'F',
        34: 'G',
        35: 'H',
        36: 'J',
        37: 'K',
        38: 'L',
        39: ';',
        40: ':',
        43: ']',
        44: 'Z',
        45: 'X',
        46: 'C',
        47: 'V',
        48: 'B',
        49: 'N',
        50: 'M',
        51: ',',
        52: '.',
        53: '/',
        89: '\\',
    }

    # 車両選択キーは一覧に入れない
    ASSIGN_TYPE_LOCO = 1
    # 例: assign_type=1, keycode=8, num=15(DCCアドレス)
    
    ASSIGN_TYPE_FUNC = 2
    ASSIGN_TYPE_ACCESSORY = 3
    
    profile = {}
    
    # キーボードで操作される車両
    selected_loco = False
    
    pressed_normal_keys = []
    pressed_special_keys = []
    
    # キーボード管理の車両
    locos = {}
    
    def getProfile(self):
        self.profile = DB.getKeyboards()
    
    def startScan(self):
        keyboard.on_press(self.keyPressed)
    
    # メインループにデータを渡す
    def getPressed(self):
        pressed_normal_keys = self.pressed_normal_keys
        self.pressed_normal_keys = []
        
        return pressed_normal_keys
    
    def runControl(self, button_responses, command_queue):
        # マスコンですでに使われているDCCアドレスでは走行指令をしない
        
        mascon_loco_addrs = []
        for button_response in button_responses:
            if button_response == {}:
                continue
            mascon_loco_addrs.append(button_response['addr'])
        
        pressed = self.pressed_special_keys
        self.pressed_special_keys = []
            
        if self.selected_loco in mascon_loco_addrs:
            if self.selected_loco in self.locos:
                del(self.locos[self.selected_loco])
                Command.setLocoSpeed(command_queue, self.selected_loco, 0)
            return
        
        if self.selected_loco not in self.locos:
            self.locos[self.selected_loco] = {'speed': 0, 'way': 0}
        
        grouped_pressed = Counter(pressed)
        
        if ('accel' in grouped_pressed) or ('brake' in grouped_pressed) or ('off' in grouped_pressed):
            if 'accel' in grouped_pressed:
                accels = grouped_pressed['accel']
                self.locos[self.selected_loco]['speed'] += accels
            if 'brake' in grouped_pressed:
                brakes = grouped_pressed['brake']
                self.locos[self.selected_loco]['speed'] = max(0, self.locos[self.selected_loco]['speed'] - brakes)
            if 'off' in grouped_pressed:
                self.locos[self.selected_loco]['speed'] = 0
            
            Command.setLocoSpeed(command_queue, self.selected_loco, self.locos[self.selected_loco]['speed'])

        
        if ('left' in grouped_pressed) or ('right' in grouped_pressed):
            if 'left' in grouped_pressed:
                self.locos[self.selected_loco]['way'] = 1
            if 'right' in grouped_pressed:
                self.locos[self.selected_loco]['way'] = 2

            Command.setLocoDirection(command_queue, self.selected_loco, self.locos[self.selected_loco]['way'])
        
        
    def keyPressed(self, event):
        scan_code = event.scan_code
        if scan_code in self.SCAN_CODES_SPECIAL:
            if self.SCAN_CODES_SPECIAL[scan_code] == 'accel':
                self.pressed_special_keys.append('accel')
                return
            elif self.SCAN_CODES_SPECIAL[scan_code] == 'brake':
                self.pressed_special_keys.append('brake')
                return
            elif self.SCAN_CODES_SPECIAL[scan_code] == 'left':
                self.pressed_special_keys.append('left')
                return
            elif self.SCAN_CODES_SPECIAL[scan_code] == 'off':
                self.pressed_special_keys.append('off')
                return
            elif self.SCAN_CODES_SPECIAL[scan_code] == 'right':
                self.pressed_special_keys.append('right')
                return

        elif scan_code in self.SCAN_CODES_LOCO:
            if not scan_code in self.profile:
                return
            else:
                data = self.profile[scan_code]
            
            loco_addr = data['num']
            self.selected_loco = loco_addr
            return

        elif scan_code in self.SCAN_CODES_NORMAL:
            if not scan_code in self.profile:
                return
            else:
                data = self.profile[scan_code]
            
            assign_type = data['assign_type']
            if assign_type == self.ASSIGN_TYPE_FUNC:
                func_id = data['num']
                if self.selected_loco == False:
                    return
                self.pressed_normal_keys.append({'type': 'func', 'loco_addr': self.selected_loco, 'func_id': func_id})
            elif assign_type == self.ASSIGN_TYPE_ACCESSORY:
                accessory_id = data['num']
                self.pressed_normal_keys.append({'type': 'accessory', 'accessory_id': accessory_id})

