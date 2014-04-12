#!/usr/bin/env python
# -*- coding: UTF8 -*-

import sys
import os
import time
import socket
import threading
import logging
import glob
import random
import wave
import struct
import SocketServer
import math

from logging.handlers import RotatingFileHandler

from xpcom import components, ServerException, nsError
from xpcom._xpcom import getProxyForObject


try:
    # Mozilla 1.9
    from xpcom._xpcom import NS_PROXY_SYNC, NS_PROXY_ALWAYS, NS_PROXY_ASYNC
except ImportError:
    # Mozilla 1.8 used different naming for these items.
    from xpcom._xpcom import PROXY_SYNC as NS_PROXY_ASYNC
    from xpcom._xpcom import PROXY_ALWAYS as NS_PROXY_ALWAYS
    from xpcom._xpcom import PROXY_ASYNC as NS_PROXY_ASYNC


# Special hack necessary to import the "pylib" directory. See bug:
# http://bugs.activestate.com/show_bug.cgi?id=74925
old_sys_path = sys.path[:]
pylib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pylib")
sys.path.append(pylib_path)
import dcTcpServ as Serv
import collector
import channel
import iudp
import ipkt
from webs import WebsHandler, WebPush
from sms import PySMS
#compile .py to .pyc
try:
    import py_compile
    py_compile.compile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pylib", "ifpms.py"))
    py_compile.compile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pylib", "userifpms.py"))
except Exception, e:
    pass

import ifpms
import userifpms
import mark

from collector import pa_env
sys.path = old_sys_path


#设置日志格式与位置
#logging.basicConfig(filename='log\error.log',format='%(asctime)s %(levelname)8s [%(name)s:%(lineno)s] %(message)s',level=logging.ERROR)

#主日志保存在log/ifpms.log
logging.root.setLevel(logging.INFO)
logging.root.propagate = 0
loghandler = RotatingFileHandler(os.path.join("log", "ifpms.log"), maxBytes=ifpms.log_size, backupCount=ifpms.log_num)
loghandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)8s [%(filename)16s:%(lineno)04s] %(message)s'))
loghandler.level = logging.INFO
logging.root.addHandler(loghandler)
logger = logging.root
logger.propagate = 0

#报文日志，保存在log/packet.log
plogger = logging.getLogger("packet")
plogger.setLevel(logging.DEBUG)
plogger.propagate = 0
loghandler = RotatingFileHandler(os.path.join("log", "packet.log"), maxBytes=ifpms.log_size, backupCount=ifpms.log_num)
loghandler.level = logging.DEBUG
loghandler.setFormatter(logging.Formatter('%(asctime)s|%(ip)s|%(message)s'))
plogger.addHandler(loghandler)


class nsIPyIfpmsPA:
    # XPCOM registration attributes.
    _com_interfaces_ = [components.interfaces.nsIPyIfpmsPA]
    _reg_clsid_ = "{dbe9c5ab-e5e6-4096-86a7-c3a1dc9e5567}"
    _reg_contractid_ = "@ov-orange.com/pyIfpmsPA;1"
    _reg_desc_ = "Ifpms PA"

    def __init__(self):

        self.did = 0
        self.pid = 0
        self.sample_pid = 0
        self.sid = ""
        self.name = u""
        self.desc = u""
        self.enable = True
        self.audio_enable = False
        self.cx = 0
        self.cy = 0
        self.status = 1
        self.latest_change_time = 0
        self.work_mode = ifpms.pa_default_val[mark.logo]["work_mode"]  # 周界
        self.process_mode = ifpms.pa_default_val[mark.logo]["process_mode"]  # 预处理模式
        self.alarm_resp_time = ifpms.pa_default_val[mark.logo]["alarm_resp_time"]  # 报警响应时间，秒
        self.alarm_sensitivity = ifpms.pa_default_val[mark.logo]["alarm_sensitivity"]  # 系统灵敏度，越小越灵敏
        self.alarm_resistant_factor = ifpms.pa_default_val[mark.logo]["alarm_resistant_factor"]  # 系统抗扰度，次数越小越不抗扰
        self.alarm_resistant_factor_gsd = ifpms.pa_default_val[mark.logo]["alarm_resistant_factor_gsd"]  # 系统抗扰度，次数越小越不抗扰
        self.sensitivity = ifpms.pa_default_val[mark.logo]["sensitivity"]
        self.enable_start = 0
        self.enable_end = 0
        self.sample_path = "sample\log"
        self.sample_startstamp = 0
        self.sample_endstamp = 0
        self.sample_currentstamp = 0
        self.sample_import_rate = 1
        self.fft_begin = 5
        self.fft_end = 100
        self.fft_noise_value = 25
        self.fft_magic_value = 1
        self.fft_size = 512
        self.fft_style = 1
        self.dc = None
        self.collector = None

    def pre_init(self, did, pid):
        self.did = did
        self.pid = pid
        self.sample_pid = 1
        self.sid = "PA-%d-%d" % (did, pid)
        self.name = u"防区 %d-%d" % (did, pid)
        return 0

    def post_init(self, dc):
        self.dc = dc
        self.collector = collector.getCollectorByDid(self.did)
        return 0

    def getSampling(self, type, offset):
        if self.collector:
            return self.collector.getSampling(type, self.pid, offset)
        else:
            return 0, [], []

    def getSamplingBasic(self, offset):
        if self.collector:
            return self.collector.getSamplingBasic(self.pid, offset)
        else:
            return 0, 0, None, None, None, None, None

    def getSamplingAll(self, offset):
        if self.collector:
            return self.collector.getSamplingAll(self.pid, offset)
        else:
            return 0, 0, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None

    def getWaveFile(self, timestamp):
        #filename=self.sid+repr(timestamp)
        wav_path = ifpms.wav_path + self.dc.ipaddr + '-' + str(self.pid) + '/'
        timeinfo = time.strftime("%y%m%d-%H%M", time.localtime(timestamp - 60))
        objfname = self.dc.ipaddr + "-" + repr(self.pid) + "-" + timeinfo + '.wav'
        fname = os.path.join(wav_path, objfname)
        if os.path.exists(fname):
            logger.info('get wave file : ' + fname)
            return os.path.basename(fname)
        else:
            return "NULL"

    def getWavData(self, timestamp):
        wav_filename = self.getWaveFile(timestamp)
        if wav_filename == "warn.wav":
            wav_filename = "null"
        wav_path = ifpms.wav_path + self.dc.ipaddr + '-' + str(self.pid) + '/'
        wav_filename = os.path.join(wav_path, wav_filename)
        logger.info("wav file is :%s", wav_filename)
        if os.path.exists(wav_filename):
            wav_data = []
            framerate = 0
            wav_file = None
            try:
                wav_file = wave.open(wav_filename, "r")
                framerate = wav_file.getframerate()
                framenum = wav_file.getnframes()
                # for n in xrange(0, framenum):
                #     data = wav_file.readframes(1)
                #     wav_data.append(struct.unpack('h', data)[0])
                data = wav_file.readframes(framenum)
                wav_data = list(struct.unpack('h' * framenum, data))
                logger.info("wav file frame number is:%d", framenum)
            except Exception, e:
                logger.exception(e)
            finally:
                wav_file.close()

            return framerate, wav_data[::512]

        else:
            logger.info("%s is not existed", wav_filename)
            data = random.sample(xrange(10000), 1000)
            return 1, list(data)


class nsIPyIfpmsDC:
    # XPCOM registration attributes.
    _com_interfaces_ = [components.interfaces.nsIPyIfpmsDC]
    _reg_clsid_ = "{da1b8cda-c972-47a6-bcb8-ba69fcff5b0c}"
    _reg_contractid_ = "@ov-orange.com/pyIfpmsDC;1"
    _reg_desc_ = "Ifpms DC"

    Type_Normal = 0
    Type_NetCaptor = 1
    Type_LogImporter = 2
    Type_RawLogImporter = 3
    Type_WavImporter = 4

    def __init__(self):

        self.did = 0
        self.sid = ""
        self.pa_num = 0
        self.ipaddr = "0.0.0.0"
        self.mac = "00:00:00:00:00:00"
        self.enable = True
        self.audio_enable = False
        self.name = u""
        self.desc = u""
        self.cx = 500
        self.cy = 500
        self.status = 1
        self.latest_change_time = 0
        self.product_type = 0
        self.protocol_ver = 2
        self.Q_workmode = 0
        self.product_id = "IFP3800-DC"
        self.hw_version = "v0.5"
        self.sw_version = "v0.5"
        self.machine_id = 0
        self.slot_id = 0
        self.medium_type = 1
        self.sensitivity = 128
        self.sensitivity2 = 0
        self.env_factor = 1
        self.sample_config_changed = False

        self.pa_list = components.classes["@mozilla.org/array;1"] \
            .createInstance(components.interfaces.nsIMutableArray);

    def pre_init(self, dc_type, ipaddr, pa_num, did):

        self.did = did
        self.sid = "DC-%d" % did
        self.name = u"采集器 %d" % did
        self.ipaddr = ipaddr
        self.pa_num = pa_num
        self.product_type = dc_type

        return 0

    def post_init(self):

        dc_type = self.product_type
        self.collector = collector.newCollector(self)

        waitevt = threading.Event()
        if dc_type == nsIPyIfpmsDC.Type_Normal:
            self.thread = None
        elif dc_type == nsIPyIfpmsDC.Type_NetCaptor:
            self.thread = channel.NetCaptor(self.ipaddr)
        elif dc_type == nsIPyIfpmsDC.Type_LogImporter:
            self.thread = channel.LogImporter(self.ipaddr, self.collector, evt=waitevt)
        elif dc_type == nsIPyIfpmsDC.Type_WavImporter:
            self.thread = channel.LogImporter(self.ipaddr, self.collector, evt=waitevt)
        else:
            self.product_type = nsIPyIfpmsDC.Type_Normal
            self.thread = None

        return 0

    def set(self, medium_type, sensitivity, sensitivity2, env_factor):
        self.medium_type = medium_type
        self.sensitivity = sensitivity
        self.sensitivity2 = sensitivity2
        self.env_factor = env_factor
        return 0

    def blockThread(self):
        if self.thread:
            self.thread.evt.clear()
            return True
        else:
            return False

    def awakeThread(self):
        if self.thread:
            self.thread.evt.set()
            return True
        else:
            return False

    def sync(self, cmd, channel_id):

        logger.info("put cmd: did %d, pid %d, cmd %d" % (self.did, channel_id, cmd))
        try:
            if self.collector.pa[channel_id - 1].name == u"环境自适应探测器":
                pa = self.collector.pa[channel_id - 1]
                pa_env.update({'sid': pa.sid})
                logger.info(pa.desc)
                if u'&' in pa.desc:
                    p = pa.desc.split('&')
                    if u'S=' in p[0]:
                        sensitivity_step = int(p[0].split('=')[1])
                        pa_env.update({'sensitivity_step': sensitivity_step})
                    if u'K=' in p[1]:
                        alarm_resistant_factor_step = int(p[1].split('=')[1])
                        pa_env.update({'alarm_resistant_factor_step': alarm_resistant_factor_step})
                logger.info(pa_env)
        except Exception, e:
            logger.info(e)

        try:
            if self.product_type == nsIPyIfpmsDC.Type_Normal and channel_id < 9:
                if self.protocol_ver == 3:
                    #  Q系列独立工作模式下发送通道控制信息
                    if self.Q_workmode == 1:
                        self.Q_setudp(cmd, channel_id, self.protocol_ver)
                    else:
                        self.collector.cmd_queue.put_nowait((cmd, channel_id))
                    #  发送设备控制信息
                    self.Q_setudp(0x09, channel_id, self.protocol_ver)
                else:
                    self.collector.cmd_queue.put_nowait((cmd, channel_id))
            elif cmd == 3 and channel_id == 9 and self.Q_workmode == 1:  # 切换成独立工作模式
                #  切换采集器模式
                header = ipkt.Header(cmd=0x03)
                body = ipkt.CommInfo(mode=1)
                sess = iudp.Session(self.ipaddr, ifpms.udp_port)
                sess.deal(header=header, body=body)
                #  保存配置
                header = ipkt.Header(cmd=0x0d, ret=0, seq=0)
                body = ipkt.Empty()
                sess = iudp.Session(self.ipaddr, ifpms.udp_port)
                sess.deal(header=header, body=body)
                #  重启命令
                header = ipkt.Header(cmd=0x0c, ret=0, seq=0)
                body = ipkt.Empty()
                sess = iudp.Session(self.ipaddr, ifpms.udp_port)
                sess.deal(header=header, body=body)
            elif cmd == 3 and channel_id == 10 and self.Q_workmode == 0:  # 切换成采集器模式
                #  切换采集器模式
                header = ipkt.Header(cmd=0x03)
                body = ipkt.CommInfo(mode=0)
                sess = iudp.Session(self.ipaddr, ifpms.udp_port)
                sess.deal(header=header, body=body)
                #  保存配置
                header = ipkt.Header(cmd=0x0d, ret=0, seq=0)
                body = ipkt.Empty()
                sess = iudp.Session(self.ipaddr, ifpms.udp_port)
                sess.deal(header=header, body=body)
                #  重启命令
                header = ipkt.Header(cmd=0x0c, ret=0, seq=0)
                body = ipkt.Empty()
                sess = iudp.Session(self.ipaddr, ifpms.udp_port)
                sess.deal(header=header, body=body)
        except Exception, e:
            logger.info(e)
        return 0

    def Q_setudp(self, cmd_id, channel_id, protocol_ver):
        header = ipkt.Header(cmd=cmd_id, channel=channel_id, ret=0, seq=0)
        #  设置设备控制信息
        if cmd_id == ipkt.SET_DEVICE_FUNCTION_REQ:
            body = ipkt.DeviceFunction()
            body.set_cellphones(ifpms.Q_phones)
            body.set_pa_name(self.collector.pa[0].name, 1)
            body.set_pa_name(self.collector.pa[1].name, 2)
            body.set_pa_name(self.collector.pa[2].name, 3)
            body.set_pa_name(self.collector.pa[3].name, 4)
        #  设置通道控制信息
        elif cmd_id == ipkt.SET_CHANNEL_CTRL_REQ:

            win_setting = ifpms.fft_window_settings[self.collector.pa[channel_id - 1].work_mode]
            if self.collector.pa[channel_id - 1].work_mode == 4: # 自适应
                work_mode = 0
            elif self.collector.pa[channel_id - 1].work_mode == 1: # 标准
                work_mode = 1
            elif self.collector.pa[channel_id - 1].work_mode == 2:  # 风雨
                work_mode = 2
                win_setting = ifpms.fft_window_settings[4]
            elif self.collector.pa[channel_id - 1].work_mode == 6:  #  均方
                work_mode = 3
            # Q系列独立工作模式下发通道控制信息中win_size为4，利用到了四组窗口
            body = ipkt.ChannelCtrl_v3( \
                enable=self.collector.pa[channel_id - 1].enable, \
                mu_factor=self.sensitivitycompound(self.collector.pa[channel_id - 1].sensitivity), \
                mode=self.collector.pa[channel_id - 1].process_mode, \
                pre_process_mode=1,
                win_size=4, \
                defence_start = self.collector.pa[channel_id - 1].enable_start, \
                defence_end = self.collector.pa[channel_id - 1].enable_end, \
                work_mode = work_mode, \
                sensitivity = self.collector.pa[channel_id - 1].alarm_sensitivity, \
                response_time = self.collector.pa[channel_id - 1].alarm_resp_time, \
                noise_immunity = self.collector.pa[channel_id - 1].alarm_resistant_factor, \
                )
            body.set_windows_Q(win_setting, work_mode)
        sess = iudp.Session(self.ipaddr, ifpms.udp_port)
        sess.deal(header=header, body=body, protocol_ver=protocol_ver)

    def sensitivitybreak(self, A):
        sn = [0, 0]
        flag = 0
        cnt = 0
        if A >= 2 and A < 65536:
            if A == 2:
                sn = [2, 1]
                return sn
            elif 2 < A <= 512:
                sn = [A, 1]
                return sn
            else:
                while(1):
                    for i in range(A / 255 + 1, int(math.sqrt(A))):
                        if (i > 1):
                            if (A % i):
                                pass
                            else:
                                sn[0] = max(i, A / i)
                                sn[1] = min(i, A / i)
                                return sn

                    cnt = cnt + 1
                    if (cnt % 2):
                        flag = flag + 1
                        A += flag
                    else:
                        flag = flag + 1
                        A -= flag
        else:
            logger.info("Invalid digitalsensitivity number!")

    def sensitivitycompound(self, A):
        sn = self.sensitivitybreak(A)
        logger.info("The first level N1=%d and the second level N2=%d" % (sn[0], sn[1]))
        if sn[1] > 1:
            return (sn[0] - 1) * 256 + (sn[1] - 2)
        else:
            return (sn[0] / 2 - 1) * 256 + (sn[1] - 1)

    def clean(self):
        self.collector.active = False
        self.collector.dc = None

        if self.thread:
            self.thread.stop()

    def getPA(self, pid):
        ''' 根据编号取防区对象 '''
        if self.pa_list.length == 0:
            logger.info("there is no pas.....")
            return None
        for i in xrange(0, self.pa_list.length):
            t = self.pa_list.queryElementAt(i, components.interfaces.nsIPyIfpmsPA)
            if t and t.pid == pid:
                return t

        return None


class nsIPyIfpmsAlarmRecord:
    # XPCOM registration attributes.
    _com_interfaces_ = [components.interfaces.nsIPyIfpmsAlarmRecord]
    _reg_clsid_ = "{5d3096a3-2aeb-4051-b1ac-07806be803f6}"
    _reg_contractid_ = "@ov-orange.com/pyIfpmsAlarmRecord;1"
    _reg_desc_ = "Ifpms alarm"

    def __init__(self):
        pass


def wav_del(ipaddr, pid):
    '''删除过期文件'''
    #import time, os ,glob

    wav_path = ifpms.wav_path
    #os.chdir(wav_path)
    #构造文件名
    template = str(ipaddr) + '-' + str(pid) + '*.wav'
    template = os.path.join(wav_path, template)
    #获取文件列表，用glob匹配
    filelist = glob.glob(template)
    #获取N天前的时间
    date = time.localtime(time.time() - (ifpms.wav_days * 24 * 60 * 60))
    filename = str(ipaddr) + '-' + str(pid) + '-' + "%02d%02d%02d-%02d%02d" % (date.tm_year % 100, date.tm_mon, date.tm_mday, date.tm_hour, date.tm_min) + ".wav"
    filename = os.path.join(wav_path, filename)
    for file in filelist:
        if os.path.abspath(file) <= os.path.abspath(filename):
            try:
                logger.info("remove %s ..." % filename)
                os.remove(file)
            except Exception, e:
                logger.exception(e)


class nsIPyIfpmsDCMgmt:
    # XPCOM registration attributes.
    _com_interfaces_ = [components.interfaces.nsIPyIfpmsDCMgmt]
    _reg_clsid_ = "{91a1466e-230e-4f3d-8266-3b064a12528b}"
    _reg_contractid_ = "@ov-orange.com/pyIfpmsDCMgmt;1"
    _reg_desc_ = "Ifpms DC"

    def __init__(self):
        self.dc_list = components.classes["@mozilla.org/array;1"] \
            .createInstance(components.interfaces.nsIMutableArray);

        self.pa_list = components.classes["@mozilla.org/array;1"] \
            .createInstance(components.interfaces.nsIMutableArray);

        self.alarm_history = components.classes["@mozilla.org/array;1"] \
            .createInstance(components.interfaces.nsIMutableArray);

        self._listener = None
        self._listenerProxy = None
        self._serv = None
        self.used_ids = []          # 已使用的编号

        logger.info("nsIPyIfpmsDCMgmt startup...")

    def createDC(self, dc_type, ipaddr, pa_num, did):

        ''' 创建采集器 '''

        retcode = 0

        if ipaddr is None or len(ipaddr) < 7 or ipaddr == "0.0.0.0" or ipaddr == "255.255.255.255":
            return None, -1

        try:
            socket.inet_aton(ipaddr)
            # legal
        except socket.error:
            return None, -1

        #检查是否有同IP或同id的，如果有，则出错
        for i in xrange(0, self.dc_list.length):
            t = self.dc_list.queryElementAt(i, components.interfaces.nsIPyIfpmsDC)
            if t and t.ipaddr == ipaddr and t.product_type == dc_type and dc_type == 0:
                return None, -2

        #分配可用的编号
        if did == 0:
            min_free_id = 1
            if self.used_ids:
                free_ids = [t for t in xrange(1, max(self.used_ids) + 2) if t not in self.used_ids]
                logger.debug("free_ids:%s", free_ids)
                min_free_id = min(free_ids)

            did = min_free_id

        logger.info("create DC-%d %s", did, ipaddr)

        try:
            dc = components.classes["@ov-orange.com/pyIfpmsDC;1"] \
                .createInstance(components.interfaces.nsIPyIfpmsDC)

            dc.pre_init(dc_type, ipaddr, pa_num, did)
            self.dc_list.appendElement(dc, False)
            self.used_ids.append(did)

        except Exception, e:
            logger.exception(e)
            retcode = -1
            dc = None
            pass
        finally:
            if self._serv and dc_type == nsIPyIfpmsDC.Type_Normal:
                self._serv.add_dc(ipaddr, did)
            pass

        if dc:
            for pid in xrange(1, pa_num + 1):
                pa = self.createPA(dc, did, pid)
                if pa:
                    self.pa_list.appendElement(pa, False)
                    dc.pa_list.appendElement(pa, False)
                else:
                    logger.error("create PA:%d-%d failed!", did, ipaddr)

            dc.post_init()

            for i in xrange(0, dc.pa_list.length):
                pa = dc.pa_list.queryElementAt(i, components.interfaces.nsIPyIfpmsPA)
                pa.post_init(dc)
        if dc.pa_num == 4:
            dc.protocol_ver = 3
        return dc, retcode

    def createPA(self, dc, did, pid):

        ''' 创建防区 '''

        logger.info("create PA-%d-%d", did, pid)

        pa_wavpath = ifpms.wav_path + dc.ipaddr + '-' + str(pid) + '/'
        if os.path.isdir(pa_wavpath):
            pass
        else:
            os.mkdir(pa_wavpath)
        #检查是否有同did/pid的，如果有，则返回失败
        try:
            pa = components.classes["@ov-orange.com/pyIfpmsPA;1"] \
                .createInstance(components.interfaces.nsIPyIfpmsPA)
            pa.pre_init(did, pid)

            # wav_del(dc.ipaddr, pid)

        except Exception, e:
            logger.exception(e)
            pa = None
            pass
        finally:
            pass

        return pa

    def getDC(self, did):

        ''' 根据编号取采集器对象 '''

        #logger.info("get DC %d", did)

        for i in xrange(0, self.dc_list.length):
            t = self.dc_list.queryElementAt(i, components.interfaces.nsIPyIfpmsDC)
            if t and t.did == did:
                return t

        return None

    def removeDC(self, did):
        ''' 根据编号删除采集器对象 '''

        dc = None
        dc_idx = None
        dc_ipaddr = None

        for i in xrange(0, self.dc_list.length):
            t = self.dc_list.queryElementAt(i, components.interfaces.nsIPyIfpmsDC)
            if t and t.did == did:
                dc_idx = i
                dc = t
                dc_ipaddr = t.ipaddr
                break

        if dc:
            # remove pa from pa_list
            collector.delCollector(dc)
            found = True
            while found:
                found = False
                pa = None
                for i in xrange(0, self.pa_list.length):
                    t = self.pa_list.queryElementAt(i, components.interfaces.nsIPyIfpmsPA)
                    if t and t.did == did:
                        found = True
                        pa_idx = i
                        pa = t
                        break

                if found:
                    logger.info("remove PA-%d-%d", pa.did, pa.pid)
                    self.pa_list.removeElementAt(pa_idx)
                    del pa

            dc.pa_list.clear()
            
            self.used_ids.remove(did)
            if self._serv and dc.product_type != 4:
                self._serv.remove_dc(dc_ipaddr)

            logger.info("remove DC-%d %s", did, dc.ipaddr)
            self.dc_list.removeElementAt(dc_idx)
            dc.clean()
            del dc


        else:
            logger.error("can not remove a non-existed DC.")

        return

    def getPA(self, did, pid):
        ''' 根据编号取防区对象 '''

        logger.debug("get PA %d %d", did, pid)

        for i in xrange(0, self.pa_list.length):
            t = self.pa_list.queryElementAt(i, components.interfaces.nsIPyIfpmsPA)
            if t and t.did == did and t.pid == pid:
                return t

        return None

    def newAlarm(self, did, pid, alm_type, new_alarm, gui_notify):

        alm_id = 0
        alm_time = 0

        #检查是否有同did/pid的，如果有，则返回失败
        if new_alarm:
            try:
                alarm = components.classes["@ov-orange.com/pyIfpmsAlarmRecord;1"] \
                    .createInstance(components.interfaces.nsIPyIfpmsAlarmRecord)

                alarm.id = 1
                alarm.aid = alm_type
                alarm.did = did
                alarm.pid = pid
               # happentime=time.strftime("%Y-%m-%d %H %M %S");
                alarm.happen_time = time.time()
                alarm.notes = "null"
                alarm.is_confirmed = False
                alarm.confirm_notes = "null"
                alarm.confirm_time = 0
                alarm.confirm_operator = ""
                if self.alarm_history.length > 0:
                    alarm.id = self.alarm_history.queryElementAt((self.alarm_history.length - 1), components.interfaces.nsIPyIfpmsAlarmRecord).id + 1
                # logger.info('alarm.aid=%d',alarm.aid)
                #配置是否往告警列表中写入断开、运行和预警等高频率状态
                # if ifpms.alarm_flag:
                #     self.alarm_history.appendElement(alarm, False)
                # else:
                #     if alarm.aid != 1 and alarm.aid != 2 and alarm.aid != 3: 
                if alarm.aid in ifpms.alarm_list:
                    self.alarm_history.appendElement(alarm, False)
                #保证历史记录的最大长度为ifpms.alarm_history_length
                if self.alarm_history.length == ifpms.alarm_history_length + 1:
                    self.alarm_history.removeElementAt(0)
            except Exception, e:
                logger.exception(e)
                pass
            finally:
                alm_id = alarm.id
                alm_time = alarm.happen_time

        if gui_notify:
            self._listenerProxy.onRaise(did, pid, alm_type, alm_id, alm_time)

    def confirmAlarm(self, id, operator, notes):
        for i in range(self.alarm_history.length):
            alarm = self.alarm_history.queryElementAt(i, components.interfaces.nsIPyIfpmsAlarmRecord)
            if alarm.id == id:
                break
        alarm.confirm_operator = operator
        alarm.confirm_notes = notes
        alarm.confirm_time = time.time()
        alarm.is_confirmed = True
        pass

    def start(self, listener):
        '''启动TCP监听服务'''
        self._port = ifpms.tcp_port

        assert(listener is not None)
        self._listener = listener

        self._listenerProxy = getProxyForObject(1, components.interfaces.nsIPyIfpmsEvent,
                                                self._listener, NS_PROXY_SYNC | NS_PROXY_ALWAYS)

        collector.setProxy(self._listenerProxy)
        collector.setMgmt(self)

        #启动网络服务线程
        logger.info("start serv...")

        WebsHandler.mgmt = self
        WebPush.mgmt = self

        try:
            self._serv = Serv.DcTcpServer(('', self._port), Serv.DcHandler, self._listenerProxy, self)
        except Exception, e:
            logger.exception(e)
        finally:
            pass

        t = threading.Thread(name="Listen Thread 1", target=self._serv.serve_forever)
        t.setDaemon(True)
        t.start()

        if userifpms.webs_enable:
            #启动webservice线程
            try:
                self.webpush = WebPush()
                self._httpd = SocketServer.TCPServer(("", userifpms.webs_port), WebsHandler)
                t3 = threading.Thread(name="Listen Thread 3", target=self._httpd.serve_forever)
                t3.setDaemon(True)
                t3.start()
            except Exception, e:
                logger.exception(e)
            finally:
                pass
        else:
            self.webpush = None

        from remote import RemoteThread 
        RemoteThread.mgmt = self
        if userifpms.remote_enable:
            #启动remote线程
            try:
                self.remoteThread = RemoteThread()
                logger.info("remote startup ok.")
            except Exception, e:
                logger.exception(e)
                self.remoteThread = None
            finally:
                pass
        else:
            self.remoteThread = None

        logger.info("startup ok.")

    def stop(self):
        pass
