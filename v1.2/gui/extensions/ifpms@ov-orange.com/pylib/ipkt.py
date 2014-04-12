#!/usr/bin/env python
# -*- coding: UTF8 -*-

# UDP-based app level communication protocol
import struct
import dpkt
import datetime
import logging


logger = logging.getLogger(__name__)

#command id
GET_BASE_INFO_REQ = 0x01
GET_BASE_INFO_RSP = 0x11
GET_COMM_INFO_REQ = 0x02
GET_COMM_INFO_RSP = 0x12
SET_COMM_INFO_REQ = 0x03
SET_COMM_INFO_RSP = 0x13
GET_SAMPLING_CTRL_REQ = 0x04
GET_SAMPLING_CTRL_RSP = 0x14
SET_SAMPLING_CTRL_REQ = 0x05
SET_SAMPLING_CTRL_RSP = 0x15
GET_CHANNEL_CTRL_REQ = 0x06
GET_CHANNEL_CTRL_RSP = 0x16
SET_CHANNEL_CTRL_REQ = 0x07
SET_CHANNEL_CTRL_RSP = 0x17

#查询设备功能控制信息
GET_DEVICE_FUNCTION_REQ = 0x08
GET_DEVICE_FUNCTION_RSP = 0x18

#设置设备功能控制信息
SET_DEVICE_FUNCTION_REQ = 0x09
SET_DEVICE_FUNCTION_RSP = 0x19


SET_SWITCH_CTRL_REQ = 0x0a
SET_SWITCH_CTRL_RSP = 0x1a
SET_RESTORE_REQ = 0x0b
SET_RESTORE_RSP = 0x1b
SET_REBOOT_REQ = 0x0c
SET_REBOOT_RSP = 0x1c
SET_SAVE_CFG_REQ = 0x0d
SET_SAVE_CFG_RSP = 0x1d
SET_UPGRADE_REQ = 0x0e
SET_UPGRADE_RSP = 0x1e

NOTIFY_PREPARE_SIMPLING_DATA = 0x21
NOTIFY_RAW_DATA = 0x22

NOTIFY_SYS_FAIL = 0x31
NOTIFY_CHANNEL_FAIL = 0x32
NOTIFY_SYS_FAIL_RECOVERY = 0x33
NOTIFY_CHANNEL_FAIL_RECOVERY = 0x34


class ErrorUnknownType(Exception):
    pass


class Header(dpkt.Packet):
    length = 6
    __hdr__ = (
        ('length', 'H', 0xffff),
        ('cmd', 'B', 0xff),
        ('ret', 'B', 0xff),
        ('channel', 'B', 0xff),
        ('seq', 'B', 0xff)
    )


class Empty(dpkt.Packet):
    __hdr__ = ()


class BaseInfo(dpkt.Packet):
    __hdr__ = (
        ('mac', '6s', '\xff\xff\xff\xff\xff\xff'),
        ('hwid', '6s', '\xff\xff\xff\xff\xff\xff'),
        ('hwcode', '2s', '\xff\xff'),
        ('hw_version', '2s', '\xff\xff'),
        ('sw_version', '2s', '\xff\xff'),
        ('sw_revision', 'H', 0xffff),
        ('proto_version', 'B', 0xff),
        ('proto_mode', 'B', 0xff),
        ('channel_num', 'B', 0xff),
        ('config_version', '2s', '\xff\xff'),
        ('boot_version', '2s', '\xff\xff'),
        ('ip_num', 'B', 0xff),
        ('machine_id', 'B', 0xff),
        ('slot_id', 'B', 0xff)
        )


class BaseInfo_v1(dpkt.Packet):
    __hdr__ = (
        ('mac', '6s', '\xff\xff\xff\xff\xff\xff'),
        ('hwid', '6s', '\xff\xff\xff\xff\xff\xff'),
        ('hwcode', '2s', '\xff\xff'),
        ('hw_version', '2s', '\xff\xff'),
        ('sw_version', '2s', '\xff\xff'),
        ('sw_revision', 'H', 0xffff),
        ('proto_version', 'B', 0xff),
        ('proto_mode', 'B', 0xff),
        ('channel_num', 'B', 0xff)
        )


class CommInfo(dpkt.Packet):
    __hdr__ = (
        ('ip_mode', 'B', 0xff),
        ('ipaddr', '4s', '\xff\xff\xff\xff'),
        ('netmask', '4s', '\xff\xff\xff\xff'),
        ('gateway', '4s', '\xff\xff\xff\xff'),
        ('mgmt_ipaddr', '4s', '\xff\xff\xff\xff'),
        ('mgmt_port', 'H', 0xffff),
        ('syslog_ipaddr', '4s', '\xff\xff\xff\xff'),
        ('syslog_port', 'H', 0xffff),
        ('syslog_priority', 'B', 0xff),
        ('log_priority', 'B', 0xff),
        ('mode', 'B', 0xff),
        ('pass', '3s', '\xff' * 3)
        )


class SamplingCtrl(dpkt.Packet):
    __hdr__ = (
        ('freq', 'B', 0xff),
        ('fft_size', 'B', 0xff)
        )


class ChannelCtrl(dpkt.Packet):
    __hdr__ = (
        ('enable', 'B', 0xff),
        ('mu_factor', 'H', 0xffff),
        ('mode', 'B', 0xff),
        ('pre_process_mode', 'B', 0xff),
        ('photoelectron_value', 'L', 0xffffffff),
        ('win_size', 'B', 0xff)
        )

    def unpack(self, buf):
        dpkt.Packet.unpack(self, buf)
        self.win = []
        for n in xrange(self.win_size):
            self.win.append(self.WinSetting(self.data[n * 6:]))
        self.data = self.win

    def __len__(self):

        if isinstance(self.data, list):
            l = self.__hdr_len__
            for n in xrange(len(self.data)):
                l = l + len(self.data[n])
            return l
        else:
            return self.__hdr_len__ + len(self.data)

    def __repr__(self):
        l = ['%s=%r' % (k, getattr(self, k))
              for k in self.__hdr_defaults__
              if getattr(self, k) != self.__hdr_defaults__[k]]
        if self.data:
            if isinstance(self.data, list):
                ll = [repr(k) for k in self.data]
                l.append('data=[%s]' % ', '.join(ll))
            else:
                l.append('data=%r' % self.data)
        return '%s(%s)' % (self.__class__.__name__, ', '.join(l))

    def __str__(self):

        if isinstance(self.data, list):
            b = self.pack_hdr()
            for n in xrange(len(self.data)):
                b = b + str(self.data[n])
            return b
        else:
            return self.pack_hdr() + str(self.data)

    class WinSetting(dpkt.Packet):
        __hdr__ = (
            ('begin', 'H', 0xffff),
            ('end', 'H', 0xffff),
            ('noise', 'H', 0xffff)
            )

        def unpack(self, buf):
            dpkt.Packet.unpack(self, buf)
            self.data = None

#Q系列通道控制信息
class ChannelCtrl_v3(dpkt.Packet):
    __hdr__ = (
        ('enable', 'B', 1),
        ('mu_factor', 'H', 16128),
        ('mode', 'B', 2),
        ('pre_process_mode', 'B', 1),
        ('photoelectron_value', 'L', 0xffffffff),
        ('win_size', 'B', 8),
        # ('windows', '%ss' % 3 * 8, Window().pack() * 8),
        # damn it!
        ('begin1', 'H', 2),
        ('end1', 'H', 30),
        ('noise1', 'H', 15),
        ('begin2', 'H', 2),
        ('end2', 'H', 30),
        ('noise2', 'H', 15),
        ('begin3', 'H', 0),
        ('end3', 'H', 0),
        ('noise3', 'H', 0),
        ('begin4', 'H', 0),
        ('end4', 'H', 0),
        ('noise4', 'H', 0),
        ('begin5', 'H', 0),
        ('end5', 'H', 0),
        ('noise5', 'H', 0),
        ('begin6', 'H', 0),
        ('end6', 'H', 0),
        ('noise6', 'H', 0),
        ('begin7', 'H', 0),
        ('end7', 'H', 0),
        ('noise7', 'H', 0),
        ('begin8', 'H', 0),
        ('end8', 'H', 0),
        ('noise8', 'H', 0),
        ('defence_start', 'B', 0),  # 0-23
        ('defence_end', 'B', 0),  # 0-23
        ('work_mode', 'B', 0),  # 标准周界和自适应周界
        ('sensitivity', 'H', 80),  # 灵敏度
        ('response_time', 'B', 3),  # 响应时间
        ('noise_immunity', 'B', 2)  # 抗干扰度
    )
    def set_windows_Q(self, windows, work_mode):
        # 下位机标准周界对应第一个窗口，自适应对应第二个窗口
        if work_mode == 0 or work_mode == 2:
            setattr(self, 'begin2', windows[0]['begin'])
            setattr(self, 'end2', windows[0]['end'])
            setattr(self, 'noise2', windows[0]['noise'])
        if work_mode == 1:
            setattr(self, 'begin1', windows[0]['begin'])
            setattr(self, 'end1', windows[0]['end'])
            setattr(self, 'noise1', windows[0]['noise'])
        if work_mode == 3: #下位机低频窗口noise由0变成5，高频窗口noise由0变成1，高频窗口
            setattr(self, 'begin3', windows[0]['begin'])
            setattr(self, 'end3', windows[0]['end'])
            setattr(self, 'noise3', windows[0]['noise'] + 5)
            setattr(self, 'begin4', windows[1]['begin'])
            setattr(self, 'end4', windows[1]['end'] + 1)
            setattr(self, 'noise4', windows[1]['noise'])

    def set_windows(self, windows):
        for i, w in enumerate(windows):
            setattr(self, 'begin%s' % (i + 1), w['begin'])
            setattr(self, 'end%s' % (i + 1), w['end'])
            setattr(self, 'noise%s' % (i + 1), w['noise'])
        self.win_size = len(windows)

    def get_windows(self):
        windows = []
        for i in xrange(1, self.win_size + 1):
            windows.append({
                'begin': getattr(self, 'begin%d' % i),
                'end': getattr(self, 'end%d' % i),
                'noise': getattr(self, 'noise%d' % i)
            })
        return windows

class ChannelCtrl_v1(dpkt.Packet):
    __hdr__ = (
        ('enable', 'B', 0xff),
        ('mu_factor', 'B', 0xff),
        ('mode', 'B', 0xff),
        ('begin', 'H', 0xffff),
        ('end', 'H', 0xffff),
        ('noise', 'H', 0xffff)
        )


class PrepareSimplingData(dpkt.Packet):
    __hdr__ = (
        ('max', 'H', 0xff),
        ('min', 'H', 0xff),
        ('avg', 'H', 0xff),
        ('variance', 'H', 0xff),  #方差特征值
        ('compression', 'H', 0xff), # 压缩特征值，由高频与低频比较得到
        ('reserve6', 'H', 0xff),
        ('reserve7', 'H', 0xff),
        ('reserve8', 'H', 0xff)
        )

    def unpack(self, buf):
        dpkt.Packet.unpack(self, buf)
        self.freq = []
        for n in xrange(len(self.data) / 4):
            self.freq.append(struct.unpack_from(">L", self.data[n * 4:])[0])
        self.data = self.freq

    def __len__(self):

        if isinstance(self.data, list):
            l = self.__hdr_len__
            for n in xrange(len(self.data)):
                l = l + len(self.data[n])
            return l
        else:
            return self.__hdr_len__ + len(self.data)

    def __repr__(self):
        l = ['%s=%r' % (k, getattr(self, k))
              for k in self.__hdr_defaults__
              if getattr(self, k) != self.__hdr_defaults__[k]]
        if self.data:
            if isinstance(self.data, list):
                ll = [repr(k) for k in self.data]
                l.append('data=[%s]' % ', '.join(ll))
            else:
                l.append('data=%r' % self.data)
        return '%s(%s)' % (self.__class__.__name__, ', '.join(l))

    def __str__(self):

        if isinstance(self.data, list):
            b = self.pack_hdr()
            for n in xrange(len(self.data)):
                b = b + str(self.data[n])
            return b
        else:
            return self.pack_hdr() + str(self.data)


class SwitchCtrl(dpkt.Packet):
    __hdr__ = (
        ('relay', 'B', 0xff),
        ('led', 'B', 0xff),
        ('mixer', 'B', 0xff)
        )


class RawData(dpkt.Packet):
    __hdr__ = (
        )


#设备功能控制
class DeviceFunction(dpkt.Packet):
    __hdr__ = (
        ('year', 'H', 2012),  # 2012-2049
        ('month', 'B', 9),  # 1-12
        ('day', 'B', 1),  # 1-31
        ('hour', 'B', 0),  # 0-23
        ('minute', 'B', 0),  # 0-59
        ('second', 'B', 0),  # 0-59
        ('relay_duration', 'H', 5),  # 继电器输出持续时间(second) 0-3600
        ('activated_phone_count', 'B', 8),  # 有效的手机号码个数 0-8
        # 八个手机号码位
        # ('cellphones', '%ss' % (1 + 11) * 8, 0),
        # damn it!
        ('phone_mode1', 'B', 1),
        ('phone1', '11s', '0' * 11),
        ('phone_mode2', 'B', 1),
        ('phone2', '11s', '0' * 11),
        ('phone_mode3', 'B', 1),
        ('phone3', '11s', '0' * 11),
        ('phone_mode4', 'B', 1),
        ('phone4', '11s', '0' * 11),
        ('phone_mode5', 'B', 1),
        ('phone5', '11s', '0' * 11),
        ('phone_mode6', 'B', 1),
        ('phone6', '11s', '0' * 11),
        ('phone_mode7', 'B', 1),
        ('phone7', '11s', '0' * 11),
        ('phone_mode8', 'B', 1),
        ('phone8', '11s', '0' * 11),
        # 中文名称unicode编码字符串长度, 最大值MAX=16(中文字数) * 4=64
        ('pa_name_len1', 'B', 12),
        # 中文转unicode编码字符串 4个字符/一个汉字
        ('pa_name1', '65s', '9632533a0031'),
        ('pa_name_len2', 'B', 12),
        ('pa_name2', '65s', '9632533a0032'),
        ('pa_name_len3', 'B', 12),
        ('pa_name3', '65s', '9632533a0033'),
        ('pa_name_len4', 'B', 12),
        ('pa_name4', '65s', '9632533a0034'),
    )

    def get_pa_name(self, ch):
        name = u''
        for i in range(getattr(self, 'pa_name_len%s' % ch) / 4):
            four_bytes = getattr(self, 'pa_name%s' % ch)[0 + i * 4:4 * (i + 1)]
            name += unichr(int(four_bytes, 16))
        return name

    def set_pa_name(self, name, ch):
        uni_len = len(name)
        assert uni_len * 4 < 64
        name = unicode(name)
        pa_name = ''.join(['%04x' % ord(uc) for uc in name])
        setattr(self, 'pa_name%s' % ch, pa_name)
        setattr(self, 'pa_name_len%s' % ch, uni_len * 4)

    def set_cellphones(self, phones):
        for i, p in enumerate(phones):
            setattr(self, 'phone_mode%s' % (i + 1), p['mode'])
            setattr(self, 'phone%s' % (i + 1), str(p['number']))
        # self.activated_phone_count = len(phones)

    def get_cellphones(self):
        phones = []
        for i in range(1, self.activated_phone_count):
            phones.append({
                'mode': getattr(self, 'phone_mode%s' % i),
                'number': getattr(self, 'phone%s' % i)
            })
        return phones

    def pack_hdr(self):
        if not self.year:
            d = datetime.datetime.now()
            for k in ('year', 'month', 'day', 'hour', 'minute', 'second'):
                setattr(self, k, getattr(d, k))
        return super(DeviceFunction, self).pack_hdr()


bodys = [{
    GET_BASE_INFO_REQ: Empty,
    GET_BASE_INFO_RSP: BaseInfo_v1,
    GET_CHANNEL_CTRL_REQ: Empty,
    GET_CHANNEL_CTRL_RSP: ChannelCtrl_v1,
    SET_CHANNEL_CTRL_REQ: ChannelCtrl_v1,
    SET_CHANNEL_CTRL_RSP: Empty,
    SET_SWITCH_CTRL_REQ: SwitchCtrl,
    SET_SWITCH_CTRL_RSP: Empty,
    NOTIFY_PREPARE_SIMPLING_DATA: PrepareSimplingData,
    NOTIFY_RAW_DATA: RawData,
    NOTIFY_SYS_FAIL: Empty,
    NOTIFY_CHANNEL_FAIL: Empty,
    NOTIFY_SYS_FAIL_RECOVERY: Empty,
    NOTIFY_CHANNEL_FAIL_RECOVERY: Empty
    }, {
    GET_BASE_INFO_REQ: Empty,
    GET_BASE_INFO_RSP: BaseInfo,
    GET_COMM_INFO_REQ: Empty,
    GET_COMM_INFO_RSP: CommInfo,
    SET_COMM_INFO_REQ: CommInfo,
    SET_COMM_INFO_RSP: Empty,
    GET_SAMPLING_CTRL_REQ: Empty,
    GET_SAMPLING_CTRL_RSP: SamplingCtrl,
    SET_SAMPLING_CTRL_REQ: SamplingCtrl,
    SET_SAMPLING_CTRL_RSP: Empty,
    GET_CHANNEL_CTRL_REQ: Empty,
    GET_CHANNEL_CTRL_RSP: ChannelCtrl,
    SET_CHANNEL_CTRL_REQ: ChannelCtrl,
    SET_CHANNEL_CTRL_RSP: Empty,
    SET_SWITCH_CTRL_REQ: SwitchCtrl,
    SET_SWITCH_CTRL_RSP: Empty,
    SET_RESTORE_REQ: Empty,
    SET_RESTORE_RSP: Empty,
    SET_REBOOT_REQ: Empty,
    SET_REBOOT_RSP: Empty,
    SET_SAVE_CFG_REQ: Empty,
    SET_SAVE_CFG_RSP: Empty,
    SET_UPGRADE_REQ: Empty,
    SET_UPGRADE_RSP: Empty,
    NOTIFY_PREPARE_SIMPLING_DATA: PrepareSimplingData,
    NOTIFY_RAW_DATA: RawData,
    NOTIFY_SYS_FAIL: Empty,
    NOTIFY_CHANNEL_FAIL: Empty,
    NOTIFY_SYS_FAIL_RECOVERY: Empty,
    NOTIFY_CHANNEL_FAIL_RECOVERY: Empty
    },
    {
    GET_BASE_INFO_REQ: Empty,
    GET_BASE_INFO_RSP: BaseInfo,
    GET_COMM_INFO_REQ: Empty,
    GET_COMM_INFO_RSP: CommInfo,
    SET_COMM_INFO_REQ: CommInfo,
    SET_COMM_INFO_RSP: Empty,
    GET_SAMPLING_CTRL_REQ: Empty,
    GET_SAMPLING_CTRL_RSP: SamplingCtrl,
    SET_SAMPLING_CTRL_REQ: SamplingCtrl,
    SET_SAMPLING_CTRL_RSP: Empty,
    GET_CHANNEL_CTRL_REQ: Empty,
    GET_CHANNEL_CTRL_RSP: ChannelCtrl_v3,
    SET_CHANNEL_CTRL_REQ: ChannelCtrl_v3,
    SET_CHANNEL_CTRL_RSP: Empty,
    SET_SWITCH_CTRL_REQ: SwitchCtrl,
    SET_SWITCH_CTRL_RSP: Empty,
    GET_DEVICE_FUNCTION_REQ:Empty,
    GET_DEVICE_FUNCTION_RSP:DeviceFunction,
    SET_DEVICE_FUNCTION_REQ:DeviceFunction,
    SET_DEVICE_FUNCTION_RSP:Empty,
    SET_RESTORE_REQ: Empty,
    SET_RESTORE_RSP: Empty,
    SET_REBOOT_REQ: Empty,
    SET_REBOOT_RSP: Empty,
    SET_SAVE_CFG_REQ: Empty,
    SET_SAVE_CFG_RSP: Empty,
    SET_UPGRADE_REQ: Empty,
    SET_UPGRADE_RSP: Empty,
    NOTIFY_PREPARE_SIMPLING_DATA: PrepareSimplingData,
    NOTIFY_RAW_DATA: RawData,
    NOTIFY_SYS_FAIL: Empty,
    NOTIFY_CHANNEL_FAIL: Empty,
    NOTIFY_SYS_FAIL_RECOVERY: Empty,
    NOTIFY_CHANNEL_FAIL_RECOVERY: Empty
    }
]


def unpack(buf, ver=2):

    header = None
    body = None

    if ver < 1 or ver > 3:
        raise ErrorUnknownType("unknown version %d" % ver)

    header = Header(buf[:Header.length])

    if header.cmd in bodys[ver - 1]:
        if bodys[ver - 1][header.cmd]:
            body = bodys[ver - 1][header.cmd](buf[Header.length:])
        else:
            body = buf[Header.length:]
    else:
        raise ErrorUnknownType("unknown packet type 0x%x" % header.cmd)

    return (header, body)
