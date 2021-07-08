#coding: utf-8

import sqlite3
import israspi

class DB:
    if israspi.is_raspi:
        dbfile = '/mnt/database/multimascon.sqlite3'
    else:
        dbfile = 'multimascon.sqlite3'
    
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
            SELECT address, accel_curve_group_id, speed_curve_group_id, base_level, light_func_id
            FROM loco
            WHERE loco_id = ?
        ''', (str(loco_id)))
        profile = cur.fetchall()[0]
        con.close()
        
        return profile
