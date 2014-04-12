#!/usr/bin/env python
# -*- coding: UTF8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler

import logging
import urllib2

import os
import threading
import time
import Queue
import base64
import socket
import simplejson
from xpcom import components, ServerException, nsError
import ifpms
import userifpms

from sms import PySMS

logger = logging.getLogger(__name__)
socket.setdefaulttimeout(25)


def web_push(url, user, passwd, notification):

    try:
        f = None
        req = urllib2.Request(url)

        if notification:
            req.add_data("notification=" + simplejson.dumps(notification))
        auth = "Basic " + base64.urlsafe_b64encode("%s:%s" % (user, passwd))
        req.add_header("Authorization", auth)
        logger.info("web push [%s]: [%s]" % (url, simplejson.dumps(notification)))
        f = urllib2.urlopen(req)
        data = f.read()
        logger.info("web push ok. response is [%s]" % data)
    #这里不捕获异常，让上层来捕获处理
    finally:
        if f:
            f.close()

    return


def web_get(url, user, passwd):

    f = None

    try:
        req = urllib2.Request(url)
        logger.info("web get [%s]" % (url))
        auth = "Basic " + base64.urlsafe_b64encode("%s:%s" % (user, passwd))
        req.add_header("Authorization", auth)
        f = urllib2.urlopen(req)
        logger.info("web get ok.")
    except Exception, e:
        logger.info("web get failed.")
    finally:
        if f:
            f.close()

    return


def sms_push(sms_com, sms_number, messagetitle, notification):

    status_name_zh = ['禁用', '断开', '运行', '预警', '告警', '断纤', '爆破']

    changetime = time.localtime(notification["status_change_time"])
    # messageTitle = u"请注意：" + ifpms.PAname[sms_number].decode('UTF8')
    # messagetitle = u"请注意：" + self.mgmt.getPA(notification['did'], notification['pid']).name
    messagecontent = u' ' + time.strftime("%Y-%m-%d %H:%M:%S", changetime).decode('UTF8') + u' ' + status_name_zh[notification["status"]].decode('UTF8')
    sms_text_zh = messagetitle + messagecontent
    try:
        logger.info("sms push [%s]: [%s]" % (sms_number, sms_text_zh))
        results = PySMS.sms_send(sms_com, sms_number, sms_text_zh)
        if 'OK' == results[-1][0:2]:
            logger.info("sms push [%s] ok" % (sms_number))
        else:
            logger.info("send message may be ok,but send next message may be effected")
        time.sleep(5)
    except Exception, e:
        logger.exception(e)


class WebsHandler(BaseHTTPRequestHandler):

    ''' Main class to present web pages and authentication. '''

    def do_AUTH(self):
        '''HTTP鉴权，鉴权通过则返回真'''
        is_auth = False
        try:
            if self.headers.getheader('Authorization') is None:
                # HTTP头无鉴权信息
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Basic realm=\"ov-orange\"')
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('no auth header received')
                logger.error("no auth header received")
            elif self.headers.getheader('Authorization') == 'Basic b3Ytb3JhbmdlOm92LW9yYW5nZQ==':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                is_auth = True
            else:
                # 鉴权未通过
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Basic realm=\"ov-orange\"')
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(self.headers.getheader('Authorization'))
                self.wfile.write('not authenticated')
                logger.error("(%s) not authenticated" % self.headers.getheader('Authorization'))
        except Exception, e:
            logger.exception(e)

        return is_auth

    def do_GET(self):
        '''处理HTTP GET请求'''

        logger.info("%s HTTP GET: %s" % (str(self.client_address), self.path))

        if not self.do_AUTH():
            pass
        else:
            # 鉴权通过
            if self.path.startswith("/webs/protection_areas/list"):

                #返回pa列表

                resp = {"protection_areas": [], "total_number": self.mgmt.pa_list.length}
                try:
                    for i in xrange(0, self.mgmt.pa_list.length):
                        pa_item = {}
                        t = self.mgmt.pa_list.queryElementAt(i, components.interfaces.nsIPyIfpmsPA)
                        pa_item["did"] = t.did
                        pa_item["pid"] = t.pid
                        pa_item["sid"] = t.sid
                        pa_item["name"] = t.name
                        pa_item["desc"] = t.desc
                        pa_item["enable"] = t.enable
                        pa_item["cx"] = t.cx
                        pa_item["cy"] = t.cy
                        pa_item["status"] = t.status
                        pa_item["status_change_time"] = t.latest_change_time
                        resp["protection_areas"].append(pa_item)

                except Exception, e:
                    logger.exception(e)

                resp_str = simplejson.dumps(resp)
                logger.info(resp_str)
                self.wfile.write(resp_str)

            elif self.path.startswith("/webs/protection_areas/get"):

                #返回单个pa

                resp = {}
                pa_item = None
                try:
                    for i in xrange(0, self.mgmt.pa_list.length):
                        t = self.mgmt.pa_list.queryElementAt(i, components.interfaces.nsIPyIfpmsPA)
                        if t.sid == os.path.basename(self.path):
                            pa_item = {}
                            pa_item["did"] = t.did
                            pa_item["pid"] = t.pid
                            pa_item["sid"] = t.sid
                            pa_item["name"] = t.name
                            pa_item["desc"] = t.desc
                            pa_item["enable"] = t.enable
                            pa_item["cx"] = t.cx
                            pa_item["cy"] = t.cy
                            pa_item["status"] = t.status
                            pa_item["status_change_time"] = t.latest_change_time
                            resp["protection_area"] = pa_item
                            break
                    else:
                        resp = {"request": self.path, "error_code": 1, "info": "invalid sid."}

                except Exception, e:
                    resp = {"request": self.path, "error_code": 1, "info": "unknown error."}
                    logger.exception(e)

                resp_str = simplejson.dumps(resp)
                logger.info(resp_str)
                self.wfile.write(resp_str)

            else:
                resp = {"request": self.path, "error_code": 1, "info": "invalid url."}
                resp_str = simplejson.dumps(resp)
                logger.info(resp_str)
                self.wfile.write(resp_str)

    def do_POST(self):
        '''处理HTTP POST请求'''

        logger.info("%s HTTP POST: %s" % (str(self.client_address), self.path))

        if not self.do_AUTH():
            pass
        else:
            try:
                #logger.info(self.headers.getheader('Authorization'))
                content_len = int(self.headers.getheader('content-length'))
                post_body = self.rfile.read(content_len)
                #logger.info("POST body is: [%s]"%post_body)
            except Exception, e:
                logger.exception(e)

        resp = {"request": self.path, "error_code": 0, "info": "ok"}
        resp_str = simplejson.dumps(resp)
        #logger.info(resp_str)
        self.wfile.write(resp_str)


class WebPush(threading.Thread):
    '''通道消息推送'''

    def __init__(self):
        logger.info("Create thread for web push.")
        self._stop = threading.Event()
        self.mesg = Queue.Queue()
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()

    def stop(self):
        self._stop.set()

    def is_stopped(self):
        return self._stop.isSet()

    def push(self, did, pid, sid, status, status_change_time):

        '''状态变更消息入口，放入消息队列待处理'''
        if userifpms.webpush_enable:
            for webs_url in userifpms.webs_urls:
                self.mesg.put((webs_url, ifpms.resend_times, did, pid, sid, status, status_change_time))
        if userifpms.smspush_enable:
            if status > 3:  # 告警类才发短信
                for sms_number in userifpms.sms_numbers:
                    self.mesg.put((sms_number, 3, did, pid, sid, status, status_change_time))

    def run(self):
        '''从消息队列取出消息，发往指定的web service'''
        try:
            self.sms_com = PySMS.Modem(userifpms.sms_port)  # 打开串口，初始化设置
            self.results = self.sms_com.command(ifpms.at_cnmi)  # 设置接收短信方式
            self.command = ifpms.at_cnmi  # 保存命令设置
            # logger.info(self.results)
        except Exception, e:
            logger.info(e)

        while not self.is_stopped():

            push_fail = None
            try:
                # if userifpms.webpush_enable:
                #     dest, times, did, pid, sid, status, status_change_time = self.mesg.get(True, ifpms.webs_idle_seconds)
                # else:
                dest, times, did, pid, sid, status, status_change_time = self.mesg.get(False)
            except Queue.Empty:
                '''空报文用于心跳'''
                if userifpms.webpush_enable:
                    for webs_url in userifpms.webs_urls:
                        web_get(webs_url, "ov-orange", "ov-orange")
                #当消息队列为空时进行短信接收，不为空时进行短信发送，保证串口不能被同时占用
                if userifpms.smspush_enable:
                    SCAnumber, OAnumber, ReceiveTime, message, self.results = PySMS.sms_receive(self.sms_com, self.command, self.results)
                    try:
                        # logger.info('短信中心号码：%s' % SCAnumber)
                        # logger.info('发送方号码：%s' % OAnumber)
                        # logger.info('短信中心接收到信息的时间：%s' % ReceiveTime)
                        # logger.info('短信内容：%s' % message.encode('utf-8'))
                        self.handle_ctrl_message(OAnumber, userifpms.m_ctrlnumbers, message)
                    except Exception, e:
                        logger.exception(e)
                time.sleep(1)
                continue
            except Exception, e:
                logger.exception(e)

            notification = {"did": did, "pid": pid, "sid": sid, "status": status, "status_change_time": status_change_time}
            logger.info(notification)

            try:
                push_fail = False
                if dest.startswith("http"):
                    web_push(dest, "ov-orange", "ov-orange", notification)
                else:
                    messagetitle = u"请注意：" + userifpms.sms_title.decode('utf-8') + u' ' + self.mgmt.getPA(notification['did'], notification['pid']).name
                    sms_push(self.sms_com, dest, messagetitle, notification)
            except PySMS.ModemError:
                push_fail = True
                logger.error("sms push[%s] fail" % dest)
            except urllib2.URLError:
                logger.error("web push[%s] fail" % dest)
                push_fail = True
            except Exception, e:
                logger.error("push[%s] fail" % dest)
                logger.exception(e)

            if push_fail and times > 0:
                times -= 1
                t = threading.Timer(ifpms.resend_interval, self.resend, args=[dest, times, did, pid, sid, status, status_change_time])
                t.start()

        logger.info("thread exit.")

    def resend(self, dest, times, did, pid, sid, status, status_change_time):
        ''' 发送失败的情况下，重新发送 '''
        #logger.info('web push resend fail! url=%s times=%d' %(webs_url, times))
        self.mesg.put((dest, times, did, pid, sid, status, status_change_time))

    def handle_ctrl_message(self, OAnumber, m_ctrlnumbers, message):
        if OAnumber in m_ctrlnumbers:
            if message.find(u'查询') >= 0:
                index = message.find(u'查询')
                status_name_zh = ['禁用', '断开', '运行', '预警', '告警', '断纤', '爆破']
                messagetitle = userifpms.sms_title
                messagetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))).decode('UTF8')
                palist = message[index + 3:-1].split(',')
                # logger.info(palist)
                messagecontent = u''
                for sid in palist:
                    did = int(sid.split('-')[1])
                    pid = int(sid.split('-')[2])
                    status = self.mgmt.getPA(did, pid).status
                    name = self.mgmt.getPA(did, pid).name
                    messagecontent += u'[' + name + u': ' +status_name_zh[status].decode('UTF8') + u'] '
                statusmessage = messagetitle.decode('UTF8') + u' ' + messagetime + messagecontent
                PySMS.sms_send(self.sms_com, OAnumber, statusmessage)
            elif message.find(u'禁用') >= 0:
                index = message.find(u'禁用')
                palist = message[index + 3:-1].split(',')
                # logger.info(palist)
                for sid in palist:
                    did = int(sid.split('-')[1])
                    pid = int(sid.split('-')[2])
                    self.mgmt.getPA(did, pid).enable = False
                PySMS.sms_send(self.sms_com, OAnumber, '禁用OK')
            elif message.find(u'启用') >= 0:
                index = message.find(u'启用')
                palist = message[index + 3:-1].split(',')
                # logger.info(palist)
                for sid in palist:
                    did = int(sid.split('-')[1])
                    pid = int(sid.split('-')[2])
                    self.mgmt.getPA(did, pid).enable = True
                PySMS.sms_send(self.sms_com, OAnumber, '启用OK')

if __name__ == '__main__':
    pass
