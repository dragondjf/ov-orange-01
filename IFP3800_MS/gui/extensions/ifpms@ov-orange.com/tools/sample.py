#!/usr/bin/env python
# -*- coding: UTF8 -*-
import os
import sys
import time
from time import time,strftime
import pcap
import dpkt
from datetime import datetime
t = float(raw_input("请输入取样时长（单位：分钟）："))*60.000
import time
t1 = time.time()
date = strftime('%Y%m%d')
now = strftime('%H%M%S')
target_dir = 'G:/samples/'
target= target_dir + strftime('%Y%m%d')
if not os.path.exists(target):
   os.makedirs(target)
os.chdir(target)
f=open(now+'.txt','a')
pc = pcap.pcap()
pc.setfilter('tcp') 

for ts,pkt in pc:

      pkg = dpkt.ethernet.Ethernet(pkt)
      ip = pkg.data
      tcp = ip.data
      if pkg.data.__class__.__name__=='IP': 
         IPdst='%d.%d.%d.%d'%tuple(map(ord,list(pkg.data.src)))

      if len(tcp.data) > 0 and tcp.dport != 6001:
         print strftime('%Y-%m-%d %H:%M:%S'),"%03d" %int(datetime.now().microsecond / 1000)+"|"+IPdst+" |Send|"+" ".join(['%02x'% ord(o) for o in tcp.data])
      if len(tcp.data) != 32 and len (tcp.data) > 0 and tcp.dport == 6001:
         print strftime('%Y-%m-%d %H:%M:%S'),"%03d" %int(datetime.now().microsecond / 1000)+"|"+IPdst+"|Recv|"+" ".join(['%02x'% ord(o) for o in tcp.data])
      elif len(tcp.data) ==32 and tcp.dport ==6001:
         print strftime('%Y-%m-%d %H:%M:%S'),"%03d" %int(datetime.now().microsecond / 1000)+"|"+IPdst+"|Recv|"+" ".join(['%02x'% ord(o) for o in tcp.data])

      t2=time.time()
      t3=t2-t1
      if t3 > t:
         f.close()
         print "取样完毕，数据保存在D:\sample\..\ 目录下"
         break
    
