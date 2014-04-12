# -*- coding: utf-8 -*-

import urllib2
from json import dumps, loads
import commands
import ConfigParser
import os
from config import get_ip_address
import time

dc_ip = get_ip_address('eth0')
dc_url = 'http://localhost:9000/DCs/'
pa_url = 'http://localhost:9000/PAs/'


def set_pa():
    # delete DC
    req = urllib2.Request(dc_url)
    res = urllib2.urlopen(req).read()
    json = loads(res)['objs']
    for item in json:
        if dc_ip == item['ip']:
            dc_id = item['_id']
            req = urllib2.Request(dc_url + dc_id)
            req.get_method = lambda: "DELETE"
            urllib2.urlopen(req).read()
    # create DC
    dc_args = {'ip': dc_ip, 'ver': 2, 'subnet_mask': '255.255.255.0', }
    dc_args = dumps(dc_args)
    req = urllib2.Request(dc_url, dc_args)
    res = urllib2.urlopen(req).read()
    res = loads(res)
    dc_id = res['_id']
    # get pa_id2
    req = urllib2.Request(pa_url)
    res = urllib2.urlopen(req).read()
    json = loads(res)['objs']
    for item in json:
        if dc_id == item['dc_id']:
            pa_id = item['_id']
    return dc_id, pa_id


def start_test(args, wave_type, s_w_num1, s_w_num2):
    args = dumps(args)
    print 'start test %s' % wave_type
    print 'post to pa2:%s' % args
    print './start.py -n -p ../../tools/wavfile/%s/ -z' % (wave_type)
    print 'warning number should be: pa1 %s  pa2 %s' % (s_w_num1, s_w_num2)
    dc_id, pa_id = set_pa()
    req = urllib2.Request(pa_url + pa_id, args)
    req.get_method = lambda: "PATCH"
    urllib2.urlopen(req).read()
    commands.getoutput(
        './start.py -n -p ../../tools/wavfile/%s/ -z' % (wave_type))
    filename1 = '%s:1' % dc_ip
    filename2 = '%s:2' % dc_ip
    w_num1 = 0
    w_num2 = 0
    if os.path.exists(filename1):
        cf = ConfigParser.ConfigParser()
        cf.read(filename1)
        w_num1 = cf.getint("main", "w_num")
        os.remove(filename1)
    if os.path.exists(filename2):
        cf = ConfigParser.ConfigParser()
        cf.read(filename2)
        w_num2 = cf.getint("main", "w_num")
        os.remove(filename2)
    print 'warning number: pa1 %s  pa2 %s' % (w_num1, w_num2)
    if w_num1 == s_w_num1 and w_num2 == s_w_num2:
        print 'pass\n'
    else:
        print 'error\n'
    time.sleep(1)
    # delete DC
    req = urllib2.Request(dc_url + dc_id)
    req.get_method = lambda: "DELETE"
    urllib2.urlopen(req).read()
    time.sleep(1)

print ''.join([
    '\npa1 is default:'
    '\nworkmode: ifpms_normal'
    '\nsensitivity=40  responsetime=2  resistantfactor=5'
    '\nfiberbreak_k:{break_time: 2,fiber_break_davg: 12,fiber_break_k: 200}\n'
])

pa_blast_alg = {
    #自适应周界
    'gsd_adaptation': [{
        'win_setting': 'f0',  # 与算法模式对应的窗口
        'daytime': [7, 20],   # 白天时段 7点至20点，即21点至次日6点为夜晚
        'responsetime_s': [6, 6],    # 短时间范围：单位为秒，乘以单位点数则为瞬间点数
        'responsetime_l': [300, 300],    # 长时间范围：单位为秒，乘以单位点数则为瞬间点数
        'sensitivity': [40, 40],  # 相对特征值data0进行比较的
        'ratio': [0.1, 0.1]   # 长时间统计的预警率百分比门限
    }],
    #爆破算法
    'gsd_blast': [{
        'win_setting': 'f0',  # 爆破窗口
        'responsetime': 1,  # 爆破响应时间
        'absolutef': 1000,  # 爆破绝对能量值门限
        'relatef': 40  # 爆破相对值门限
    }]
}

pa_fiberbreak_alg = {
    #斜率校正判定
    'fiberbreak_k': [{
        'break_time': 2,  # 短纤响应时间
        'fiber_break_davg': 5,  # 一个点的断纤平均值davg门限
        'fiber_break_k': 200  # 斜率校正断纤，特征值data9超过此值表示断纤
    }]
}

args2 = {"alg": pa_fiberbreak_alg}
start_test(args2, 'fiber_broken', 8, 7)

args2 = {"sensitivity": 1000, "responsetime": 2, "resistantfactor": 1}
start_test(args2, 'normal', 3, 5)

args2 = {"sensitivity": 400, "responsetime": 2, "resistantfactor": 1}
start_test(args2, 'warning', 2, 4)

args2 = {"workmode": "gsd_adaptation", "alg": pa_blast_alg}  # pa_default_alg
start_test(args2, 'blast', 3, 1)


# start_test(args2, 'excavate', 1, 1)
