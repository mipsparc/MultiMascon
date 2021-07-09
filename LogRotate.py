# ログローテーションをすることでログが肥大化するのを防ぐ
import os
import re

def rotate(log_dir):
    log_files = sorted(os.listdir(log_dir), key=lambda x:int((re.search(r"[0-9]+", x)).group(0)))

    #10個ログを残す
    for f in log_files[:-5]:
        os.remove(log_dir + '/' + f)
