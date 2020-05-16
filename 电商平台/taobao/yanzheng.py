#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @File    :   yanzheng.py
# @Time    :   2019/8/5 18:33
# @Author  :   LJL
# @Version :   1.0
# @Email :     491692391@qq.com
# @License :   (C)Copyright 2019-2100, LJL
# @Desc    :   None

# here put the import lib

def get_track(distance):
    '''拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速'''
    # 初速度
    v = 0
    # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
    t = 0.2
    t_a = 0.2
    t1 = 1.5
    t2 = 0.5
    # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
    tracks = []
    # 加速度(计划3秒内完成滑动)
    a1 = 2 * distance / 3
    # 减速度（3秒内完成，公式推导）
    a2 = -6 * distance
    while True:
        if t_a <= t1:
            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a1 * (t ** 2)
            tracks.append(round(s))
            # 下次的初速度
            v = v0 + a1 * t
            # 总用时
            t_a += t
        elif t1 < t_a and t_a <= t1 + t2:
            v0 = a1*t1
            s = v0 * t + 0.5 * a2 * (t ** 2)
            tracks.append(round(s))
            v = v0 + a2 * t
            t_a += t
        else:
            break

    tracks.append(distance - sum(tracks))
    print(sum(tracks),tracks)


if __name__ == '__main__':
    get_track(258)
