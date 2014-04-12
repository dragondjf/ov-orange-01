#!/usr/bin/env python
# -*-coding:utf-8-*-
import logging
import serial
import time
logger = logging.getLogger(__name__)


class ModemError(RuntimeError):
    pass


class Modem(object):
    '''
    Provides access to a gsm modem

    '''
    def __init__(self, dev_id):
        self.conn = serial.Serial(dev_id, 9600, timeout=1, xonxoff=0)
        # make sure modem is OK
        self.command('AT')
        self.command('AT+CSCS="GSM"')
        self.command('AT+CMGF=0')

    def command(self, at_command, flush=True):
        logger.info(repr(at_command))
        self.conn.write(at_command)
        if flush:
            self.conn.write('\r')
        if at_command[-1] == '\x1a':
            time.sleep(4)
        results = self.conn.readlines()
        logger.info(repr(results))

        for line in results:
            if 'ERROR' in line:
                raise ModemError(results)
        return results

    def __del__(self):
        try:
            self.conn.close()
        except AttributeError:
            pass


def PDUsend(sms, length, message):
    """
    Send a SMS message by PDU
    """
    sms.command('AT+CMGS=%s' % length)
    results = sms.command(message + '\x1a', flush=False)
    return results


def TEXTsend(sms, number, message):
    """
    Send a SMS message by TEXT
    """
    sms.command('AT+CMGF=1')
    sms.command('AT+CMGS=%s' % number)
    results = sms.command(message + '\x1a', flush=False)
    return results


def sms_send(sms, sms_number, message, mode="PDU"):
    '''
        send message by mode
    '''

    lengthTPUD, SMS_SUBMIT_PDU = EncodeMessage(sms, sms_number, message)
    if mode == "PDU":
        results = PDUsend(sms, lengthTPUD, SMS_SUBMIT_PDU)
    elif mode == "TEXT":
        results = TEXTsend(sms, sms_number, message)
    return results


def sms_receive(sms, command, results, IsOk=False):
    '''
        Receive Message by different command,
            AT+CNMI=2,1
            AT+CNMI=2,2
            AT+CMGL=4
        return SCAnumber, OAnumber ,ReceiveTime, message
    '''
    try:
        SCAnumber = ''
        OAnumber = ''
        ReceiveTime = ''
        message = ''
        if command == 'AT+CNMI=2,2' and results != [] and len(results[1].split(',')) > 1:
            lengthmessage = results[1].split(',')[-1][:-2]
            content = results[2][:-2]
            SCAnumber, OAnumber, ReceiveTime, message = DecodeMessage(lengthmessage, content)
            if IsOk:
                sms_send(sms, OAnumber, '接收OK')
            results = []
        elif command == 'AT+CNMI=2,1' and results != [] and len(results[1].split(',')) > 1:
            index = results[1].split(',')[1][:-2]
            message = sms.command('AT+CMGR=%s' % index)
            sms.command('AT+CMGD=%s' % index)
            lengthmessage = message[1].split(',')[-1][:-2]
            content = message[2][:-2]
            SCAnumber, OAnumber, ReceiveTime, message = DecodeMessage(lengthmessage, content)
            if IsOk:
                sms_send(sms, OAnumber, '接收OK')
        elif command == 'AT+CMGL=4':
            lengthmessage = results[-4].split(',')[-1][:-2]
            content = results[-3][:-2]
            SCAnumber, OAnumber, ReceiveTime, message = DecodeMessage(lengthmessage, content)

        results = sms.conn.readlines()
    except Exception, e:
        logger.exception(e)
    return SCAnumber, OAnumber, ReceiveTime, message, results


def EncodeMessage(sms, sms_number, message):
    '''
        SMS_SUBMIT_PDU = SCA + PDUType + MR + DA + PID + DCS + VP + UDL + UD,
        Encode  message like SMS_SUBMIT_PDU
    '''

    # SCAnumber = sms.command('AT+CSCA?')[-3]
    # SCAnumber_begin = SCAnumber.find("+86") + 1
    # SMSC = SCAnumber[SCAnumber_begin:SCAnumber_begin + 13]
    # SMSC = '0891' + oddevenswitch(SMSC)
    SMSC = '00'
    DAnumber = '86' + sms_number
    usc2message = UCS2code(message)
    if len(usc2message) / 4 > 70:
        raise "message is too long,can't send"
    elif len(usc2message) / 2 < 10:
        lengthmessage = "0" + str(len(usc2message) / 2)
    else:
        lengthmessage = hex(len(usc2message) / 2)[2:]
    TPDU = '1100' + '0D91' + oddevenswitch(DAnumber) + '0008' + 'A8' + lengthmessage + usc2message  # 构建TPDU

    SMS_SUBMIT_PDU = SMSC + TPDU  # 构建PDU格式短信
    lengthTPUD = str(len(TPDU) / 2)  # 获取发送短信TPUD的长度

    return lengthTPUD, SMS_SUBMIT_PDU


def DecodeMessage(lengthmessage, SMS_deliver_PDU):
    '''
        decode hex content to true message:
        SMS_deliver_PDU = SCA + PDUType + MR + OA + PID + DCS + SCTS + UDL + UD
        SCA = '08' + '91' + '68' + SCAnumber  :国际编码
    '''

    Message = u''
    SCAnumber = oddevenswitch(SMS_deliver_PDU[6:18])[:-1]
    OAnumber = oddevenswitch(SMS_deliver_PDU[26:38])[:-1]
    SCTS = oddevenswitch(SMS_deliver_PDU[42:56])
    DCS = SMS_deliver_PDU[40:42]
    UDL = SMS_deliver_PDU[56:58]
    UD = SMS_deliver_PDU[58:]

    year = '20' + SCTS[0:2]
    month = SCTS[2:4]
    day = SCTS[4:6]
    hour = SCTS[6:8]
    mintue = SCTS[8:10]
    second = SCTS[10:12]
    TimeZone = SCTS[12:14]

    ReceiveTime = year + '-' + month + '-' + day + '-' + hour + '-' + mintue + '-' + second + ':' + '+' + str(int(TimeZone) - 24)

    # assert int(UDL, 16) == len(UD) / 2

    if DCS == '08':
        for i in range(len(UD) / 4):
            Message += unichr(int(UD[i * 4:(i + 1) * 4], 16))
    elif DCS == '00':
        s = bin(int(UD, 16))[2:]
        s1 = ''
        l_s = len(s) / 8
        for i in range(l_s):
            s1 += s[(l_s - i - 1) * 8: (l_s - i) * 8]
        message = ''
        b = len(s1) - (max(range(len(s1) / 7)) + 1) * 7
        s2 = s1[b:]
        l_s2 = len(s2) / 7
        for i in range(l_s2):
            bit7 = s2[(l_s2 - i - 1) * 7:(l_s2 - i) * 7]
            bit7 = '0' + bit7
            message += chr(int(bit7, 2))
        Message = message.decode('utf-8')

    logger.info('SMS_deliver_PDU:%s' % SMS_deliver_PDU)
    logger.info('SCAnumber:%s' % SCAnumber)
    logger.info('lengthmessage:%s' % lengthmessage)
    logger.info('OAnumber:%s' % OAnumber)
    logger.info('ReceiveTime:%s' % ReceiveTime)
    logger.info('UDL by read:%s' % str(int(UDL, 16)))
    logger.info('UDL by Calculated :%s' % str(len(UD) / 2))
    logger.info('UD:%s' % UD)
    logger.info('Message:%s' % Message)

    return SCAnumber, OAnumber, ReceiveTime, Message


def oddevenswitch(str):
    '''
        Switch the odd bit and the even bit  which are adjacent.
        if the length of string is odd,add F to the last bit.

    '''
    l = len(str)
    if l / 2 == 0:
        pass
    else:
        str = str + 'F'
    l = len(str)
    t = ''
    for i in range(l / 2):
        t += str[i * 2 + 1] + str[i * 2]
    return t


def UCS2code(message):
    '''
    Turn an string with simple chinese to UCS2 formatter,
    return usc2message

    examle:
        UCS2code('启用！12Hello!')
    return:
        542f7528ff010031003200480065006c006c006f0021
    '''
    if isinstance(message, str):
        message = message.decode('utf-8')
    usc2message = ''
    try:
        for i in range(len(message)):
            if len(repr(repr(message[i]))) == 12:
                usc2message += repr(repr(message[i]))[6:10]
            else:
                usc2message += '00' + message[i].decode('utf-8').encode('hex')
    except Exception, e:
        logger.exception(e)

    return usc2message

if __name__ == '__main__':
    pass
