#coding: utf-8

# 各マスコンのボタンとアクションを統一的に扱うIDを管理する
class Button:
    # 押してワンショットのアクションをするファンクション
    ASSIGN_TYPE_FUNC_MOMENTARY = 1
    # 押してON、もう一度押してOFFのアクションをするファンクション
    ASSIGN_TYPE_FUNC_ALTERNATE = 2

    # 押してワンショットのアクションをするアクセサリ
    ASSIGN_TYPE_ACCESSORY_MOMENTARY = 3
    # 押してON、もう一度押してOFFのアクションをするアクセサリ
    ASSIGN_TYPE_ACCESSORY_ALTERNATE = 4
    
    OHC_PC01A_WHITE = 11
    OHC_PC01A_YELLOW = 12
    
    TYPE2_UP = 21
    TYPE2_DOWN = 22
    TYPE2_SELECT = 23
    TYPE2_START = 24
    TYPE2_A = 25
    TYPE2_B = 26
    TYPE2_C = 27
    TYPE2_D = 28
    TYPE2_HONE = 29
    
    @classmethod
    def processButtons(self, button_responses, command_queue):
        pass
