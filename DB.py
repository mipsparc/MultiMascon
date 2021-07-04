#coding: utf-8

import sqlite3
import israspi

class DB:
    if israspi.is_raspi:
        dbfile = '/mnt/database/multimascon.sqlite3'
    else:
        dbfile = 'multimascon.sqlite3'
    
    @classmethod
    def getSpeedAccelCurveById(self, curve_group_id):
        print(self.dbfile)
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
        
