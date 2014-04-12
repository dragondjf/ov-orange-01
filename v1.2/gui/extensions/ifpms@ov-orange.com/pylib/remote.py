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
        self.write("LoginHandler")

    def post(self):
        self.write("post")


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("LogoutHandler")

    def post(self):
        self.write("post")


class PushStatusHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("PushStatusHandler")

    def post(self):
        self.write("post")


class SetProtectHandler(tornado.websocket.WebSocketHandler):
    socket_handlers = set()

    def open(self):
        WebsocketStatusHandler.socket_handlers.add(self)
        logger.info("some client come in")

    def on_close(self):
        WebsocketStatusHandler.socket_handlers.remove(self)
        logger.info("some client logout")

    def on_message(self, message):
        pass


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


