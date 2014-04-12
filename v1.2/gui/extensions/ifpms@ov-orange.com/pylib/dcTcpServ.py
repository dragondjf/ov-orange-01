#!/usr/bin/env python
# -*- coding: UTF8 -*-

import time
import SocketServer
import socket
import Queue
import logging
import os
import struct
import wave
import math

import collector
import ifpms
import ipkt
import iudp

logger = logging.root
plogger = logging.getLogger("packet")

TIMEOUT = 5  # TCP连接接收超时
iplist = []  # zzh debug


class ErrorPacket(Exception):
    pass


class ErrorConnect(Exception):
    pass


class ErrorConnectClose(Exception):
    pass


class ErrorHead(Exception):
    pass


class DcHandler(SocketServer.BaseRequestHandler):

    HEAD_SIZE = 6

    def setup(self):

        logger.warn("%s is connected!" % self.client_address[0])
        pa_num = collector.getCollectorByKey(self.client_address[0]).dc.pa_num
        logger.warn("pa number of per dc:%d" % pa_num)
        self.raw_data = [[]] * pa_num
        self.wav_file = [None] * pa_num  # 音频文件
        self.wav_timestamp = [0] * pa_num  # 音频时间
        iplist.append(self.client_address[0])  # zzh debug
        self.break_type = 0  # 断开类型判断，0表示常断，1表示瞬间断开

        #clear queue
        try:
            self.collector = collector.getCollectorByKey(self.client_address[0])
            while not self.collector.cmd_queue.empty():
                self.collector.cmd_queue.get_nowait()
        except Exception, e:
            logger.exception(e)

        try:
            self.request.settimeout(TIMEOUT)

            if self.collector.dc.protocol_ver == 2:
                self.collector.changeStatus(1, collector.Collector.STATUS_CONNECT)
                self.collector.changeStatus(2, collector.Collector.STATUS_CONNECT)

                self.collector.cmd_queue.put_nowait((ipkt.GET_BASE_INFO_REQ, 0))
                self.collector.cmd_queue.put_nowait((ipkt.SET_CHANNEL_CTRL_REQ, 1))
                self.collector.cmd_queue.put_nowait((ipkt.SET_CHANNEL_CTRL_REQ, 2))
                self.collector.cmd_queue.put_nowait((ipkt.SET_SWITCH_CTRL_REQ, 1))
                self.collector.cmd_queue.put_nowait((ipkt.SET_SWITCH_CTRL_REQ, 2))
            elif self.collector.dc.protocol_ver == 3:
                self.collector.changeStatus(1, collector.Collector.STATUS_CONNECT)
                self.collector.changeStatus(2, collector.Collector.STATUS_CONNECT)
                self.collector.changeStatus(3, collector.Collector.STATUS_CONNECT)
                self.collector.changeStatus(4, collector.Collector.STATUS_CONNECT)

                self.collector.cmd_queue.put_nowait((ipkt.GET_BASE_INFO_REQ, 0))
                self.collector.cmd_queue.put_nowait((ipkt.SET_CHANNEL_CTRL_REQ, 1))
                self.collector.cmd_queue.put_nowait((ipkt.SET_CHANNEL_CTRL_REQ, 2))
                self.collector.cmd_queue.put_nowait((ipkt.SET_CHANNEL_CTRL_REQ, 3))
                self.collector.cmd_queue.put_nowait((ipkt.SET_CHANNEL_CTRL_REQ, 4))
                self.collector.cmd_queue.put_nowait((ipkt.SET_SWITCH_CTRL_REQ, 1))
                self.collector.cmd_queue.put_nowait((ipkt.SET_SWITCH_CTRL_REQ, 2))
                self.collector.cmd_queue.put_nowait((ipkt.SET_SWITCH_CTRL_REQ, 3))
                self.collector.cmd_queue.put_nowait((ipkt.SET_SWITCH_CTRL_REQ, 4))
        except Exception, e:
            logger.exception(e)

    def handle(self):
        if not self.collector:
            logger.warn("no collector!")
            return

        while self.collector.active:

            try:
                self.dc_set()
                self.tcp_deal()
            except ErrorConnectClose, e:
                logger.exception(e)
                self.break_type = 1
                break
            except ErrorPacket, e:
                logger.exception(e)
                self.break_type = 1
                break
            except ErrorHead, e:
                logger.exception(e)
                self.break_type = 1
                break
            except Exception, e:
                logger.exception(e)
                self.break_type = 0
                break

    def dc_set(self):

        """异步命令处理，从队列中取出命令，打包发出"""

        channel_id = 0
        body = None

        try:
            cmd_id, channel_id = self.collector.cmd_queue.get_nowait()
        except Queue.Empty:
            return

        header = ipkt.Header(cmd=cmd_id, channel=channel_id, ret=0, seq=0)

        if cmd_id == ipkt.GET_BASE_INFO_REQ:
            body = ipkt.Empty()
        elif cmd_id == ipkt.SET_CHANNEL_CTRL_REQ:  # 设置通道参数
            if self.collector.dc.protocol_ver == 2:
                win_setting = ifpms.fft_window_settings[self.collector.pa[channel_id - 1].work_mode]
                win_data = []
                for n in xrange(0, len(win_setting)):
                    win_data.append(
                        ipkt.ChannelCtrl.WinSetting( \
                            begin=win_setting[n]['begin'], \
                            end=win_setting[n]['end'], \
                            noise=win_setting[n]['noise']), \
                    )
                body = ipkt.ChannelCtrl( \
                    enable=1, \
                    mu_factor=self.sensitivitycompound(self.collector.pa[channel_id - 1].sensitivity), \
                    mode=self.collector.pa[channel_id - 1].process_mode, \
                    pre_process_mode=1,
                    win_size=len(win_data), \
                    data=win_data)
            elif self.collector.dc.protocol_ver == 3:
                if self.collector.dc.Q_workmode == 0:
                    body = ipkt.ChannelCtrl_v3( \
                        enable=1, \
                        mu_factor=self.sensitivitycompound(self.collector.pa[channel_id - 1].sensitivity), \
                        mode=self.collector.pa[channel_id - 1].process_mode, \
                        pre_process_mode=1,
                        )
                    win_setting = ifpms.fft_window_settings[self.collector.pa[channel_id - 1].work_mode]
                    body.set_windows(win_setting)
            else:
                mu_factor = self.collector.pa[channel_id - 1].sensitivity
                if mu_factor >= 255:
                    mu_factor = 254

                body = ipkt.ChannelCtrl_v1( \
                    enable=1, \
                    mu_factor=mu_factor, \
                    mode=255, \
                    begin=5, \
                    end=100, \
                    noise=25 \
                    )
        elif cmd_id == ipkt.SET_SWITCH_CTRL_REQ:  # 设置开关量

            if self.collector.pa[channel_id - 1].status in [collector.Collector.STATUS_ALARM_CRITICAL, collector.Collector.STATUS_ALARM_BLAST]:
                beep = 1
            else:
                beep = 0

            body = ipkt.SwitchCtrl( \
                relay=beep, \
                led=beep, \
                mixer=int(self.collector.pa[channel_id - 1].audio_enable))

        else:
            pass

        try:
            if (self.collector.dc.protocol_ver == 2 or self.collector.dc.protocol_ver == 3) and self.collector.dc.Q_workmode == 0:
                sess = iudp.Session(self.client_address[0], ifpms.udp_port)
                rsp = sess.deal(header=header, body=body, protocol_ver=self.collector.dc.protocol_ver)
                self.pkt_handle(rsp[0], rsp[1])
            else:
                self.tcp_send(header=header, body=body)

        except Exception, e:
            logger.exception(e)

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

    def tcp_send(self, header, body=None):

        body_str = ''

        if body:
            body_str = str(body)
            header.length = len(body_str)
        else:
            header.length = 0

        sendbuf = str(header) + body_str

        logger.info(repr((header, body)))
        plogger.debug("Send|" + " ".join(['%02x' % ord(o) for o in sendbuf]), extra={"ip": self.client_address[0]})

        try:
            self.request.send(sendbuf)
        except Exception, e:
            logger.exception(e)
            raise ErrorConnect('transmit failed!')

    def tcp_deal(self):

        """接收并处理一个完整的TCP应用层报文"""

        recv_head = None
        recv_body = None
        body_len = 0
        cid = 0

        try:
            #接收包头
            recv_head = ""#zzh debug
            while len(recv_head) < self.HEAD_SIZE:
                recv_t = self.request.recv(self.HEAD_SIZE - len(recv_head))
                if not recv_t:
                    raise ErrorHead("can not recv head:" + str(recv_head))
                else:
                    recv_head = recv_head + recv_t
            if not recv_head or len(recv_head) == 0:
                raise ErrorConnectClose(self.client_address[0] + "connection is close.")
            elif len(recv_head) != DcHandler.HEAD_SIZE:
                logger.info(repr(recv_head))
                logger.info(len(recv_head))
                raise ErrorPacket("invalid head length.")
            else:
                body_len, cid = struct.unpack_from(">HB", recv_head)
                recv_body = ""

                if body_len > 4096:
                    raise ErrorConnect("recv head error:%d" % (body_len))
                elif body_len > 0:

                    #接收包体
                    while len(recv_body) < body_len:
                        recv_t = self.request.recv(body_len - len(recv_body))

                        if not recv_t:
                            raise ErrorConnect("can not recv body:" + str(recv_t))
                        else:
                            recv_body = recv_body + recv_t

                    #检查包完整性
                    if len(recv_body) != body_len:
                        raise ErrorConnect("recv body error! recv_len is %d" % len(recv_body))
                else:
                    recv_body = ""

                if ifpms.raw_settings['enable_pkt_log']:
                    if cid != 0x22:  # 22为原始报文，只记波形
                        plogger.debug("Recv|" + " ".join(['%02x' % ord(o) for o in recv_head + recv_body]), extra={"ip": self.client_address[0]})

            # 解析报文
            header, body = ipkt.unpack(recv_head + recv_body, ver=self.collector.dc.protocol_ver)

            self.pkt_handle(header, body)

        except socket.timeout:
            raise ErrorConnect("tcp timeout: " + str(self.client_address[0]))

        except ipkt.ErrorUnknownType, e:
            logger.warn(e)

        return

    def pkt_handle(self, header, body):

        if header.cmd == ipkt.GET_BASE_INFO_RSP:
            logger.info("recv packet from " + self.client_address[0] + ": " + repr((header, body)))
            self.collector.dc.mac = ":".join(["%02x" % ord(t) for t in body.mac])
            #self.collector.dc.protocol_ver = body.proto_version
            self.collector.dc.hw_version = "v" + ".".join(["%d" % ord(t) for t in body.hw_version])
            self.collector.dc.sw_version = "v" + ".".join(["%d" % ord(t) for t in body.sw_version]) + '-r' + str(body.sw_revision)
            if self.collector.dc.protocol_ver == 2:
                self.proto_mode = body.proto_mode
                self.ip_num = body.ip_num
                self.channel_num = body.channel_num
                self.collector.dc.slot_id = body.slot_id
                self.collector.dc.machine_id = body.machine_id
        elif header.cmd == ipkt.NOTIFY_PREPARE_SIMPLING_DATA:
            self.collector.sampling(header.channel, body.min, body.max, body.avg, body.variance,body.compression, body.data)
        elif header.cmd == ipkt.NOTIFY_RAW_DATA:
            FFT_SIZE = 1024
            data_size = len(body.data) / 2
            t_raw_data = list(struct.unpack_from('>' + 'H' * data_size, body.data))
            if len(self.raw_data[header.channel - 1]) + len(t_raw_data) >= FFT_SIZE:
                self.collector.raw_sampling(header.channel, self.raw_data[header.channel - 1] + t_raw_data)
                self.raw_data[header.channel - 1] = []
            else:
                self.raw_data[header.channel - 1] = t_raw_data

            self.wav_dump(header.channel, t_raw_data)

        elif header.cmd == ipkt.NOTIFY_SYS_FAIL:
            logger.info("recv packet from " + self.client_address[0] + ": " + repr((header, body)))
            if header.ret == 0x04:
                self.collector.changeSystemStatus(collector.Collector.STATUS_LID_OPEN)
        elif header.cmd == ipkt.NOTIFY_SYS_FAIL_RECOVERY:
            logger.info("recv packet from " + self.client_address[0] + ": " + repr((header, body)))
            if header.ret == 0x04:
                self.collector.changeSystemStatus(collector.Collector.STATUS_LID_CLOSE)
        else:
            logger.warn("ignore packet from " + self.client_address[0] + ": " + repr((header, body)))
            pass

    def wav_dump(self, channel_id, data):

        "原始报文以分钟为间隔存为wav音频"

        if channel_id > len(self.wav_file):
            return

        current_timestamp = int(time.time())

        if self.wav_timestamp[channel_id - 1] / 60 != current_timestamp / 60:
            if self.wav_file[channel_id - 1]:
                self.wav_file[channel_id - 1].close()
                self.wav_file[channel_id - 1] = None
            else:
                pass
        else:
            pass

        "文件未打开，则打开音频文件"
        wav_path = ifpms.wav_path + self.collector.dc.ipaddr + "-" + str(channel_id) + '/'
        if not self.wav_file[channel_id - 1]:
            self.wav_timestamp[channel_id - 1] = current_timestamp
            ts = time.localtime(current_timestamp)
            ts_filename = wav_path + self.collector.dc.ipaddr + "-" + str(channel_id) + "-" \
                + "%02d%02d%02d-%02d%02d" % (ts.tm_year % 100, ts.tm_mon, ts.tm_mday, ts.tm_hour, ts.tm_min) + ".wav"
            self.wav_file[channel_id - 1] = wave.open(ts_filename, 'w')

            #几个参数的含义分别为 1-单通道，2-2字节即16位的采样精度，5120的采样率
            self.wav_file[channel_id - 1].setparams((1, 2, 5120, 0, 'NONE', 'not compressed'))
            tmp_timestamp = current_timestamp - (ifpms.wav_days * 24 * 60 * 60)  # 删除N天前的wav
            tmp = time.localtime(tmp_timestamp)
            tmp_filename = wav_path + self.collector.dc.ipaddr + "-" + str(channel_id) + "-" + "%02d%02d%02d-%02d%02d" % (tmp.tm_year % 100, tmp.tm_mon, tmp.tm_mday, tmp.tm_hour, tmp.tm_min) + ".wav"
            try:
                os.remove(tmp_filename)
            except:
                pass
        if self.wav_file[channel_id - 1] != None:
            #转字节序，12位采样精度放大到16位采样精度，所以乘以16（2^4）。将采样值从0~2^32调整到-2^31 ~ 2^31，所以减32768。

            wave_data = [d * 16 - 32768 for d in data]
            packed_data = ""
            for d in wave_data:
                packed_data = packed_data + struct.pack('h', d)
            self.wav_file[channel_id - 1].writeframes(packed_data)

    def finish(self):
        iplist.remove(self.client_address[0])#zzh debug
        #logger.warn("def finish :%s is disconnected! the iplist is %s" % self.client_address[0], str(iplist)
        try:
            #logger.warn("%s is disconnected!"%self.client_address[0])
            if self.break_type == 0:
                if self.collector.dc.protocol_ver == 2:
                    self.collector.changeStatus(1, collector.Collector.STATUS_DISCONN)
                    self.collector.changeStatus(2, collector.Collector.STATUS_DISCONN)
                elif self.collector.dc.protocol_ver == 3:
                    self.collector.changeStatus(1, collector.Collector.STATUS_DISCONN)
                    self.collector.changeStatus(2, collector.Collector.STATUS_DISCONN)
                    self.collector.changeStatus(3, collector.Collector.STATUS_DISCONN)
                    self.collector.changeStatus(4, collector.Collector.STATUS_DISCONN)
            elif self.break_type == 1:
                pass
            self.collector.deactive()

            for n in range(0, len(self.wav_file)):
                if self.wav_file[n]:
                    self.wav_file[n].close()

        except Exception, e:
            logger.exception(e)


class DcTcpServer(SocketServer.ThreadingTCPServer):
    def __init__(self, server_address, RequestHandlerClass, proxy, mgmt, port=6001):
        self._ips = {}
        self._dids = {}
        self._socks = {}
        self._proxy = proxy
        self._mgmt = mgmt
        SocketServer.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass)

    def verify_request(self, request, client_address):
        #zzh debug
        if client_address[0] in iplist:
            logger.info("DC  deny %s %s ", client_address, "False the Threading ALREADY EXISTS ")
            return False
        else:
            if client_address[0] in self._ips:  # and self._ips[client_address[0]] == 0:
                self._ips[client_address[0]] = self._ips[client_address[0]] + 1
                self._socks[id(request)] = client_address[0]
                logger.info("allow %s", client_address)
                return True
            else:
                logger.info("deny %s", client_address)
                #logger.info("ips.haskey(%s)=%s, num=%d"%(client_address[0],self._ips.has_key(client_address[0]),self._ips[client_address[0]]))
                return False

    def close_request(self, request):
        if id(request) in self._socks:
            client_addr = self._socks[id(request)]
            logger.info("close_request(%s) ", client_addr)
            del self._socks[id(request)]
            if client_addr in self._ips:
                self._ips[client_addr] = self._ips[client_addr] - 1

    def add_dc(self, ipaddr, sid):
        logger.info("add ipaddr: " + ipaddr)
        if ipaddr not in self._ips:
            self._ips[ipaddr] = 0

        self._dids[ipaddr] = sid

    def remove_dc(self, ipaddr):
        logger.info("remove out ipaddr: " + ipaddr)
        if ipaddr in self._ips:
            del self._ips[ipaddr]

        if ipaddr in iplist:
            iplist.remove(ipaddr)

        if ipaddr in self._dids:
            del self._dids[ipaddr]
