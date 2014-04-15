#!/usr/bin/env python
# -*- coding: UTF8 -*-

import logging
import Queue
import time
import math
import pywt
import ipkt

try:
    import thread
    import threading
except ImportError:
    thread = None

import numpy as np

import ifpms
import userifpms
import mark

_lock = None

logger = logging.getLogger(__name__)

# 爆破状态存储
status_blast_normal = {}
status_blast_wav = {}

# 环境自适应探测器全局参数
pa_env = {
    'sid': u'PA-1-1',  # 默认环境自适应探测器对应的sid
    'sensitivity_step': ifpms.sensitivity_step,  # 灵敏度步进值
    'alarm_resistant_factor_step': ifpms.alarm_resistant_factor_step,  # 抗干扰因子的步进值
    'status': {}  # 环境自适应防区的状态存储
}


def _acquireLock():
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    global _lock
    if (not _lock) and thread:
        _lock = threading.RLock()
    if _lock:
        _lock.acquire()


def _releaseLock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    if _lock:
        _lock.release()


def group(seq, size): 
    """
    Returns an iterator over a series of lists of length size from iterable.

        >>> list(group([1,2,3,4], 2))
        [[1, 2], [3, 4]]
        >>> list(group([1,2,3,4,5], 2))
        [[1, 2], [3, 4], [5]]
    """
    def take(seq, n):
        for i in xrange(n):
            yield seq.next()

    if not hasattr(seq, 'next'):  
        seq = iter(seq)
    while True: 
        x = list(take(seq, size))
        if x:
            yield x
        else:
            break





class ErrorNotExisted(Exception):
    pass


class ErrorUnknown(Exception):
    pass

#---------------------------------------------------------------------------
#   Collector classes and functions
#---------------------------------------------------------------------------


class Collector:
    '''
    Collector对象负责数据采集与处理。与DC对象对应。
    '''

    DATA_EXT_SIZE = 11

    DTYPE = np.dtype({
        'names': ['min', 'max', 'freq', 'spread', 'prewarn'] + ['data%d' % n for n in range(0, DATA_EXT_SIZE)],
        'formats': ['i4', 'i4', 'i4', 'i4', 'i4'] + ['i4'] * DATA_EXT_SIZE})
    LOGTIME_DTYPE = np.dtype({
        'names': ['logtime'],
        'formats': ['i8']})

    DSIZE = 4096

    status_name = ['disable', 'disconn', 'connect', 'alarm_minor', 'alarm_critical', 'alarm_fiber_break', 'alarm_blast']

    STATUS_DISABLE = 0
    STATUS_DISCONN = 1
    STATUS_CONNECT = 2
    STATUS_ALARM_MINOR = 3
    STATUS_ALARM_CRITICAL = 4
    STATUS_ALARM_FIBER_BREAK = 5
    STATUS_ALARM_BLAST = 6
    STATUS_LID_OPEN = 7
    STATUS_LID_CLOSE = 8

    ALARM_DELAY_SECS = 5  # 告警状态延迟秒数
    ALARM_REPREAT_INTERVAL_SECS = 2  # 告警持续期间播放声音重复间隔

    SYNC_NONE = 0
    SYNC_READ = 1
    SYNC_WRITE = 2
    SYNC_AUDIO = 3

    """
    """
    def __init__(self, dc):

        self.active_dc(dc)

    def init(self):
        for _id in range(0, self.dc.pa_num):
            if not self.pa[_id]:
                self.pa[_id] = self.dc.getPA(_id + 1)

    def active_dc(self, dc):

        logger.info("active Collector %s" % dc.ipaddr)

        self.active = True
        self.dc = dc
        self.pa = [None] * self.dc.pa_num

        for _id in range(0, self.dc.pa_num):
            if not self.pa[_id]:
                self.pa[_id] = self.dc.getPA(_id + 1)

        self.cmd_queue = Queue.Queue()

        #数据缓冲初始化
        self.data = np.zeros((self.dc.pa_num, Collector.DSIZE), dtype=Collector.DTYPE)
        self.data_logtime = np.zeros((self.dc.pa_num, Collector.DSIZE), dtype=Collector.LOGTIME_DTYPE)
        self.offset = [0] * self.dc.pa_num  # 计数
        self.min = [65535] * self.dc.pa_num  # 最小幅值
        self.max = [2] * self.dc.pa_num  # 最大幅值
        self.spread = [1] * self.dc.pa_num  # 最大幅差
        self.freq = [0] * self.dc.pa_num   # 最大频幅
        self.lastnotifytime = [0] * self.dc.pa_num  # 最近状态变化时间
        self.logtime = [0] * self.dc.pa_num
        self.MU_factor = [0] * self.dc.pa_num
        self.MUchange_offset = [0] * self.dc.pa_num
        self.fiberbreak_history = [ifpms.fiber_k_history] * self.dc.pa_num
        self.blastflag = [0] * self.dc.pa_num  # 爆破判断
        self.range_max = [ifpms.mean_max] * self.dc.pa_num  # 均方周界算法中开启度最大值
        self.range_min = [ifpms.mean_min] * self.dc.pa_num  # 均方周界算法中开启度最小值
        self.range_kq = [ifpms.mean_max - ifpms.mean_min] * self.dc.pa_num  # 开启度范围

    def deactive(self):
        #self.active = False
        while not self.cmd_queue.empty():
            self.cmd_queue.get_nowait()
        #self.dc.clean()

        if self.dc.product_type == 0:
            if self.dc.ipaddr in status_blast_normal:
                status_blast_normal.pop(self.dc.ipaddr)
        elif self.dc.product_type == 4:
            if self.dc.ipaddr in status_blast_wav:
                status_blast_wav.pop(self.dc.ipaddr)

    def sampling(self, pid, dmin, dmax, davg, variance, compression, dfreqs):

        check_point = True

        if self.pa[pid - 1].work_mode == 1:
            dfreq = dfreqs[0] / ifpms.magic
        else:
            dfreq = dfreqs[0]

        if not self.dc:
            return -1

        if pid <= 0 or pid > self.dc.pa_num:
            logger.error("Invaild pid(%d)", pid)
            return -1
        #self.init()
        if not self.pa[pid - 1]:
            logger.error("Invaild pid(%d)", pid)
            return -1

        self.data[pid - 1, :-1] = self.data[pid - 1, 1:]  # 数据前移
        self.data_logtime[pid - 1, :-1] = self.data_logtime[pid - 1, 1:]  # 数据前移
        self.offset[pid - 1] += 1
        self.min[pid - 1] = min(self.min[pid - 1], dmin)
        self.max[pid - 1] = max(self.max[pid - 1], dmax)
        self.spread[pid - 1] = max(self.spread[pid - 1], self.max[pid - 1] - self.min[pid - 1])
        self.data[pid - 1, -1] = (dmin, dmax, dfreq, davg, 0) + (0, ) * Collector.DATA_EXT_SIZE
        self.data_logtime[pid - 1, -1] = (self.logtime[pid - 1],)
        # logger.info('pa work mode %d, Q dc work mode %d' % (self.pa[pid - 1].work_mode, self.dc.Q_workmode))
        if self.pa[pid - 1].work_mode == 4 and self.dc.Q_workmode == 0:
            if ifpms.featureflag:
                # 自适应周界，Q采集器模式
                #取最近ifpms.max_t分钟max的最大值，并且正常情况下max值不应低于500
                t_max = max(np.max(self.data[pid - 1, -5 * 60 * ifpms.max_t:]["max"]), 500)
                #屏蔽光功率绝对值对F的影响
                self.data[pid - 1, -1]['data0'] = t_max
                self.data[pid - 1, -1]['data1'] = self.data[pid - 1, -1]['freq']
                self.data[pid - 1, -1]['freq'] = self.data[pid - 1, -1]['data1'] * 100 / t_max
        elif self.pa[pid - 1].work_mode == 1 and self.dc.Q_workmode == 0:
            # 标准周界，Q独立工作模式
            #取最近2分钟max的最大值，并且正常情况下max值不应低于500
            t_max = max(np.max(self.data[pid - 1, -5 * 60:]["max"]), 500)
            self.data[pid - 1, -1]['data1'] = self.data[pid - 1, -1]['freq']
            self.data[pid - 1, -1]['data5'] = self.data[pid - 1, -1]['data1'] * 100 / t_max  #自适应能力值

            self.data[pid - 1, -1]['data3'] = np.sum(self.data[pid - 1, -ifpms.action_n:]['data1'])
            self.data[pid - 1, -1]['data4'] = np.mean(self.data[pid - 1, -ifpms.background_t2 * 5: -ifpms.background_t1 * 5]['data1'])
            if self.data[pid - 1, -1]['data4'] < self.data[pid - 1, -1]['data3'] / ifpms.b:
                self.data[pid - 1, -1]['data4'] = 0
            self.data[pid - 1, -1]['data0'] =  (self.data[pid - 1, -1]['data3'] + 1) / (self.data[pid - 1, -1]['data4'] + 1)
            self.data[pid - 1, -1]['freq'] = self.data[pid - 1, -1]['data5'] * self.data[pid - 1, -1]['data0'] / (ifpms.k * 150)
        elif self.pa[pid - 1].work_mode == 4 and self.dc.Q_workmode == 1:
            # 自适应周界，Q独立工作模式
            #取最近2分钟max的最大值，并且正常情况下max值不应低于500
            t_max = max(np.max(self.data[pid - 1, -5 * 60:]["max"]), 500)
            #屏蔽光功率绝对值对F的影响
            self.data[pid - 1, -1]['data0'] = t_max
            self.data[pid - 1, -1]['data1'] = self.data[pid - 1, -1]['freq']
            self.data[pid - 1, -1]['freq'] = self.data[pid - 1, -1]['data1'] * 100 / t_max
        elif self.pa[pid - 1].work_mode == 1 and self.dc.Q_workmode == 1:
            # 标准周界，Q独立工作模式
            #取最近2分钟max的最大值，并且正常情况下max值不应低于500
            t_max = max(np.max(self.data[pid - 1, -5 * 60:]["max"]), 500)
            self.data[pid - 1, -1]['data1'] = self.data[pid - 1, -1]['freq']
            self.data[pid - 1, -1]['data5'] = self.data[pid - 1, -1]['data1'] * 100 / t_max  #自适应能力值

            self.data[pid - 1, -1]['data3'] = np.sum(self.data[pid - 1, -ifpms.action_n:]['data1'])
            self.data[pid - 1, -1]['data4'] = np.mean(self.data[pid - 1, -ifpms.background_t2 * 5: -ifpms.background_t1 * 5]['data1'])
            if self.data[pid - 1, -1]['data4'] < self.data[pid - 1, -1]['data3'] / ifpms.b:
                self.data[pid - 1, -1]['data4'] = 0
            self.data[pid - 1, -1]['data0'] =  (self.data[pid - 1, -1]['data3'] + 1) / (self.data[pid - 1, -1]['data4'] + 1)
            self.data[pid - 1, -1]['freq'] = self.data[pid - 1, -1]['data5'] * self.data[pid - 1, -1]['data0'] / (ifpms.k * 150)
        elif self.pa[pid - 1].work_mode == 6 and self.dc.Q_workmode == 0:
            self.range_max[pid - 1] = max(self.data[pid-1, -300:]['max'])
            self.range_min[pid - 1] = min(self.data[pid-1, -300:]['min'])
            self.range_kq[pid - 1] = self.range_max[pid - 1] - self.range_min[pid - 1]
            self.data[pid - 1, -1]['data5'] = self.range_kq[pid - 1]
            spread_mean = np.mean(self.data[pid-1, -ifpms.mean_points:]['spread'])
            if spread_mean > self.range_min[pid - 1] + self.range_kq[pid - 1] / ifpms.mean_magic and spread_mean < self.range_max[pid - 1] - self.range_kq[pid - 1] / ifpms.mean_magic:
            # if abs(spread_mean - self.range_max[pid - 1] + self.range_kq[pid - 1]/2) < 100  and abs(spread_mean - self.range_min[pid - 1] - self.range_kq[pid - 1]/2) < 100:
                self.data[pid - 1, -1]['data1'] = dfreqs[0]
                self.data[pid - 1, -1]['data3'] = dfreqs[1]
                if sum(self.data[pid - 1, -ifpms.mean_points:]['data3']) / sum(self.data[pid - 1, -ifpms.mean_points:]['data1']) >=1:
                    self.data[pid - 1, -1]['data8'] = 10
                else:
                    self.data[pid - 1, -1]['data8'] = -10                
                self.data[pid - 1, -1]['freq'] = pow(spread_mean, 2) / sum([(self.data[pid - 1, -(i + 1)]['spread'] - spread_mean)**2 for i in xrange(ifpms.mean_points)])
                self.data[pid - 1, -1]['freq'] = self.data[pid - 1, -1]['freq'] / ifpms.magic
                if self.data[pid - 1, -1]['freq'] > 0 and (np.mean(self.data[pid-1, -ifpms.mean_points:]['max']) - np.mean(self.data[pid-1, -ifpms.mean_points:]['min'])) < self.range_kq[pid - 1] / ifpms.mean_range_magic:
                    self.data[pid - 1, -1]['freq'] = 0
            else:
                self.data[pid - 1, -1]['freq'] = 0
        elif self.pa[pid - 1].work_mode == 6 and self.dc.Q_workmode == 1:
            self.data[pid - 1, -1]['freq'] = variance
            self.data[pid - 1, -1]['data1'] = dfreqs[0]
            self.data[pid - 1, -1]['data3'] = dfreqs[1]
            if compression == 1:
                self.data[pid - 1, -1]['data8'] = -10
            else:
                self.data[pid - 1, -1]['data8'] = compression
        # logger.info("MU_factor=%d",self.pa[pid - 1].sensitivity)

        if self.MU_factor[pid - 1] != self.pa[pid - 1].sensitivity:
            self.MUchange_offset[pid - 1] = 10
        else:
            if self.MUchange_offset[pid - 1] > 0:
                self.MUchange_offset[pid - 1] -= 1

        # logger.info("MUchange_offset=%d",self.MUchange_offset[pid - 1])
        pa_ref = self.pa[pid - 1]
        current_hour = time.localtime().tm_hour
        if pa_ref.enable_start < pa_ref.enable_end and (pa_ref.enable_start > current_hour or pa_ref.enable_end <= current_hour):  # do not process data
            tiemenable = True
        elif pa_ref.enable_start > pa_ref.enable_end and current_hour >= pa_ref.enable_end and current_hour < pa_ref.enable_start:
            tiemenable = True
        else:
            tiemenable = False

        if not self.pa[pid - 1].enable or tiemenable:
            status = Collector.STATUS_DISABLE
        elif self.offset[pid - 1] > 10 and self.MUchange_offset[pid - 1] == 0:
            if self.pa[pid - 1].status != Collector.STATUS_DISCONN:
                status = self.pa[pid - 1].status
            else:
                status = Collector.STATUS_CONNECT

            bool_fiber_break = self.fiberbreak(pid)

            if bool_fiber_break:
                status = Collector.STATUS_ALARM_FIBER_BREAK
                self.data[pid - 1, -1]['freq'] = 0
                self.data[pid - 1, -1]['data7'] = self.data[pid - 1, -2]['data7']
            elif self.pa[pid - 1].work_mode == 1 or self.pa[pid - 1].work_mode == 4:
                if self.data[pid - 1, -1]['freq'] < 0:
                    self.data[pid - 1, -1]['freq'] = 0
                status = self.check_MZ_optimize(pid, status)
            elif self.pa[pid - 1].work_mode == 6:
                status = self.check_MZ_Mean(pid, status)
            elif self.pa[pid - 1].work_mode == 2:
                #风雨探测
                status = self.environment_detect(pid, status)
            elif self.pa[pid - 1].work_mode == 3:
                #wenbo
                status, check_point = self.check_wenbo(pid, status)
            elif self.pa[pid - 1].work_mode == 5:
                #wenbo_upgrade
                # self.data[pid - 1, -1]['data3'] = dfreqs[1]
                status, check_point = self.check_wenbo_upgrade_new(pid, status)
        else:
            status = Collector.STATUS_CONNECT
            self.data[pid - 1, -1]['freq'] = 0
            self.data[pid - 1, -1]['data7'] = self.data[pid - 1, -2]['data7']

        # logger.info("History_MU_factor=%d",self.MU_factor[pid-1])
        self.MU_factor[pid - 1] = self.pa[pid - 1].sensitivity

        if check_point:
            self.changeStatus(pid, status)

    # 断纤判断算法
    def fiberbreak(self, pid):
        if self.dc.protocol_ver == 2:
            #2.0硬件断纤检查条件
            t_davg = np.sum(self.data[pid - 1, -ifpms.break_time * 5:]["spread"])
            bool_fiber_break = t_davg < ifpms.break_time * ifpms.fiber_break_threshold_avg * 5
        else:
            #1.0硬件断纤检查条件
            t_davg = np.sum(self.data[pid - 1, -ifpms.break_time * 5:]["spread"])
            bool_fiber_break = t_davg < ifpms.break_time * ifpms.fiber_break_threshold_avg * 5

        if bool_fiber_break:
            k_before = max(self.data[pid - 1, -(ifpms.davg_time + 1) * 5:-ifpms.davg_time * 5]["spread"])
            k = (k_before + 1) / (self.data[pid - 1, -1]["spread"] + 1)
            k1 = (self.fiberbreak_history[pid - 1] + 1) / (self.data[pid - 1, -1]["spread"] + 1)
            self.data[pid - 1, -1]["data9"] = k1
            if k > ifpms.fiber_k:
                self.fiberbreak_history[pid - 1] = k_before
            if np.mean(self.data[pid - 1, -5:]["data9"]) < ifpms.fiber_k:
                bool_fiber_break = False
            elif self.pa[pid - 1].sid in ifpms.fiber_pa:
                bool_fiber_break = False
        return bool_fiber_break

    def changeSystemStatus(self, status):
        logger.info("collector lid status changed....staus%d" % status)
        if self.manager.mgmt:
            self.manager.mgmt.newAlarm(self.dc.did, 1, status, True, True)

    def changeStatus(self, pid, status):

        if not self.dc:
            return

        if pid <= 0 or pid > self.dc.pa_num:
            logger.error("Invaild pid(%d)", pid)
            return -1

        self.init()

        if not self.pa[pid - 1]:
            logger.error("Invaild pid(%d)", pid)
            return -1

        # 比当前告警级别更严重的告警，其状态应保持一定时间以引起关注
        if hasattr(userifpms, "alarm_delay_secs"):
            delay_secs = userifpms.alarm_delay_secs
        else:
            delay_secs = Collector.ALARM_DELAY_SECS

        if status != self.pa[pid - 1].status:

            if status != Collector.STATUS_DISCONN \
                and status < self.pa[pid - 1].status \
                and int(time.time()) - self.pa[pid - 1].latest_change_time < delay_secs:
                    status = self.pa[pid - 1].status

        #状态变化
        if status != self.pa[pid - 1].status:
            logger.warn("%s-%d status changed!(%s to %s)", self.dc.sid, pid, Collector.status_name[self.pa[pid - 1].status], Collector.status_name[status])
            self.pa[pid - 1].status = status
            self.pa[pid - 1].latest_change_time = int(time.time())
            self.lastnotifytime[pid - 1] = int(time.time())

            if self.manager.mgmt:
                self.manager.mgmt.newAlarm(self.dc.did, pid, status, True, True)
                if self.manager.mgmt.webpush:
                    self.manager.mgmt.webpush.push(self.pa[pid - 1].did, pid, self.pa[pid - 1].sid, self.pa[pid - 1].status, self.pa[pid - 1].latest_change_time)

                if self.manager.mgmt.remoteThread:
                    self.manager.mgmt.remoteThread.push(self.pa[pid - 1].did, pid, self.pa[pid - 1].sid, self.pa[pid - 1].status, self.pa[pid - 1].latest_change_time)

            self.cmd_queue.put_nowait((ipkt.SET_SWITCH_CTRL_REQ, pid))
            if userifpms.gsm_flag and self.dc.Q_workmode ==0 and status in userifpms.gsm_status:
                self.cmd_queue.put_nowait((ipkt.SET_GSM_CTRL_REQ, pid))

        elif (self.pa[pid - 1].status == Collector.STATUS_ALARM_CRITICAL or self.pa[pid - 1].status == Collector.STATUS_ALARM_BLAST) \
            and int(time.time()) - self.lastnotifytime[pid - 1] > Collector.ALARM_REPREAT_INTERVAL_SECS \
            and int(time.time()) - self.pa[pid - 1].latest_change_time < delay_secs:
            #告警持续期内，循环播放声音
            if self.manager.mgmt:
                self.manager.mgmt.newAlarm(self.dc.did, pid, status, False, True)
                self.lastnotifytime[pid - 1] = int(time.time())
        elif self.pa[pid - 1].status == Collector.STATUS_ALARM_MINOR:
            if self.manager.mgmt:
                self.manager.mgmt.newAlarm(self.dc.did, pid, status, False, True)

    def raw_sampling(self, pid, raw_data):

        """原始样本采集入口"""

        if not self.dc:
            return -1

        if pid <= 0 or pid > self.dc.pa_num:
            logger.error("Invaild pid(%d)", pid)
            return -1

        if not self.pa[pid - 1]:
            logger.error("Invaild PA(pid=%d)", pid)
            return -1

        #获得防区 启用时间段 决定是否继续处理数据
        #logger.info("check pa  enable time ... did : %d, pid%d "%(self.dc.did,pid))

        pa_ref = self.pa[pid - 1]

        if pa_ref.process_mode == 3 and self.dc.product_type == 0:  # 混合模式时不处理原始样本，避免重复处理
            return 0

        #是否进行小波滤波处理
        if ifpms.checkend == True:
            raw_data=self.wavelet_smooth(raw_data, 'coif3', ifpms.smooth_level)
        else:
            pass

        #窗口模式选择
        raw_data_len = len(raw_data)

        dmin = min(raw_data)
        dmax = max(raw_data)

        fft_data = np.fft.fft(raw_data)

        #频点的物理意义
        fft = np.abs(fft_data[0:raw_data_len / 2]) / (raw_data_len / 2)
        fft[0] = fft[0] / 2  # 基频仅需除以FFT_SIZE

        if mark.logo == "default":
            for n in xrange(0,len(fft)):
                # if n+1 > 1: #去掉基频
                self.data[pid-1, -1 * 1024 / 2 + n]['prewarn'] = fft[n]
                # else:
                #     self.data[pid-1, -1 * 1024 / 2 + n]['prewarn'] = 1024
        # 计算窗口相交部分，多窗口
        win_setting = ifpms.fft_window_settings[self.pa[pid - 1].work_mode]
        freq_val = []
        for n in xrange(0, len(win_setting)):
            dfreq = 0
            if win_setting[n]["noise"] == 0:
                dfreq = np.sum(fft[win_setting[n]["begin"] - 1:win_setting[n]["end"]])
            else:
                #取相交部分
                tfft = np.array(fft[win_setting[n]["begin"] - 1:win_setting[n]["end"]]) - win_setting[n]["noise"]
                #计算和
                dfreq = np.sum(tfft[tfft > 0]) / win_setting[n]["magic"]

            freq_val.append(dfreq)
        davg = np.mean(raw_data)

        if self.pa[pid - 1].work_mode == 3:
            x = list(group(raw_data, ifpms.grain))
            gx = [(max(item) + 1) / (min(item) + 1) for item in x]
            gxx = [i for i in gx if i >=2]
            s = np.sum(gx) - 1024 / ifpms.grain - ifpms.basement
            if s >= 0:
                self.data[pid - 1, -1]['data0'] = s
            else:
                self.data[pid - 1, -1]['data0'] = 0
        elif self.pa[pid - 1].work_mode == 4 and not ifpms.featureflag:
            x = list(group(raw_data, ifpms.grain))
            gx = [(max(item) + 1) / (min(item) + 1) for item in x]
            gxx = [i for i in gx if i >=2]
            s = np.sum(gx) - 1024 / ifpms.grain - ifpms.basement
            if s >= 0:
                self.data[pid - 1, -1]['freq'] = s
            else:
                self.data[pid - 1, -1]['freq'] = 0

        self.sampling(pid, dmin, dmax, davg, 0, 0 ,freq_val)

    def environment_detect(self, pid, status_orig):
        status = status_orig

        # 无效的防区号
        if pid <= 0 or pid > self.dc.pa_num:
            logger.error("Invaild pid(%d)", pid)
            return status
        #根据灵敏设置取回参数
        #瞬间时段和参考时段，两个时段的采样报文包数
        alarm_resp_time = self.pa[pid - 1].alarm_resp_time or 2
        INSTANT_PERIOD_NUM = int(alarm_resp_time * 5)
        THRESHOLD_FREQ_TIME = self.pa[pid - 1].alarm_resistant_factor or 1
        THRESHOLD_FREQ = self.pa[pid - 1].alarm_sensitivity or 1

        #有效采样点达到可计算条件，瞬间时段和参考时段均采集到有效数据
        if self.offset[pid - 1] > INSTANT_PERIOD_NUM:
            period_ins_freq_overrange_num = np.sum(np.greater(self.data[pid - 1, -1 * INSTANT_PERIOD_NUM:]['freq'], THRESHOLD_FREQ))

            #瞬间频值达到频值门限的次数达到次数门限
            if period_ins_freq_overrange_num >= THRESHOLD_FREQ_TIME:
                status = Collector.STATUS_ALARM_CRITICAL
                self.data[pid - 1, -1]['data6'] = 6
            else:
                status = Collector.STATUS_CONNECT
                self.data[pid - 1, -1]['data6'] = -6

        else:
            #采样数量未达到计算条件
            pass

        return status

    def wavelet_smooth(self, x, wavelet, lev):
        '''
        小波滤波
        x-原始数据
        lev分解层数
        主要是对细节系数进行处理，可以置零，可以倍数下降等具体可以改下面相应代码
        '''
        xd = np.zeros(len(x))
        coeffs = pywt.wavedec(x, wavelet, level=lev)
        if ifpms.smooth_A:
            coeffs[0] = np.zeros(len(coeffs[0]))
        if ifpms.smooth_DL != 0:
            for i in range(ifpms.smooth_DL):
                coeffs[i + 1] = np.zeros(len(coeffs[i + 1]))
        if ifpms.smooth_DH != 0:
            for i in range(ifpms.smooth_DH):
                coeffs[lev - i] = np.zeros(len(coeffs[lev - i]))
        xd = pywt.waverec(coeffs, wavelet)
        return xd

    # 工作模式选择文博优化
    def check_wenbo_upgrade_new(self, pid, status_orig):

        status = status_orig
        check_point = False  # 文博模式只会在特定时间点进行检查，该标志标记了检查点
        daynight = 0
        # 无效的防区号
        if pid <= 0 or pid > self.dc.pa_num:
            logger.error("Invaild pid(%d)", pid)
            return status

        #sensitivity = self.pa[pid-1].sensitivity % 5
        if time.localtime()[3] in range(ifpms.wb_settings['Daytime'][0], ifpms.wb_settings['Daytime'][1] + 1):  # 7点至20点为白天
            daynight = 0
        else:
            daynight = 1
            # 每秒采样点数
        pkt_num_pre_sec = 5

        THRESHOLD_FREQ_RATIO = self.pa[pid - 1].alarm_resistant_factor_gsd or 80
        THRESHOLD_FREQ = self.pa[pid - 1].alarm_sensitivity or 40

        S_NUM = int(ifpms.wb_settings['SRange'][daynight] * pkt_num_pre_sec)
        L_NUM = int(ifpms.wb_settings['LRange'][daynight] * pkt_num_pre_sec)

        if self.data[pid - 1, -1]['freq'] != 0 and self.data[pid - 1, -2]['freq'] != 0 and self.offset[pid - 1] > S_NUM:
            self.data[pid - 1, -1]['data0'] = 10 * self.data[pid - 1, -1]['freq'] / np.mean(self.data[pid - 1]['freq'][-S_NUM:])
            # self.data[pid - 1, -1]['data1'] = 10 * self.data[pid - 1, -1]['data3'] / np.mean(self.data[pid-1]['data3'][-S_NUM:])

        alarm_blast_flag = self.blast_check(pid)

        if alarm_blast_flag and self.blastflag[pid - 1]:
            status = Collector.STATUS_ALARM_BLAST
            self.data[pid - 1, -1]['data7'] = self.data[pid - 1, -2]['data7']
            check_point = True
        else:
            if self.offset[pid - 1] % S_NUM == 0:  # 达到检查点，按时间分段，计算每小段的告警状态，小段告警为轻微告警

                check_point = True

                if np.sum(np.greater(self.data[pid - 1, -1 * S_NUM:]['data0'], THRESHOLD_FREQ)) == 0:
                    self.data[pid - 1, -1]['data6'] = -10
                    status = Collector.STATUS_CONNECT
                else:
                    self.data[pid - 1, -1]['data6'] = 10
                    if ifpms.alarm_minor_flag:
                        status = Collector.STATUS_ALARM_MINOR
                    else:
                        status = Collector.STATUS_CONNECT

                n3 = np.sum(np.greater(self.data[pid - 1, -1 * L_NUM:]['data6'], 0))
                #n3 = np.sum(np.greater(self.data[pid-1,-1*L_NUM:]['data2'],0))
                self.data[pid - 1, -1]['data7'] = n3 * 100 / (L_NUM / S_NUM)

                if n3 * 100 / (L_NUM / S_NUM) >= THRESHOLD_FREQ_RATIO:
                    logger.info("critical alarm: %d > %d", n3 * 100 / (L_NUM / S_NUM), THRESHOLD_FREQ_RATIO)
                    status = Collector.STATUS_ALARM_CRITICAL
            else:
                self.data[pid - 1, -1]['data6'] = 0
                self.data[pid - 1, -1]['data7'] = self.data[pid - 1, -2]['data7']

        return status, check_point

    def blast_check_dict(self):
        blast_status = []
        for ip, collector in self.manager.collectorDict.items():
            for i in xrange(collector.dc.pa_num):
                if ip in ifpms.Blasting_P and ifpms.Blasting_enable:
                    flag0 = max(collector.data[i, -5:]['freq']) > ifpms.Blasting_p[ip][i][0]
                    flag1 = max(collector.data[i, -5:]['data0']) > ifpms.Blasting_p[ip][i][1]
                elif ifpms.Blasting_enable is False:
                        flag0 = max(collector.data[i, -5:]['freq']) > userifpms.blast_freq
                        flag1 = max(collector.data[i, -5:]['data0']) > userifpms.blast_data0
                else:
                    flag0 = False
                    flag1 = False
                flag = flag0 and flag1
                blast_status.append(flag)

        if sum(blast_status) >= userifpms.blast_num:
            alarm_blast_flag = True
        else:
            alarm_blast_flag = False
        return alarm_blast_flag

    def blast_check(self, pid):

        ip = self.dc.ipaddr
        if ip in ifpms.Blasting_P and ifpms.Blasting_enable:
            flag0 = max(self.data[pid - 1, -5:]['freq']) > ifpms.Blasting_p[ip][pid - 1][0]
            flag1 = max(self.data[pid - 1, -5:]['data0']) > ifpms.Blasting_p[ip][pid - 1][1]
        elif ifpms.Blasting_enable is False:
                flag0 = max(self.data[pid - 1, -5:]['freq']) > userifpms.blast_freq
                flag1 = max(self.data[pid - 1, -5:]['data0']) > userifpms.blast_data0
        else:
            flag0 = False
            flag1 = False
        flag = flag0 and flag1
        self.blastflag[pid - 1] = int(flag)
        if self.dc.product_type == 0:
            status_blast_normal.update({ip: self.blastflag})
            lsstatus = []
            for value in status_blast_normal.values():
                lsstatus.extend(value)
            if sum(lsstatus) >= userifpms.blast_num:
                logger.info('normal blastflag%s' % repr(status_blast_normal))
                alarm_blast_flag = True
            else:
                alarm_blast_flag = False
            return alarm_blast_flag

        elif self.dc.product_type == 4:
            status_blast_wav.update({ip: self.blastflag})
            # logger.info('wav blastflag%s' % repr(status_blast_wav))
            lsstatus = []
            for value in status_blast_wav.values():
                lsstatus.extend(value)
            if sum(lsstatus) >= userifpms.blast_num:
                logger.info('wav blastflag%s' % repr(status_blast_wav))
                alarm_blast_flag = True
            else:
                alarm_blast_flag = False
            return alarm_blast_flag

    #工作模式选择文博
    def check_wenbo(self, pid, status_orig):

        status = status_orig
        check_point = False  # 文博模式只会在特定时间点进行检查，该标志标记了检查点
        daynight = 0
        # 无效的防区号
        if pid <= 0 or pid > self.dc.pa_num:
            logger.error("Invaild pid(%d)", pid)
            return status

        #sensitivity = self.pa[pid-1].sensitivity % 5
        if time.localtime()[3] in range(ifpms.wb_settings['Daytime'][0], ifpms.wb_settings['Daytime'][1] + 1):  # 7点至20点为白天
            daynight = 0
        else:
            daynight = 1
            # 每秒采样点数
        pkt_num_pre_sec = 5

        THRESHOLD_FREQ_RATIO = self.pa[pid - 1].alarm_resistant_factor_gsd or 80
        THRESHOLD_FREQ = self.pa[pid - 1].alarm_sensitivity or 40

        S_NUM = int(ifpms.wb_settings['SRange'][daynight] * pkt_num_pre_sec)
        L_NUM = int(ifpms.wb_settings['LRange'][daynight] * pkt_num_pre_sec)

        # if self.data[pid - 1, -1]['freq'] != 0 and self.data[pid - 1, -2]['freq'] != 0 and self.offset[pid - 1] > S_NUM:
        #     self.data[pid - 1, -1]['data0'] = 10 * self.data[pid - 1, -1]['freq'] / np.mean(self.data[pid - 1]['freq'][-S_NUM:])
            # self.data[pid - 1, -1]['data1'] = 10 * self.data[pid - 1, -1]['data3'] / np.mean(self.data[pid-1]['data3'][-S_NUM:])

        alarm_blast_flag = self.blast_check(pid)

        if alarm_blast_flag and self.blastflag[pid - 1]:
            status = Collector.STATUS_ALARM_BLAST
            self.data[pid - 1, -1]['data7'] = self.data[pid - 1, -2]['data7']
            check_point = True
        else:
            if self.offset[pid - 1] % S_NUM == 0:  # 达到检查点，按时间分段，计算每小段的告警状态，小段告警为轻微告警

                check_point = True

                if np.sum(np.greater(self.data[pid - 1, -1 * S_NUM:]['data0'], THRESHOLD_FREQ)) == 0:
                    self.data[pid - 1, -1]['data6'] = -10
                    status = Collector.STATUS_CONNECT
                else:
                    self.data[pid - 1, -1]['data6'] = 10
                    if ifpms.alarm_minor_flag:
                        status = Collector.STATUS_ALARM_MINOR
                    else:
                        status = Collector.STATUS_CONNECT

                n3 = np.sum(np.greater(self.data[pid - 1, -1 * L_NUM:]['data6'], 0))
                #n3 = np.sum(np.greater(self.data[pid-1,-1*L_NUM:]['data2'],0))
                self.data[pid - 1, -1]['data7'] = n3 * 100 / (L_NUM / S_NUM)

                if n3 * 100 / (L_NUM / S_NUM) >= THRESHOLD_FREQ_RATIO:
                    logger.info("critical alarm: %d > %d", n3 * 100 / (L_NUM / S_NUM), THRESHOLD_FREQ_RATIO)
                    status = Collector.STATUS_ALARM_CRITICAL
            else:
                self.data[pid - 1, -1]['data6'] = 0
                self.data[pid - 1, -1]['data7'] = self.data[pid - 1, -2]['data7']

        return status, check_point

    #工作模式选择check_MZ_optimize
    def check_MZ_optimize(self, pid, status_orig):
        status = status_orig

        # 无效的防区号
        if pid <= 0 or pid > self.dc.pa_num:
            logger.error("Invaild pid(%d)", pid)
            return status
        #根据灵敏设置取回参数
        #瞬间时段和参考时段，两个时段的采样报文包数

        alarm_resp_time = self.pa[pid - 1].alarm_resp_time or 2
        INSTANT_PERIOD_NUM = int(alarm_resp_time * 5)
        THRESHOLD_FREQ_TIME = self.pa[pid - 1].alarm_resistant_factor or 1
        THRESHOLD_FREQ = self.pa[pid - 1].alarm_sensitivity or 1

        if ifpms.environment_detect_flag:
            if self.pa[pid - 1].sid == pa_env['sid']:
                pa_env['status'].update({self.pa[pid - 1].sid: status})
            else:
                if pa_env['sid'] in pa_env['status']:
                    if pa_env['status'][pa_env['sid']] == Collector.STATUS_ALARM_CRITICAL:
                        THRESHOLD_FREQ_TIME = self.pa[pid - 1].alarm_resistant_factor + pa_env['alarm_resistant_factor_step']
                        THRESHOLD_FREQ = self.pa[pid - 1].alarm_sensitivity + pa_env['sensitivity_step']

        #有效采样点达到可计算条件，瞬间时段和参考时段均采集到有效数据
        if self.offset[pid - 1] > INSTANT_PERIOD_NUM:
            period_ins_freq_overrange_num = np.sum(np.greater(self.data[pid - 1, -1 * INSTANT_PERIOD_NUM:]['freq'], THRESHOLD_FREQ))
            self.data[pid - 1, -1]['data2'] = period_ins_freq_overrange_num

            #瞬间频值达到频值门限的次数达到次数门限
            if period_ins_freq_overrange_num >= THRESHOLD_FREQ_TIME:
                status = Collector.STATUS_ALARM_CRITICAL
                self.data[pid - 1, -1]['data6'] = 6
            else:
                status = Collector.STATUS_CONNECT
                self.data[pid - 1, -1]['data6'] = -6

        else:
            #采样数量未达到计算条件
            pass

        return status

    #均方周界算法
    def check_MZ_Mean(self, pid, status_orig):
        status = status_orig

        # 无效的防区号
        if pid <= 0 or pid > self.dc.pa_num:
            logger.error("Invaild pid(%d)", pid)
            return status
        #根据灵敏设置取回参数
        #瞬间时段和参考时段，两个时段的采样报文包数
        alarm_resp_time = self.pa[pid - 1].alarm_resp_time or 2
        INSTANT_PERIOD_NUM = int(alarm_resp_time * 5)
        THRESHOLD_FREQ_TIME = self.pa[pid - 1].alarm_resistant_factor or 1
        THRESHOLD_FREQ = self.pa[pid - 1].alarm_sensitivity or 1

        if ifpms.environment_detect_flag:
            if self.pa[pid - 1].sid == pa_env['sid']:
                pa_env['status'].update({self.pa[pid - 1].sid: status})
            else:
                if pa_env['sid'] in pa_env['status']:
                    if pa_env['status'][pa_env['sid']] == Collector.STATUS_ALARM_CRITICAL:
                        THRESHOLD_FREQ_TIME = self.pa[pid - 1].alarm_resistant_factor + pa_env['alarm_resistant_factor_step']
                        THRESHOLD_FREQ = self.pa[pid - 1].alarm_sensitivity + pa_env['sensitivity_step']

        mean_flag = False
        period_ins_num = np.sum(np.greater(self.data[pid - 1, -1 * INSTANT_PERIOD_NUM:]['data8'], 5))
        if period_ins_num >= 5:  # data8必须至少持续1s（5个点）为10才认定为扰动导致
            mean_flag = True
        else:
            mean_flag = False

        #有效采样点达到可计算条件，瞬间时段和参考时段均采集到有效数据
        if self.offset[pid - 1] > INSTANT_PERIOD_NUM:
            period_ins_freq_overrange_num = np.sum(np.greater(self.data[pid - 1, -1 * INSTANT_PERIOD_NUM:]['freq'], THRESHOLD_FREQ))
            #瞬间频值达到频值门限的次数达到次数门限

            if period_ins_freq_overrange_num >= THRESHOLD_FREQ_TIME and mean_flag:
                status = Collector.STATUS_ALARM_CRITICAL
                self.data[pid - 1, -1]['data6'] = 6
            else:
                status = Collector.STATUS_CONNECT
                self.data[pid - 1, -1]['data6'] = -6

        else:
            #采样数量未达到计算条件
            pass

        return status

    def getSampling(self, type, pid, offset):

        #return offset+1, [offset+100,2,3]

        if pid <= 0 or pid > self.dc.pa_num:
            return 0, [], []

        begin = -1

        if offset < 0:
            begin = offset - 1
        else:
            if offset >= self.offset[pid - 1]:
                return self.offset[pid - 1], [], []
            else:
                begin = offset - self.offset[pid - 1]

        sampling_data = self.data[pid - 1, begin:][type]

        return self.offset[pid - 1], list(sampling_data), list(self.data_logtime[pid - 1, begin:]['logtime'])

    def getSamplingBasic(self, pid, offset):

        if pid <= 0 or pid > self.dc.pa_num:
            return 0, None, None, None

        begin = -1

        if offset < 0:
            begin = offset - 1
        else:
            if offset >= self.offset[pid - 1]:
                return self.offset[pid - 1], []
            else:
                begin = offset - self.offset[pid - 1]

        return self.offset[pid - 1], list(self.data[pid - 1, begin:]['min']), \
            list(self.data[pid - 1, begin:]['max']), \
            list(self.data[pid - 1, begin:]['freq']), \
            list(self.data[pid - 1, begin:]['spread']), \
            list(self.data[pid - 1, begin:]['prewarn']),\
            list(self.data_logtime[pid - 1, begin:]['logtime'])

    def getSamplingAll(self, pid, offset):

        if pid <= 0 or pid > self.dc.pa_num:
            return 0, None, None, None

        begin = -1

        if offset < 0:
            begin = offset - 1
        else:
            if offset >= self.offset[pid - 1]:
                return self.offset[pid - 1], []
            else:
                begin = offset - self.offset[pid - 1]

        return self.offset[pid - 1],\
            list(self.data[pid - 1, begin:]['min']), \
            list(self.data[pid - 1, begin:]['max']), \
            list(self.data[pid - 1, begin:]['freq']), \
            list(self.data[pid - 1, begin:]['spread']), \
            list(self.data[pid - 1, begin:]['prewarn']), \
            list(self.data[pid - 1, begin:]['data0']), \
            list(self.data[pid - 1, begin:]['data1']), \
            list(self.data[pid - 1, begin:]['data2']), \
            list(self.data[pid - 1, begin:]['data3']), \
            list(self.data[pid - 1, begin:]['data4']), \
            list(self.data[pid - 1, begin:]['data5']), \
            list(self.data[pid - 1, begin:]['data6']), \
            list(self.data[pid - 1, begin:]['data7']), \
            list(self.data[pid - 1, begin:]['data8']), \
            list(self.data[pid - 1, begin:]['data9']),\
            list(self.data_logtime[pid - 1, begin:]['logtime'])


class Manager:

    def __init__(self):
        """
        Initialize the manager.
        """
        self.collectorDict = {}
        self.proxy = None

    def newCollector(self, dc):
        rv = None
        _acquireLock()

        if dc.product_type == 0:
            dict_key = dc.ipaddr
        else:
            dict_key = dc.did

        try:
            if dict_key in self.collectorDict:
                rv = self.collectorDict[dict_key]
                rv.active_dc(dc)
            else:
                # create if not existed
                rv = Collector(dc)
                rv.manager = self
                self.collectorDict[dict_key] = rv
        finally:
            _releaseLock()
        return rv

    def delCollector(self, dc):
        rv = None
        _acquireLock()

        if dc.product_type == 0:
            dict_key = dc.ipaddr
        else:
            dict_key = dc.did

        try:
            if dict_key in self.collectorDict:
                rv = self.collectorDict[dict_key]
                rv.deactive()
                del self.collectorDict[dict_key]
        finally:
            _releaseLock()
        return

    def getCollectorByKey(self, key):
        rv = None
        _acquireLock()
        try:
            if key in self.collectorDict:
                rv = self.collectorDict[key]
            else:
                pass
        finally:
            _releaseLock()

        if not rv:
            raise ErrorNotExisted('%s not existed' % (str(key)))

        return rv

    # def getCollectorByIP(self, ipaddr):
    #     rv = None
    #     _acquireLock()
    #     try:
    #         if self.collectorDict.has_key(ipaddr):
    #             rv = self.collectorDict[ipaddr]
    #         else:
    #             pass
    #     finally:
    #         _releaseLock()
    #     return rv

    # def delCollectorByDid(self,did):
    #     if self.collectorDict.has_key(did):
    #         del self.collectorDict[did]

    def getCollectorByDid(self, did):
        rv = None
        _acquireLock()
        try:
            for i in self.collectorDict:
                if self.collectorDict[i].dc:
                    if self.collectorDict[i].dc.did == did:
                        rv = self.collectorDict[i]
        finally:
            _releaseLock()
        return rv

    def setProxy(self, proxy):
        self.proxy = proxy

    def setMgmt(self, mgmt):
        self.mgmt = mgmt


def newCollector(dc):
    if dc:
        return Collector.manager.newCollector(dc)
    else:
        raise ErrorUnknown('miss parameter')


def delCollector(dc):
    if dc:
        return Collector.manager.delCollector(dc)
    else:
        raise ErrorUnknown('miss parameter')


def getCollectorByKey(key):
    return Collector.manager.getCollectorByKey(key)


def getCollectorByDid(did):
    return Collector.manager.getCollectorByDid(did)


def setProxy(proxy):
    Collector.manager.setProxy(proxy)


def setMgmt(mgmt):
    Collector.manager.setMgmt(mgmt)


Collector.manager = Manager()
