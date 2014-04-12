#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..', '..'))
import ConfigParser
import pkg
import time
import signal
import socket
import datetime
import argparse
from cui import CUI
from tornado import ioloop
from tornado import iostream
from functools import partial
from multiprocessing import freeze_support, Process
from config import Config, opt, logger, get_ip_address, get_mac_address


class TCPClient(Process):
    def __init__(self, host, ip, send_err, file_path, test):
        super(TCPClient, self).__init__()
        self.daemon = True
        self.ip = ip
        self.test = test
        self.file_path = file_path
        self.send_err = send_err
        self.target = (host, opt.tcp_port)
        self.io_loop = ioloop.IOLoop()

    def on_connected(self):
        logger.info('TCP connection to %s established!' % repr(self.target))
        from wave_reader import WaveReader
        WaveReader(self.stream, self.send_err, self.file_path, self.test).run()

    def reconnect(self):
        self.io_loop.add_timeout(
            datetime.timedelta(seconds=1),
            self.connect
        )
        logger.warn('Reestablishing TCP connection to %s' % repr(self.target))

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.bind((self.ip, 0))
        self.stream = iostream.IOStream(sock, self.io_loop)
        self.stream.set_close_callback(self.reconnect)
        self.stream.connect(self.target, self.on_connected)

    def run(self):
        self.connect()
        if self.test:
            self.io_loop.add_callback(write_pid('tcp'))
        self.io_loop.start()


class UDPServer(Process):
    def __init__(self, ifname, ip, test):
        super(UDPServer, self).__init__()
        self.daemon = True
        self.ifname = ifname
        self.ip = ip
        self.test = test

    def deal_pkg(self, header, body):
        res = None
        if header.cmd == pkg.SET_CHANNEL_CTRL_REQ:
            res = pkg.Header(cmd=pkg.SET_CHANNEL_CTRL_RSP)
            for k in ('mode', 'enable', 'mu_factor'):
                Config.set(header.channel, k, getattr(body, k))

            wsets = [(w.begin, w.noise, w.end) for w in body.data]
            Config.set(header.channel, 'win_settings', wsets)
        elif header.cmd == pkg.GET_BASE_INFO_REQ:
            res = pkg.Header(cmd=pkg.GET_BASE_INFO_RSP)
            body = pkg.BaseInfo(
                mac=get_mac_address(self.ifname),
                hwid='Emultr',
                hwcode='EM',
                hw_version=chr(2) + chr(0),
                sw_version=chr(2) + chr(0),
                sw_revision=0,
                proto_version=2,
                channel_num=2,
                machine_id=0,
                ip_num=1,
                slot_id=0
            )
            res = pkg.combine(res, body)
        elif header.cmd == pkg.SET_SWITCH_CTRL_REQ:
            res = pkg.Header(cmd=pkg.SET_SWITCH_CTRL_RSP)
            if body.led == 1:       # light on
                if self.test:
                    algorithm_test(self.ip + ":" + str(header.channel))
                led = 'LED RED'
            elif body.led == 0xff:  # blink
                led = 'LED BLINK'
            elif body.led == 0:     # light off
                led = 'LED BLACK'
            logger.critical((self.ip, led))
        elif header.cmd == pkg.GET_CHANNEL_CTRL_REQ:
            res = pkg.Header(cmd=pkg.GET_CHANNEL_CTRL_RSP)
            ch_ctl = pkg.ChannelCtrl()
            for k in ('enable', 'mu_factor', 'mode'):
                setattr(ch_ctl, k, Config.get(header.channel, k))
            win_sts = Config.get(header.channel, 'win_settings')
            ch_ctl.win_size = len(win_sts)
            for ws in win_sts:
                wp = pkg.ChannelCtrl.WinSetting(
                    begin=ws[0],
                    end=ws[1],
                    noise=ws[2]
                )
                ch_ctl.data += wp.pack()
            res.data = ch_ctl.pack()
        else:
            logger.info(repr((header, body)))
        if res:
            res.seq = header.seq
            return res.pack()

    def on_msg(self, fd, events):
        data, address = self.sock.recvfrom(1024)
        header, body = pkg.unpack(data)
        res = self.deal_pkg(header, body)
        if res:
            self.sock.sendto(res, address)

    def init(self):
        addr = (self.ip, opt.udp_port)
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setblocking(0)
                sock.bind(addr)
                break
            except socket.error as e:
                logger.warn(e)
                logger.warn('restarting UDPServer')
                time.sleep(1)
        logger.info('UDP Server started on %s:%s' % addr)
        self.sock = sock

    def run(self):
        self.init()
        io_loop = ioloop.IOLoop()
        io_loop.add_handler(self.sock.fileno(), self.on_msg, io_loop.READ)
        if self.test:
            io_loop.add_callback(write_pid('udp'))
        io_loop.start()


def write_pid(pname):
    pid = '/tmp/%s.pid' % pname
    with open(pid, 'w') as fl:
        fl.write(str(os.getpid()))


def stop():
    try:
        pid1 = int(open('/tmp/udp.pid').read())
        pid2 = int(open('/tmp/tcp.pid').read())
    except IOError:
        logger.warn('can not find any running server')
    else:
        try:
            os.kill(pid1, signal.SIGKILL)
            os.kill(pid2, signal.SIGKILL)
        except Exception, e:
            logger.warn('error when killing %s: %s' % (pid1, e))
            logger.warn('error when killing %s: %s' % (pid2, e))
        else:
            logger.info('Process udp and tcp killed')
            try:
                os.remove('/tmp/udp.pid')
                os.remove('/tmp/tcp.pid')
                sys.exit(0)
            except OSError, e:
                logger.warn('remove pid file failed: %s' % e)


class Emulator():
    def __init__(self, ifname, host, ip, send_err, file_path, test):
        self.ifname = ifname
        self.host = host
        self.ip = ip
        self.send_err = send_err
        self.file_path = file_path
        self.test = test

    def run(self):
        UDPServer(self.ifname, self.ip, self.test).start()
        TCPClient(self.host, self.ip, self.send_err,
                  self.file_path, self.test).start()
        logger.info('Emulator started on %s' % self.ip)
        if self.test:
            time.sleep(60)
            stop()


def algorithm_test(filename):
    if os.path.exists(filename):
        cf = ConfigParser.ConfigParser()
        cf.read(filename)
        w_num = cf.getint("main", "w_num")
        cf.set("main", "w_num", w_num + 1)
        cf.write(open(filename, "w"))
    else:
        fn = os.path.join("./", filename)
        config = ConfigParser.ConfigParser()
        config.read([fn])
        config.add_section('main')
        config.set('main', 'w_num', 1)
        config.write(open(fn, 'w'))


def extract_range(ip_lst):
    r = []
    for ip in ip_lst:
        if '-' in ip:
            prefix, end = ip.split('-')
            prefix = prefix.split('.')
            start = prefix.pop(-1)
            for i in range(int(start), int(end) + 1):
                r.append('.'.join(prefix) + '.%s' % i)
        else:
            r.append(ip)
    return r


def launch_emulators(dc_list, ifname, host_ip, send_err, file_path, test):
    for dc_ip in dc_list:
        Emulator(ifname, host_ip, dc_ip, send_err, file_path, test).run()


def main(args):
    import fnmatch
    for fileName in os.listdir('./'):
        if fnmatch.fnmatch(fileName, '192*:*'):
            os.remove(fileName)
    self_ip = get_ip_address(args.interface)
    host_ip = args.host_ip or self_ip
    dc_list = extract_range(args.dc_ips) or [self_ip]
    file_path = args.file_path
    send_err = True if args.send_err else None
    test = True if args.algorithm_test else None
    launch_emu = partial(
        launch_emulators, dc_list, args.interface, host_ip, send_err, file_path, test)
    if args.cui:
        [logger.removeHandler(h) for h in logger.handlers]
        CUI(dc_list, logger, launch_emu).show()
    else:
        launch_emu()
        signal.signal(signal.SIGINT, lambda *arg: sys.exit())
        signal.pause()


parser = argparse.ArgumentParser(description='Data Collector Emulator')
parser.add_argument(
    '-t', '--target',
    dest='host_ip',
    action='store',
    default=None,
    help='IP address of which running IFPMS software.'
)

parser.add_argument(
    '-d', '--dc_ip',
    dest='dc_ips',
    nargs='+',
    action='store',
    default=[],
    help='IP address(es) of emulated DC.'
         'You can specify multiple addresses like:'
         '10.10.10.1-10 or just 10.10.10.1 10.10.10.2.'
)

parser.add_argument(
    '-z', '--test-algorithm',
    dest='algorithm_test',
    action='store_true',
    default=False,
    help='Test algorithm.'
)

parser.add_argument(
    '-n', '--no-CUI',
    dest='cui',
    action='store_false',
    default=True,
    help='Disable CUI.'
)

parser.add_argument(
    '-e', '--send-error',
    dest='send_err',
    action='store_true',
    default=False,
    help='Send ERROR.'
)

parser.add_argument(
    '-p', '--file-path',
    dest='file_path',
    action='store',
    default='.',
    help='Add wav file path.'
)

parser.add_argument(
    '-i', '--interface',
    dest='interface',
    action='store',
    default='eth0',
    help='The network interface to get IP address, default eth0.'
)


if __name__ == '__main__':
    freeze_support()
    main(parser.parse_args())
