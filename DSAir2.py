#coding:utf-8

# DesktopStation DSAir2への接続ライブラリ

import serial
import time
import queue

class DSAir2:   
    def __init__(self, port):
        self.ser = serial.Serial(port, baudrate=115200, timeout=0.2, write_timeout=0.2, inter_byte_timeout=0.1)
        # DSair2を再起動
        self.reset()
        time.sleep(1)

        self.ser.reset_input_buffer()
        self.send('setPing()')
        time.sleep(1)
        init_response = self.ser.read(200)
        if (not init_response.decode('ascii').endswith('200 Ok\r\n')
            and not init_response.decode('ascii').endswith('100 Ready\r\n')
        ):
            print('DSair2を正常に認識できませんでした。終了します')
            raise ValueError('DSair2認識エラー')
        else:
            print('DSair2を正常に認識しました。')

    def send(self, value):
        self.ser.write(value.encode('ascii') + b'\n')
        self.ser.flush()
        
    def reset(self):
        self.send('reset()')
        
    def read(self):
        self.ser.readline()

def Worker(port, command_queue):
    dsair = DSAir2(port)
    
    while True:
        try:
            commands = [];
            #キューを一旦すべて取得する
            while True:
                try:
                    commands.append(command_queue.get_nowait())
                except queue.Empty:
                    break
            
            #取得したコマンドをすべて一定間隔で送信する
            print('送出コマンド数: ' + str(len(commands)))
            for command in commands:
                dsair.send(command)
                # ブロックする
                print(dsair.readline())
        # 緊急停止
        finally:
            dsair.reset()
