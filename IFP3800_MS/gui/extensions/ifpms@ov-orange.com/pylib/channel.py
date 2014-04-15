#!/usr/bin/env python
# -*- coding: UTF8 -*-

import logging
import wave
import struct
import time
import os
import glob
import re
import threading
import collector
import ifpms

DATA_SIZE = 512

logger = logging.getLogger(__name__)


class NetCaptor(threading.Thread):

    '''网络捕获'''

    def __init__(self, ipaddr, port=6001):
        self.ipaddr = ipaddr
        self.port = port
        logger.info("Create thread for capturing packet from %s." % ipaddr)
        self.collector = collector.getCollectorByIP(ipaddr)
        self._stop = threading.Event()
        threading.Thread.__init__(self)
        #super(StoppableThread, self).__init__()
        self.setDaemon(True)
        self.start()

    def stop(self):
        self._stop.set()

    def is_stopped(self):
        return self._stop.isSet()

    def run(self):
        logger.info("capture packet from %s." % self.ipaddr)

        try:
            import pcap
            import dpkt
            pc = pcap.pcap(timeout_ms=1000)
            pc.setfilter('host %s and (port %d or port %d)' % (self.ipaddr, self.port, 6002))
            pc.setnonblock()

        except Exception, e:
            logger.exception(e)

        for ts, pkt in pc:
            pkg = dpkt.ethernet.Ethernet(pkt)
            ip = pkg.data
            tcp = ip.data

            if tcp.dport == 6001 and len(tcp.data) >= 2 and tcp.data[:1] == '\x02':
                for n in xrange(0, len(tcp.data) / 16):
                    cid, length, pid, freq, unknown, tmin, tmax, eol = struct.unpack("=bbbH6sHHb", tcp.data[n * 16:n * 16 + 16])
                    if self.collector:
                        self.collector.sampling(pid, tmin, tmax, 1, freq)
            elif tcp.dport == 6002 and len(tcp.data) >= 6 and tcp.data[2] == '\x22':
                body_len, cid, ret_code, reserve1, reserve2 = struct.unpack(">HBBBB", tcp.data[:6])
                if body_len + 6 == len(tcp.data) and DATA_SIZE * 2 == body_len:
                    raw_data = list(struct.unpack('>' + 'H' * DATA_SIZE, tcp.data[6:]))
                    self.collector.raw_sampling(reserve1, raw_data)
            else:
                pass

            if self.is_stopped():
                break

        logger.info("capture packet from " + self.ipaddr + " is ok.")
        logger.info("thread exit.")


class LogImporter(threading.Thread):

    '''日志导入'''

    def __init__(self, ipaddr, collector, evt, port=6001):
        self.ipaddr = ipaddr
        self.port = port
        self.evt = evt
        self.evt.set()
        self.collector = collector
        if not collector:
            logger.info("ini import log thread ... collector dose not exist......")
        logger.info("Create thread for import log.")
        self._stop = threading.Event()
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()

    def stop(self):
        self._stop.set()

    def is_stopped(self):
        return self._stop.isSet()

    def get_logtime(self, logtime):
        return logtime

    def Importing(self, path, beginstamp, endstamp, pa_type, pid):  # 开始导入数据 样本路径 开始时间 结束时间 样本类型2,4 分别对应 日志或者波形文件 防区编号1,2
        logger.info("importing begin. path:%s begin:%s end:%s type:%s pid:%s" % (path, beginstamp, endstamp, pa_type, pid))
        if pa_type == 2:
            for filename in glob.glob(os.path.join(path, "*.txt")):
                log_file = open(filename, "r")
                logger.info("open file :" + filename)
                for line in log_file:
                    self.evt.wait()
                    if self.collector.dc.sample_config_changed:
                        logger.info('clear buff and re import ......')
                        #zeros collector data buff
                        self.collector.dc.sample_config_changed = False
                        self.collector.active_dc(self.collector.dc)
                        return
                    if self.is_stopped():  # collector is deleted ....
                        return
                    words = line.split('|')
                    t_logtime = words[0].split(',')
                    seconds = time.mktime(time.strptime(t_logtime[0], "%Y-%m-%d %H:%M:%S"))
                    if (seconds >= beginstamp and seconds <= endstamp) or (beginstamp == 0 and seconds <= endstamp) or (seconds >= beginstamp and endstamp == 0):
                        self.ReadLine(words, pid)
                    elif beginstamp == 0 and endstamp == 0:
                        self.ReadLine(words, pid)
                    else:
                        continue

        elif pa_type == 4:  # 波形文件 解析
            self.WavImport(path, beginstamp, endstamp, pid)
            return

    def ReadLine(self, words, samplepid):
        delaytime = 0.1
        rate = self.collector.dc.getPA(1).sample_import_rate
        #logger.info()
        delaytime = (1 / rate) * 0.1
        packet = None

        if len(words) == 4 and words[2] == 'Recv' and words[1] == self.collector.dc.ipaddr:
            '''2011-08-30 13:50:48,217|192.168.10.178|Recv|02 0d 01 96 7e 00 00 00 00 00 00 aa 00 62 02 ff 02 0d 02 00 00 00 00 00 00 00 00 00 00 00 00 ff'''
            packet = words[3].split(' ')
            '''2011-09-06 15:06:25 546|192.168.10.178|Recv: 02 0d 01 b1 07 00 00 00 00 00 00 2a 00 21 01 ff 02 0d 02 00 00 00 00 00 00 00 00 b8 00 11 03 ff'''
        elif len(words) == 3 and words[2][:6] == "Recv: " and words[1] == self.collector.dc.ipaddr:
            packet = words[2][6:].split(' ')
        else:
            pass

        if packet and len(packet) % 16 == 0 and packet[0] == '02':
            for n in xrange(0, len(packet) / 16):
                data = packet[n * 16:(n + 1) * 16]
                #cid = int(data[0], 16)
                #length = int(data[1],16)
                #pid = int(data[2],16)
                freq = int(''.join(data[3:5][::-1]), 16)  # 2字节？4字节？
                tmin = int(''.join(data[11:13][::-1]), 16)
                tmax = int(''.join(data[13:15][::-1]), 16)
                #havedata=True
                self.collector.sampling(1, tmin, tmax, 1, freq)
                time.sleep(delaytime)
        elif packet and len(packet) == 6 + DATA_SIZE * 2:
            data = [int(t, 16) for t in packet]
            if data[4] == samplepid:
                new_data = [0] * DATA_SIZE
                for n in xrange(0, DATA_SIZE):
                    new_data[n] = data[6 + 2 * n] * 256 + data[6 + 2 * n + 1]
                self.collector.raw_sampling(1, new_data)
                t_logtime = words[0].split(',')
                seconds = time.mktime(time.strptime(t_logtime[0], "%Y-%m-%d %H:%M:%S"))
                self.collector.logtime[0] = self.get_logtime(seconds * 1000 + int(t_logtime[1]))  # 毫秒获取
                #logger.info('logtime=%d'%seconds)
            time.sleep(delaytime)

    def WavImport(self, path, beginstamp, endstamp, pid):
        '''
        Search files according to the beginstamp and endstamp in the gaven path.

        The function returns timestamps and packets imported from *.wav files.
        Each packet is a list which contains 512 data read from the file and matches the timestamp.
        When conditions gotten from the administor changed,search again.Then return new results.
        '''
        package = []
        filenames = []
        if ifpms.wav_flag:
            filenames = self.FilenameFilter(path, beginstamp, endstamp, pid)
        else:
            if beginstamp == 0 and endstamp == 0:
                pass
            else: 
                filenames = self.dynamic_wavname(path, beginstamp, endstamp, pid)
        for filename in filenames:
            if os.path.isfile(filename):
                logger.info("import file :" + filename)
                offset = 0
                timespace = 0
                current_time = 0
                year = int('20' + filename[-15:-13])
                month = int(filename[-13:-11])
                day = int(filename[-11:-9])
                hour = int(filename[-8:-6])
                minute = int(filename[-6:-4])
                date = (year, month, day, hour, minute, 0, 0, 0, 0)  # translate time into the form of struct_time
                file_name = dict(seconds=time.mktime(date))  # create dictionary for elements on which searching is to be based
                try:
                    wav_file = wave.open(filename)  # open target file and get data from them
                    #framerate = wav_file.getframerate()
                    framenum = wav_file.getnframes()
                    Timestamp = file_name['seconds']
                    for n in xrange(0, framenum):  # store data in a sublist
                        data = wav_file.readframes(1)
                        if self.is_stopped():  # collector is deleted
                            return
                        package.append(struct.unpack('h', data)[0])

                        if len(package) % 1024 == 0:
                            self.collector.logtime[0] = self.get_logtime(Timestamp * 1000)
                            Timestamp += 0.1

                            packet = [(d + 32768) / 16 for d in package]

                            self.collector.raw_sampling(1, packet)
                            self.evt.wait()
                            last_time = current_time  # the time point of last packet performed
                            current_time = time.clock()  # the time point of current packet performed
                            rate = self.collector.dc.getPA(1).sample_import_rate
                            rate = 1 / rate
                            t_space = 0.1 * rate - (current_time - last_time)
                            last_timespace = timespace  # the last timespace between two packets
                            #keep the speed of performance automatically
                            if offset < 2:
                                timespace = 0.094840
                            elif offset > 1:
                                if -0.025 < t_space < 0.025:
                                    timespace = last_timespace + t_space
                                else:
                                    timespace = last_timespace
                            foo = timespace * rate
                            if foo < 0.0:
                                foo = 0.0
                            time.sleep(foo)
                            #logger.info('sleep : %f'%(timespace * rate))
                            package = []
                            offset += 1
                            if not self.collector:
                                return
                            if self.collector.dc.sample_config_changed:  # if config changed,restar collector
                                self.collector.dc.sample_config_changed = False
                                self.collector.active_dc(self.collector.dc)
                                return
                    logger.info("wav file frame number is:%d", framenum)
                except Exception, e:
                    logger.exception(e)
                finally:
                    wav_file.close()
        return

    def dynamic_wavname(self, path, beginstamp, endstamp, pid):
        filenames = []
        n = (endstamp - beginstamp) / 60
        try:
            for j in xrange(int(n)):
                t = list(time.localtime(beginstamp + 60 * j))
                for i in xrange(len(t)):
                    if t[i] < 10:
                        t[i] = '0' + str(t[i])
                    else:
                        t[i] = str(t[i])
                filename_t = t[0][2:] + t[1] + t[2] + '-' + t[3] + t[4]
                filename = path + '\\' + self.collector.dc.ipaddr + '-' + str(pid) + '-' + filename_t + '.wav'
                filenames.append(filename)
        except Exception, e:
            logger.info(e)
        return filenames

    def FilenameFilter(self, path, beginstamp, endstamp, pid):
        '''
        Find the files whose names match with the form of "xxx.xxx.xxx.xxx-x-xxxxxx-xxxx.wav".

        The function returns a list of filenames which is sorted based on the timestamps contained by themselves.
        '''
        pattern = '.*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d-\d{6}-\d{4}\.wav$'
        filenames = []
        if endstamp == 0:
            endstamp = time.time()
        for filename in glob.glob(os.path.join(path, "*.wav")):
            if re.search(pattern, filename):
                fileabsname = os.path.basename(filename)
                year = int('20' + filename[-15:-13])
                month = int(filename[-13:-11])
                day = int(filename[-11:-9])
                hour = int(filename[-8:-6])
                minute = int(filename[-6:-4])
                date = (year, month, day, hour, minute, 0, 0, 0, 0)  # translate time into the form of struct_time
                file_name = dict(ipaddr=fileabsname[:-18], pid=int(filename[-17]), seconds=time.mktime(date))  # create dictionary for elements on which searching is to be based
                if file_name['ipaddr'] == self.collector.dc.ipaddr and file_name['pid'] == pid and beginstamp - 60 < file_name['seconds'] < endstamp + 60:
                    filenames.append(filename)
            else:
                pass
        filenames.sort(key=self.f_id)
        return filenames

    def f_id(self, f_id):  # the key of sort() method used by FilenameFilter
        return int(f_id[-15:-9] + f_id[-8:-4])

    def ReImport(self):
        logger.info("function reimport  begin.....")
        pa1 = None
        if self.is_stopped():
            return
        pa1 = self.collector.dc.getPA(1)
        if not pa1:
            logger.info('get pa error')
            return
        #logger.info("sample path"+pa1.sample_path)
        path = pa1.sample_path
        #logger.info("sample begin stamp%d"%pa1.sample_startstamp)
        begin = pa1.sample_startstamp
        end = pa1.sample_endstamp
        #logger.info("sample end %d"%pa1.sample_endstamp)
        pid = pa1.sample_pid
        #logger.info("sample pid %d"%pa1.sample_pid)
        #logger.info("dc_type%d"%self.collector.dc.product_type)
        self.Importing(path, begin, end, self.collector.dc.product_type, pid)

    def run(self):
        if not self.collector:
            logger.error("Invaild collector!")
            return
        self.ReImport()
        logger.info("Importing finished!")
        if self.is_stopped():
            logger.info("dc deleted ,importing thread exit...")
            return
        logger.info("Importing done and will  restart in 2 seconds.... ")
        time.sleep(2)
        self.run()
