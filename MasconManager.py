from OHC_PC01A import OHC_PC01A
from DENSYA_CON_T01 import DENSYA_CON_T01
from DENSYA_CON_T03 import DENSYA_CON_T03
from PS1Dengo import PS1Dengo
from DB import DB
import logging

class MasconManager:
    mascon_connections = {}
    mascons = {}
    
    def addControl(self, adds):
        for add in adds:
            if add['port'] in self.mascon_connections.keys():
                if add != self.mascon_connections[add['port']]:
                    logging.error('USB接続情報に齟齬があります')
                    raise RuntimeError
            
            if add['vendor'] == '0079' and add['product'] == '0006':
                logging.info('OHC_PC01Aを認識')
                loco_id = DB.getLocoIdByMasconPos(add['port'])
                if loco_id is None:
                    continue
                self.mascon_connections[add['port']] = add
                self.mascons[add['port']] = OHC_PC01A(loco_id[0], add['joystick_num'])
            elif add['vendor'] == '0ae4' and add['product'] == '0004':
                logging.info('DENSYA_CON_T01を認識')
                loco_id = DB.getLocoIdByMasconPos(add['port'])
                if loco_id is None:
                    continue
                self.mascon_connections[add['port']] = add
                self.mascons[add['port']] = DENSYA_CON_T01(loco_id[0], add['bus'], add['address'])
            elif add['vendor'] == '0ae4' and add['product'] == '0007':
                logging.info('DENSYA_CON_T03を認識')
                loco_id = DB.getLocoIdByMasconPos(add['port'])
                if loco_id is None:
                    continue
                self.mascon_connections[add['port']] = add
                self.mascons[add['port']] = DENSYA_CON_T03(loco_id[0], add['bus'], add['address'])
            elif add['vendor'] == '0925' and add['product'] == '1801': # ELECOM JC-PS201U
                logging.info('PS1電車でGOマスコン(ELECOM JC-PS201U)を認識')
                loco_id = DB.getLocoIdByMasconPos(add['port'])
                if loco_id is None:
                    continue
                self.mascon_connections[add['port']] = add
                self.mascons[add['port']] = PS1Dengo(loco_id[0], add['joystick_num'])
            else:
                # 関係ないデバイス
                pass
                
    def removeControl(self, remove_ports, command_queue):
        for port in remove_ports:
            logging.info(f'ポート{port}に接続された機器を除去します')
            if port in self.mascons.keys():
                self.mascons[port].stop(command_queue)
                del(self.mascons[port])
                del(self.mascon_connections[port])
