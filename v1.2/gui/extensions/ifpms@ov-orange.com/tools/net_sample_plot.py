"""
JAN data instant parser
"""
import time
import matplotlib
import thread
import dpkt
import pcap
import wx

matplotlib.use('WXAgg') # do this before importing pylab

import matplotlib.pyplot as plt

fig = plt.figure()

net_pps = 8   #packet number per second
net_seconds = 30 #capturing seconds

net_data_enable = [False,False,True,True]
net_data_enable = [True,True,False,False]

net_data1 = [0]*(net_pps*net_seconds)
net_data2 = [0]*(net_pps*net_seconds)
net_data3 = [0]*(net_pps*net_seconds)
net_data4 = [0]*(net_pps*net_seconds)

FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def dump(src, length=16):
    N=0; result=''
    while src:
       s,src = src[:length],src[length:]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       s = s.translate(FILTER)
       result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
       N+=length
    return result

class CapThread:
    def __init__(self):
        pass

    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Run(self):
        
        #f = open('1.pcap')
        #pc = dpkt.pcap.Reader(f)

        no = 0
        starttime = time.time()
        pc = pcap.pcap(timeout_ms=1000)
        pc.setfilter('port 6001')
        
        #while True:
        #    ts, pkt = pc.next()
        #    if pkt != None:
        #        pkg = dpkt.ethernet.Ethernet(pkt)
        #        net_data.pop(0)
        #        net_data.append(len(pkg)%512)
        #    else:
        #        net_data.pop(0)
        #        net_data.append(0)
        #        print 'timeout'
            
        for ts,pkt in pc:
            #print dump(pkt) 
            pkg = dpkt.ethernet.Ethernet(pkt)
            ip = pkg.data
            tcp = ip.data
            
            if tcp.dport == 6001 and len(tcp.data) >= 32 and tcp.data[:3] == '\x02\x0d\x01' :
                #print dump(tcp.data)
                #print tcp.sport
                ords = [ ord(n) for n in tcp.data ]                
                net_data1.pop(0)
                net_data1.append(ords[3])
                net_data2.pop(0)
                net_data2.append(ords[4])
                net_data3.pop(0)
                net_data3.append(ords[12]*256+ords[11])
                net_data4.pop(0)
                net_data4.append(ords[14]*256+ords[13])
                
                print "%4d %4d: %3d %3d %3d %3d"%(time.time()-starttime,no,ords[3],ords[4],ords[12]*256+ords[11],ords[14]*256+ords[13])
                no += 1
                
            #net_data.append(len(pkg)%512)
            #print "aa=[%d]"%aa
            #net_data.append(len(pkg))
        
        self.running = False

ax = fig.add_subplot(111)
ax.axis([1,net_pps*net_seconds, -20, 400])

if net_data_enable[0] == True:
    line1, = ax.plot(net_data1,"r")
if net_data_enable[1] == True:
    line2, = ax.plot(net_data2,"b")
if net_data_enable[2] == True:
    line3, = ax.plot(net_data3,"m")
if net_data_enable[3] == True:
    line4, = ax.plot(net_data2,"c")

#for i in xrange(0,4):
#    line, = ax.plot(net_data[i],"r")
#    lines.append(line)

def update_line(event):
    #for i in xrange(0,4):
    #    lines[i].set_ydata(net_data[i])
    if net_data_enable[0] == True:
        line1.set_ydata(net_data1)
    if net_data_enable[1] == True:
        line2.set_ydata(net_data2)
    if net_data_enable[2] == True:
        line3.set_ydata(net_data3)
    if net_data_enable[3] == True:
        line4.set_ydata(net_data4)
    fig.canvas.draw()                 # redraw the canvas

# start capture thread
threads = []
threads.append(CapThread())

for t in threads:
    t.Start()

id = wx.NewId()
actor = fig.canvas.manager.frame
timer = wx.Timer(actor, id=id)
timer.Start(50)
wx.EVT_TIMER(actor, id, update_line)

plt.show()
