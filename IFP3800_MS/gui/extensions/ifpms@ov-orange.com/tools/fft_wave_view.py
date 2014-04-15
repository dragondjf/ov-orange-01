# -*- coding: utf-8 -*-

import sys, os, types, time, socket, threading
import logging
import glob
import numpy as np
import time
import wx
import matplotlib

matplotlib.use('WXAgg') # do this before importing pylab

import matplotlib.pyplot as plt


logging.basicConfig(format='%(asctime)s %(levelname)8s [%(name)s:%(lineno)s] %(message)s',level=logging.DEBUG)


class nsIPyIfpmsDC:
    Type_Normal = 0
    Type_NetCaptor = 1
    Type_LogImporter = 2
    Type_RawLogImporter = 3
    Type_RawImporter = 4

    def __init__(self):
        self.ipaddr = "0.0.0.0"
        self.mac = "00:00:00:00:00:00"
        self.enable = True
        self.name = u""
        self.desc = u""
        self.cx = 500
        self.cy = 500
        self.status = 1
        self.latest_change_time = 0
        self.product_type = 9
        self.product_id = "IFP3800-DC"
        self.hw_version = "v0.5"
        self.sw_version = "v0.5"
        self.env_factor = 1
        self._sync_type = 0
        self._sync_status = 0  

    def init(self, dc_type, ipaddr, pa_num, did):

        self.did = did
        self.sid = "DC-%d"%did
        self.ipaddr = ipaddr
        self.pa_num = 2
        self.product_type = dc_type
        self.collector = collector.newCollector(self)
        
        if dc_type == nsIPyIfpmsDC.Type_Normal:
            self.thread = None
            pass
        elif dc_type == nsIPyIfpmsDC.Type_NetCaptor:
            self.thread = channel.NetCaptor(self.ipaddr)
        elif dc_type == nsIPyIfpmsDC.Type_LogImporter:
            self.thread = channel.LogImporter(self.ipaddr)
        elif dc_type == nsIPyIfpmsDC.Type_RawLogImporter:
            self.thread = channel.RawLogImporter(self.ipaddr)
        elif dc_type == nsIPyIfpmsDC.Type_RawImporter:
            self.thread = channel.RawImporter(self.ipaddr)
        else:
            self.thread = None
    
        return 0

    def clean(self):
        if self.thread:
            self.thread.stop()
            
    def getPA(self, pid):          
        return None


logger = logging.getLogger(__name__)

# Special hack necessary to import the "pylib" directory. See bug:
# http://bugs.activestate.com/show_bug.cgi?id=74925
old_sys_path = sys.path[:]
pylib_path = os.path.join(os.getcwd(), "..", "pylib")
sys.path.append(pylib_path)
import collector
import channel
import dcTcpServ as Serv
#from pylib import collector, channel
sys.path = old_sys_path


'''
def myshow(data):
    fig = figure(figsize=(12, 3))
    ax = fig.add_subplot(1,1,1)
#    ax.axis([1,len(data), 0.2, 1.6])
    ax.plot(data) #all data

    show()
'''

#    Type_Normal = 0
#    Type_NetCaptor = 1
#    Type_LogImporter = 2
#    Type_RawImporter = 3

dsize = 512
port = 6002
ipaddr = "192.168.100.100"
dc =nsIPyIfpmsDC()
#dc.init(nsIPyIfpmsDC.Type_LogImporter, ipaddr, 2, 1)
dc.init(nsIPyIfpmsDC.Type_Normal, ipaddr, 2, 1)
#dc.init(nsIPyIfpmsDC.Type_NetCaptor, ipaddr, 2, 1)

TSIZE = 10
TCOLOR=['b','r','g','y','h','b','g','y','r','h']
TNAME = ['min', 'max', 'freq', 'spread', 'prewarn'] + ['data%d'%n for n in range(0,TSIZE)]
#LINE_NAMES = [['min','max'],['data%d'%n for n in range(2,4)],['data5'],['data%d'%n for n in range(6,7)]+['prewarn'],['freq']]
LINE_NAMES = [['min','max'],['prewarn'],['freq']]
data = {}
plot_number = len(LINE_NAMES)
my_lines = [{}]*plot_number
my_plots = [None]*plot_number
pa = 1

#dc.init(nsIPyIfpmsDC.Type_RawImporter, "192.168.10.178", 2, 1)

serv = None

try:
    serv = Serv.DcTcpServer(('',port), Serv.NewDcTcpHandler, None, None)
    serv.add_dc(ipaddr,1)
    t = threading.Thread(name="Event Thread",target=serv.serve_forever)
    t.setDaemon(True)
    t.start()
except Exception, ex:
    context = str(ex)
    logger.error(context)
    logger.error("Can not listen tcp port on %d"%port)
finally:
    pass

'''
n = 0
offset = -10
while n < 10: 
    time.sleep(1)
    offset, freq = dc.collector.getSampling("freq",1,offset)
    print "get freq:"+' '.join([str(f) for f in freq])
    n += 1

#ax.axis([1,net_pps*net_seconds, -20, 400])


offset, freqs = dc.collector.getSampling("freq",1,-128)
myshow(freqs)

'''

def update_line(event):

    data["offset"], data['min'], data['max'], data['freq'], data['spread'], data['prewarn'], data['data0'], data['data1'], data['data2'] ,\
        data['data3'], data['data4'], data['data5'], data['data6'], data['data7'], data['data8'], data['data9'] = dc.collector.getSamplingAll(pa,-1*dsize)
    
    #print data['data4']


    for i in xrange(0,plot_number):
        tmin = 65536
        tmax = 0
        for n in xrange(0,len(LINE_NAMES[i])):
            my_lines[i][LINE_NAMES[i][n]].set_ydata(data[LINE_NAMES[i][n]])
            tmin = min(tmin,min(data[LINE_NAMES[i][n]]))
            tmax = max(tmax,max(data[LINE_NAMES[i][n]]))
        my_plots[i].axis([1,dsize, -10+tmin, 10+tmax])

    fig.canvas.draw()                 # redraw the canvas

def my_close(event):
    if dc.thread:
        dc.thread.stop()
    time.sleep(0.2)
    print "Bye"
    sys.exit(0)



fig = plt.figure(figsize=(15, 5))
for i in xrange(0,plot_number):
    my_plots[i] = fig.add_subplot(plot_number,1,i+1)
    my_plots[i].axis([1,dsize, -10, 350])
    my_plots[i].yaxis.grid()
    my_plots[i].xaxis.grid()

data["offset"], data['min'], data['max'], data['freq'], data['spread'], data['prewarn'], data['data0'], data['data1'], data['data2'] ,\
    data['data3'], data['data4'], data['data5'], data['data6'], data['data7'], data['data8'], data['data9'] = dc.collector.getSamplingAll(pa,-1*dsize)

for i in xrange(0,plot_number):
    for n in xrange(0,len(LINE_NAMES[i])):
        my_lines[i][LINE_NAMES[i][n]], = my_plots[i].plot(data[LINE_NAMES[i][n]],TCOLOR[n])

        
id = wx.NewId()
actor = fig.canvas.manager.frame
timer = wx.Timer(actor, id=id)
timer.Start(500)
wx.EVT_TIMER(actor, id, update_line)

wx.EVT_CLOSE(actor,my_close)
plt.show()
