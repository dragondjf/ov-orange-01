#!/usr/bin/env python
# -*- coding: UTF8 -*-

#告警状态持续时间设置
alarm_delay_secs = 5  # 默认告警状态持续5秒


# 爆破设置
blast_num = 2  # 至少有blast_num个防区同时满足blast_freq和blast_data0才会爆破
blast_freq = 4000  # 爆破的一次绝对能量值，与freq值进行比较
blast_data0 = 50   # 爆破的一次相对能量值，与data0值进行比较


# 联动设置
webs_enable = False          # 外部联动总开关，True表示开启，False表示关闭

# web联动设置
webpush_enable = False  # 网络报文发送开关，True表示开启，False表示关闭
webs_port = 8000            # 端口号
webs_urls = ["http://127.0.0.1:8000/tgcssbms/sensor/notification", "http://192.168.100.2:8000/tgcssbms/sensor/notification"]      # 本地测试用服务地址

# 短信联动设置
smspush_enable = False   # 手机短信发送开关，True表示开启，False表示关闭
sms_port = 'COM3'       # 串口号，根据实际情况需修改
sms_numbers = ['13986218913']      # 报警信息通知手机号
sms_title = '东湖高新梨园基站'     # 报警信息描述表头
m_ctrlnumbers = ['13986218913']    # 可发送控制命令的手机号

# Q采集器模式下GSM开关
gsm_flag = False
gsm_status = [4, 5]  # 4代表告警, 5代表断纤
