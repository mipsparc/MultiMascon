#coding: utf-8

import sqlite3
import logging

class DB:
    dbfile = '/mnt/database/multimascon.sqlite3'

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    @classmethod
    def getSpeedOutputCurveById(self, curve_group_id):
        con = sqlite3.connect(self.dbfile)
        cur = con.cursor()
        cur.execute('''
            SELECT speed, output
            FROM speed_output_curve
            WHERE curve_group_id = ?
            ORDER BY speed ASC
        ''', (str(curve_group_id)))
        profile = cur.fetchall()
        con.close()
        
        return profile
        
    @classmethod
    def getSpeedAccelCurveById(self, curve_group_id):
        con = sqlite3.connect(self.dbfile)
        cur = con.cursor()
        cur.execute('''
            SELECT speed, accel
            FROM speed_accel_curve
            WHERE curve_group_id = ?
            ORDER BY speed ASC
        ''', (str(curve_group_id)))
        profile = cur.fetchall()
        con.close()
        
        return profile

    @classmethod
    def getLocoById(self, loco_id):
        con = sqlite3.connect(self.dbfile)
        con.row_factory = self.dict_factory
        cur = con.cursor()
        cur.execute('''
            SELECT address, accel_curve_group_id, speed_curve_group_id, base_level, light_func_id, brake_ratio
            FROM loco
            WHERE loco_id = ?
        ''', (str(loco_id)))
        profile = cur.fetchone()
        con.close()
        
        return profile
    
    @classmethod
    def getLocoIdByMasconPos(self, mascon_pos):
        con = sqlite3.connect(self.dbfile)
        cur = con.cursor()
        cur.execute('''
            SELECT loco_id
            FROM mascon_assign
            WHERE mascon_pos = ?
        ''', (mascon_pos,))
        loco_profile = cur.fetchone()
        con.close()
        
        return loco_profile
    
    @classmethod
    def getButtons(self):
        con = sqlite3.connect(self.dbfile)
        con.row_factory = self.dict_factory
        cur = con.cursor()
        cur.execute('''
            SELECT loco_id, button_id, assign_type, send_key
            FROM button_assign
            JOIN mascon_assign USING (mascon_pos)
        ''', ())
        button_profile = cur.fetchall()
        con.close()
        
        # 各車両ごとにボタン操作をまとめる
        output = {}
        for p in button_profile:
            if p['loco_id'] not in output:
                output[p['loco_id']] = {}
            output[p['loco_id']][p['button_id']] = p
        
        return output

    @classmethod
    def getKeyboards(self):
        con = sqlite3.connect(self.dbfile)
        con.row_factory = self.dict_factory
        cur = con.cursor()
        cur.execute('''
            SELECT assign_type, key_code, num
            FROM keyboard_assign
        ''', ())
        keyboard_profiles = cur.fetchall()
        con.close()

        # key_codeをキーにする
        output = {}
        for keyboard_profile in keyboard_profiles:
            output[int(keyboard_profile['key_code'])] = keyboard_profile
        
        return output

