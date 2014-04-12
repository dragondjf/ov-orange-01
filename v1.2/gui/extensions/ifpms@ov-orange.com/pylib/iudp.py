#!/usr/bin/env python
# -*- coding: UTF8 -*-

# UDP-based app level communication protocol
import socket
import ipkt
import logging
import ifpms

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class Session():

    def __init__(self, host, port):

        self.host = host
        self.port = port

    def deal(self, header, body=None, protocol_ver=2):

        s = None
        body_str = ''

        if body:
            body_str = str(body)
            header.length = len(body_str)
        else:
            header.length = 0

        sendbuf = str(header) + body_str

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((self.host, self.port))
            s.settimeout(3)
            logger.info('send to ' + self.host + ': ' + repr((header, body)))
            s.send(sendbuf)
            recvbuf = s.recv(1024)
        except Exception, e:
            logging.exception(e)
            raise Error('transmit failed!')
        finally:
            if s:
                s.close()

        rsp = ipkt.unpack(recvbuf, protocol_ver)
        logger.info('recv from ' + self.host + ': ' + repr(rsp))
        self.echo_udp_status(rsp[0])
        return rsp

    def echo_udp_status(self, header):
        if ifpms.echo_flag:
            if header.ret == 0:
                if header.cmd in ifpms.echo_zh_status:
                    logger.info(ifpms.echo_zh_status[header.cmd] + '成功')
                else:
                    logger.info('%s 指令执行成功' % int(header.cmd))
            else:
                if header.cmd in ifpms.echo_zh_status:
                    logger.info(ifpms.echo_zh_status[header.cmd] + '失败')
                else:
                    logger.info('%s 指令执行失败' % int(header.cmd))
