#coding:utf-8

# 座標群から一次関数の連続を作って、値を求める

def getValue(value, profile):
    for i, p in enumerate(profile):
        if p[0] == value:
            return p[1]
        if p[0] > value:
            # 1次関数を求める
            tilt = (p[1] - profile[i-1][1]) / (p[0] - profile[i-1][0])
            b = p[1] - tilt * p[0]
            output = int(tilt * value + b)
            return output
