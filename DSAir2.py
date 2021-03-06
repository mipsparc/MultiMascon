#coding:utf-8

# DesktopStation DSAir2への接続ライブラリ

import serial
import time
import queue
import sys
import glob
import logging
from Command import Command
import signal

class DSAir2:   
    def __init__(self, port, logger):
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
            if logger:
                logging.error('DSAirを正常に認識できませんでした')
            raise IndexError
        else:
            if logger:
                logging.info('DSAirを正常に認識しました')

    def send(self, value):
        print(value)
        self.ser.write(value.encode('ascii') + b'\n')
        self.ser.flush()
        
    def reset(self):
        self.send('reset()')
        logging.info('リセット信号を送信しました')
        
    def read(self):
        return self.ser.read(200)

def safe_reset(*args):
    dsair.reset()
    exit()

# 簡単に落ちないように、どんなエラーが出ても一定時間待って再確立を試みる
def Worker(command_queue, logger):
    global dsair
    while True:
        try:
            # ttyUSB1になることもあるので
            port = glob.glob('/dev/ttyUSB*')[0]
            dsair = DSAir2(port, logger)
            signal.signal(signal.SIGTERM, safe_reset)

            Command.switchToDCC(command_queue)
            while True:
                try:
                    command = command_queue.get_nowait();
                    dsair.send(command)
                    time.sleep(0.1)
                except queue.Empty:
                    time.sleep(0.01)
        except IndexError:
            time.sleep(3)
        except Exception as e:
            logging.exception('DSAirとの接続に失敗しました')
            time.sleep(3)
