# ログローテーションをすることでログが肥大化するのを防ぐ
import os

def rotate(log_dir):
    log_files = sorted(os.listdir(log_dir))

    #10個ログを残す
    for f in log_files[:-10]:
        os.remove(log_dir + '/' + f)
