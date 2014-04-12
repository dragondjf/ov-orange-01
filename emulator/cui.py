#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import logging
from urwid import AttrWrap, SimpleListWalker
from urwid import Columns, Text, ListBox, Frame, LineBox
from urwid import MainLoop, ExitMainLoop, raw_display

palette = [

    ('LED BLACK', 'white', 'black', 'bold'),
    ('LED RED', 'white', 'dark red', 'bold'),
    ('LED BLINK', 'white', 'dark red', 'blink'),

    ('INFO', 'dark green', 'black', 'bold'),
    ('DEBUG', 'dark blue', 'black', 'bold'),
    ('WARNING', 'yellow', 'black', 'bold'),
    ('ERROR', 'dark red', 'black', 'bold'),

    ('NORMAL', 'white', 'black'),
    ('SELECTED', 'black', 'white'),
]


def pa_wid(label):
    return AttrWrap(Text(label), 'NORMAL', 'SELECTED')


class MultiProcHandler(logging.Handler):
    def __init__(self, cui):
        import threading
        import multiprocessing
        logging.Handler.__init__(self)
        self.cui = cui
        self.queue = multiprocessing.Queue(-1)

        t = threading.Thread(target=self.receive)
        t.daemon = True
        t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)

    def receive(self):
        import sys
        import traceback
        while True:
            try:
                record = self.queue.get()
                if not record.prefix:
                    self.cui.set_alarm(*record.msg)
                else:
                    self.cui.write_log(record.prefix, record.levelname)
                    self.cui.write_log(record.msg)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        # ensure that exc_info and args
        # have been stringified.  Removes any chance of
        # unpickleable things inside and possibly reduces
        # message size sent over the pipe
        if record.args:
            try:
                record.msg = record.msg % record.args
            except TypeError:
                record.msg = str(record.msg)
            finally:
                record.args = None
        if record.exc_info:
            self.format(record)
            record.exc_info = None
        if record.levelname == 'CRITICAL' and isinstance(record.msg, tuple):
            record.prefix = None
        else:
            prefix = '['
            prefix += record.levelname[0] + ' '
            prefix += time.strftime(
                "%y%m%d %H:%M:%S",
                time.localtime(record.created)
            ) + ' '
            prefix += record.filename + ':'
            prefix += str(record.lineno) + ']'
            record.prefix = prefix

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        logging.Handler.close(self)


class CUI(object):
    header = LineBox(
        Text(
            ' - '.join(
                ['You may use "ifconfig eth0:n 192.168.100.n"'
                 + ' to assign more IP addresses',
                 'Quit: ESC']
            )
        ), 'Data Collector Emulator')

    def __init__(self, pa_list, logger, callback):
        logger.addHandler(MultiProcHandler(self))
        self.pa_list = SimpleListWalker([pa_wid(t) for t in pa_list])
        self.lbar = LineBox(AttrWrap(
            ListBox(self.pa_list),
            'white'
        ), 'PA List')
        self.log = SimpleListWalker(())
        self.right = ListBox(self.log)
        cols = Columns([
            ('weight', 2, self.lbar),
            ('weight', 8, self.right)
        ], dividechars=1, focus_column=1)
        frame = Frame(cols, header=self.header)
        screen = raw_display.Screen()

        def unhandled(key):
            if key == 'esc':
                raise ExitMainLoop()
        self.loop = MainLoop(frame, palette, screen, unhandled_input=unhandled)

        def auto_refresh(*dummy):
            self.loop.set_alarm_in(0.1, auto_refresh)
        auto_refresh()
        callback()

    def write_log(self, msg, level='NORMAL'):
        msg = AttrWrap(Text(msg), level)
        self.log.append(msg)
        l = len(self.log)
        if l:
            self.right.set_focus(l)

    def set_alarm(self, pa_name, attr='LED RED'):
        for w in self.pa_list:
            if w.text == pa_name:
                w.attr = attr

    def show(self):
        self.loop.run()
