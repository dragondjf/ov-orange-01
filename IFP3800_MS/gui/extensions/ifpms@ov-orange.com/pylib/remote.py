#!/usr/bin/env python
# -*- coding: UTF8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler

import logging
import urllib2

import os
import threading
import thread
import time
import Queue
import base64
import socket
import simplejson
from xpcom import components, ServerException, nsError
import ifpms
import userifpms


import os

import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options
import tornado.httpserver
import tornado.web
import tornado.websocket


logger = logging.getLogger(__name__)
define("port", default=userifpms.remote_server_port, help="run port", type=int)


class PAListHandler(tornado.web.RequestHandler):
    def get(self):
        resp = {"protection_areas": [], "total_number": self.application.mgmt.pa_list.length}
        try:
            for i in xrange(0, self.application.mgmt.pa_list.length):
                pa_item = {}
                t = self.application.mgmt.pa_list.queryElementAt(i, components.interfaces.nsIPyIfpmsPA)
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
        self.write(resp_str)

    def post(self):
        self.write("post")


class AlarmHistoryHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("AlarmHistoryHandler")

    def post(self):
        self.write("post")


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        fd = open("chrome/etc/custom.conf","r")
        confstr = fd.read()
        fd.close()
        #resp_str = simplejson.dumps(confstr)
        self.write("<pre>" + confstr + "</pre>")

    def post(self):
        backcode = 2 # backcode: 1: success  2: 用户名不存在 3：密码错误
        account = self.get_argument('account', '')
        password = self.get_argument('password', '')
        logger.info(account)
        logger.info(password)
        fd = open("chrome/etc/custom.conf","r")
        confstr = fd.read()
        fd.close()
        confObj = simplejson.loads(confstr)
        logger.info(confObj['userinfo'])
        if "userinfo" in confObj:
            for user in confObj['userinfo']:
                if account == user['account']:
                    if password == user['password']:
                        backcode = 1
                    else:
                        backcode = 3
                break
        self.write(str(backcode))


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("LogoutHandler")

    def post(self):
        self.write("post")


class PushStatusHandler(tornado.websocket.WebSocketHandler):
    socket_handlers = set()

    def open(self):
        PushStatusHandler.socket_handlers.add(self)
        logger.info("some client come in")

    def on_close(self):
        PushStatusHandler.socket_handlers.remove(self)
        logger.info("some client logout")

    def on_message(self, message):
        pass


class SetProtectHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("SetProtectHandler")

    def post(self):
        '''
        数据格式：
        {"did": 1, "pid":1, "enable":1}# 1:开启 0：禁用
        '''
        if userifpms.remote_receive_enable:
            did = self.get_argument('did', '')
            pid = self.get_argument('pid', '')
            enable = self.get_argument('enable', '')
            flag = False
            if enable != "":
                try:
                    for i in xrange(0, self.application.mgmt.pa_list.length):
                        t = self.application.mgmt.pa_list.queryElementAt(i, components.interfaces.nsIPyIfpmsPA)
                        if t.did == int(did) and t.pid == int(pid):
                            t.enable = bool(int(enable))
                            flag = True
                            break
                except Exception, e:
                    logger.exception(e)
                # 1:成功 0：失败 -1:无权限
                if flag:
                    self.write("1")
                else:
                    self.write("0")
            else:
                self.write("-1")


class NotFoundHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("404")

    def post(self):
        self.write("post")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/palist", PAListHandler),
            (r"/alarmHistory", AlarmHistoryHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/pushstatus", PushStatusHandler),
            (r"/setprotect", SetProtectHandler),
            (r"/404", NotFoundHandler)
        ]
        settings = dict(
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
    def _setglabel(self, mgmt):
        self.mgmt = mgmt


class RemoteThread(threading.Thread):
    '''支持远程访问的线程 by jack.zh'''

    def __init__(self):
        logger.info("remote thread init.")
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
        if userifpms.remote_send_enable:
                self.mesg.put((did, pid, sid, status, status_change_time))

    def run(self):
        try:
            thread.start_new_thread(self.send_message_ws, ())
            tornado.options.parse_command_line()
            a = Application()
            a._setglabel(self.mgmt)
            app = tornado.httpserver.HTTPServer(a)
            app.listen(options.port)
            tornado.ioloop.IOLoop.instance().start()
        except Exception, e:
            logger.info("remote start error.")
        else:
            pass
        finally:
            pass

        logger.info("thread exit.")


    def send_message_ws(self):
        while True:
            try:
                did, pid, sid, status, status_change_time = self.mesg.get()
                notification = {"did": did, "pid": pid, "sid": sid, "status": status, "status_change_time": status_change_time}
                logger.info("================send========================")
                logger.info(notification)
                notification = simplejson.dumps(notification)
                for handler in PushStatusHandler.socket_handlers:
                    try:
                        handler.write_message(notification)
                    except:
                        logger.warn('Error sending message')
            except:
                logger.warn('Error send_message_ws')


if __name__ == "__main__":
    pass
    # tornado.options.parse_command_line()
    # a = Application()
    # a._setglabel(1)
    # app = tornado.httpserver.HTTPServer(a)
    # app.listen(options.port)
    # tornado.ioloop.IOLoop.instance().start()


