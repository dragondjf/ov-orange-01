from multiprocessing import Manager
from tornado.log import enable_pretty_logging
from logging import getLogger, NOTSET, Filter


class opt(object):
    PreProcessing = 1
    RawData = 2
    MixMode = 3
    tcp_port = 6002
    udp_port = 6004


class Config(object):
    @classmethod
    def get(cls, *args):
        if len(args) == 1:
            channel, name = '', args[0]
        else:
            channel, name = args
        return _config.get(name + str(channel))

    @classmethod
    def set(cls, *args):
        if len(args) == 1:
            channel, name, value = '', args
        else:
            channel, name, value = args
        _config[name + str(channel)] = value


mgr = Manager()
_config = mgr.dict()

_config.update({
    'fft_size': 1024,
    'enable1': 1,
    'enable2': 1,
    'mode1': opt.PreProcessing,
    'mode2': opt.PreProcessing,
    'mu_factor1': 0xff,
    'mu_factor2': 0xff,
    'win_settings1': [(5, 100, 0)],
    'win_settings2': [(5, 100, 0)]
})


logger = getLogger()
enable_pretty_logging()
logger.setLevel(NOTSET)


class LEDFilter(Filter):
    BLINK = '\033[5m'
    RED = '\033[1;41;37m'
    BLACK = '\033[2;44;30m'
    END = '\033[0m'

    def filter(self, record):
        if record.levelname != 'CRITICAL':
            return True
        else:
            ip, color = record.msg
            prefix = getattr(self, color.split()[1])
            print '%s[LED]%s %s' % (prefix, self.END, ip)

logger.handlers[0].addFilter(LEDFilter())


import fcntl
import struct
import socket
#from utils import get_ip_address


def get_ip_address(ifname="eth0"):
    import socket
    if False:#platform_is('windows', 'cygwin'):
        ip = '127.0.0.1'
    else:
        myname = socket.getfqdn(socket.gethostname())
        ip = socket.gethostbyname(myname)
    if ip.startswith('127'):  # makes no sense
        import netifaces
        print netifaces.AF_INET
        
        print netifaces.ifaddresses(ifname)
        print ifname
        try:
            ip = netifaces.ifaddresses(ifname)[netifaces.AF_INET][0]['addr']
        except:
            ip = netifaces.ifaddresses("wlan0")[netifaces.AF_INET][0]['addr']
    return ip

def get_mac_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
    return info[18:24]
    # return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
