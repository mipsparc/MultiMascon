from OHC_PC01A import OHC_PC01A
from DENSYA_CON_T01 import DENSYA_CON_T01
from DB import DB

class MasconManager:
    mascons = {}
    
    def addControl(self, adds):
        for add in adds:
            if add['port'] in self.mascons.keys():
                if add != self.mascons[add['port']]:
                    raise RuntimeError

            self.mascons[add['port']] = add
            
            if add['vendor'] == '0079' and add['product'] == '0006':
                loco_id = DB.getLocoIdByMasconPos(add['port'])
                new_mascon = OHC_PC01A(loco_id, add['joystick_num'])
            elif add['vendor'] == '0ae4' and add['product'] == '0004':
                loco_id = DB.getLocoIdByMasconPos(add['port'])
                new_mascon = DENSYA_CON_T01(loco_id, add['bus'], add['address'])
                
    def removeControl(self, removes):
        for remove in removes:
            if add['port'] in self.mascons.keys():
                del(self.mascon[add['port']])
