# ログローテーションをすることでログが肥大化するのを防ぐ
import os
import pathlib

def rotate(log_dir):
    log_filenums = sorted([int(p.stem) for p in pathlib.Path(log_dir).iterdir()], reverse=True)

    #10個ログを残す
    for f in log_filenums[5:]:
        os.remove(log_dir + '/' + f'{f}.txt')
