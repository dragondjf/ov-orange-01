#!/usr/bin/env python
# -*- coding: UTF8 -*-

#server setting
tcp_port = 6002
udp_port = 6004

#wenbo参数，数组分别表示白天模式（7点至20点为白天）和夜间模式
wb_settings = {
    'Daytime': [7, 20],  # 白天时段 7点至20点，即21点至次日6点为夜晚
    'SRange': [6, 6],    # 短时间范围：单位为秒，乘以单位点数则为瞬间点数
    'LRange': [1 * 300, 1 * 300],    # 长时间范围：单位为秒，乘以单位点数则为瞬间点数
    'LowFreqThreshold': [0, 0],  # 低频域门限附加值
    'LowFreqThresholdTime': [1, 1],  # 低频域门限次数

#长时间范围内，达到预警门限的比例，超过该比例产生报警
    'WarnRatio': [0, 0],     # 比例门限

#任意时刻，频域值达到HighFreqThreshold直接报警
    'HighFreqThreshold': [2000, 2000]  # 高频域门限，发生一次即直接严重告警，不需等到长时间统计，用于爆破识别

}

#原始样本处理参数
raw_settings = {
    'enable_pkt_log': False  # 允许报文记录到文件
}

#暴雨抑制，True-减少50%的预警率，False，显示为“干扰”
rainstorm_suppression = False

#自适应地波算法爆破门限设置
Blasting_enable = False  # 开启以采集器为单位进行分组判断爆破的功能
Blasting_P = {
    '192.168.100.4': [[4000, 50], [4000, 50]],
    '192.168.100.5': [[4000, 50], [4000, 50]]
}
#模式设置
fft_window_settings = {
    # 1 标准周界
    # 2 未使用
    # 3 标准地波
    # 4 自适应周界
    # 5 自适应地波
    # 6 均方周界
    0: [{
        'begin': 5,  # 计算能量和值的频点的起点
        'end': 100,  # 频点的终点
        'noise': 25,  # 忽略能量值低的噪点，能量低于该值的频点不计
        'magic': 1  # 能量求合后除以该值
        }],
    1: [{
        'begin': 2,  # 计算能量和值的频点的起点
        'end': 30,  # 频点的终点
        'noise': 15,  # 忽略能量值低的噪点，能量低于该值的频点不计
        'magic': 1  # 能量求合后除以该值
        }],
    2: [{
        'begin': 2,  # 计算能量和值的频点的起点
        'end': 30,  # 频点的终点
        'noise': 0,  # 忽略能量值低的噪点，能量低于该值的频点不计
        'magic': 1  # 能量求合后除以该值
        }],
    3: [{
        'begin': 2,  # 计算能量和值的频点的起点
        'end': 30,  # 频点的终点
        'noise': 0,  # 忽略能量值低的噪点，能量低于该值的频点不计
        'magic': 1  # 能量求合后除以该值
        }],
    4: [{
        'begin': 2,  # 计算能量和值的频点的起点
        'end': 30,  # 频点的终点
        'noise': 15,  # 忽略能量值低的噪点，能量低于该值的频点不计
        'magic': 1  # 能量求合后除以该值
        }],
    5: [{
        'begin': 2,  # 计算能量和值的频点的起点
        'end': 30,  # 频点的终点
        'noise': 0,  # 忽略能量值低的噪点，能量低于该值的频点不计
        'magic': 1  # 能量求合后除以该值
        }],
    6: [{
        'begin': 2,  # 计算能量和值的频点的起点
        'end': 30,  # 频点的终点
        'noise': 0,  # 忽略能量值低的噪点，能量低于该值的频点不计
        'magic': 1  # 能量求合后除以该值
        },
        {
        'begin': 30,  # 计算能量和值的频点的起点
        'end': 510,  # 频点的终点
        'noise': 0,  # 忽略能量值低的噪点，能量低于该值的频点不计
        'magic': 1  # 能量求合后除以该值
        }]
}

#周界算法配置参数
max_t = 2   # 自适应周界算法：取多长时间的max特征值的最大值进行freq值校正（单位分钟）
magic = 20  # 标准周界算法：freq值除以该值使其变化范围在0-300之间

#全局参数
break_time = 2   # 断纤响应时间
davg_time = 2    # 利用断纤前的一段时间来校正产生的断纤是否正常
fiber_break_threshold_avg = 12  # 一个点的断纤平均值告警门限
fiber_k_history = 1500  # 断纤判断中突变时刻的历史值初始化设置
fiber_k = 200   # 斜率校正断纤，特征值data9超过此值表示断纤
fiber_pa = []    # 屏蔽个别防区的断纤功能
log_size = 10 * 1024 * 1024  # 单个日志文件大小
log_num = 100  # 日志文件数量
wav_days = 10  # 音频保留天数
wav_path = "chrome/wavs/"
wav_flag = False  # True表示遍历文件方式，False表示自动生成文件列表方式(必须指定开始时间和结束时间)
alarm_delay_secs = 5  # 告警状态持续秒数
alarm_history_length = 1000  # 保存最新的1000条历史状态
alarm_list = [4, 5, 6, 7, 8, 9, 10]   # 编号0-10与后续列表状态对应，在alarm_list中的状态将显示在告警列表中.['禁用','断开','运行','预警','告警', '断纤', '爆破','拆盖','机盖正常','风雨','启动']
alarm_minor_flag = True  # False表示预警不显示，True表示预警显示

#环境自适应探测器步进
environment_detect_flag = False  # 环境自适应探测器开启标志
alarm_resistant_factor_step = 0    # 抗干扰因子步进
sensitivity_step = 0    # 灵敏度步进


#小波滤波参数设置
checkend = False    # 是否进行x小波滤波
smooth_level = 10  # 小波f分解层数
smooth_A = True   # True为去掉载波，False为b不去掉载波
smooth_DL = 0    # 滤去低频的层数
smooth_DH = 3    # 滤去高频的层数


# Web Service 配置
webs_idle_seconds = 1  # 空闲时间,单位秒
resend_times = 10  # 发送失败后重新发送的次数
resend_interval = 12  # 重新发送时间（单位秒）

# 短信配置
at_cnmi = 'AT+CNMI=2,1'  # 接收短信命令配置


#均方周界算法中开启度范围
mean_min = 1000  # 默认开启度最小值
mean_max = 3000  # 默认开启度最大值
mean_magic = 4  # 进行均方运算的开启度比例限定因子
mean_range_magic = 10  # 进行均方运算的开启度范围限定因子
mean_points = 10  # 特征运算所用的点数

#Q系列设备功能控制信息中手机号码设置，最多配置8个手机号码
#mode为0/1对应管理员和操作员权限
Q_phones = [
    {'mode':0, 'number':15271926542}
]
#常用udp指令根据返回码和命令字显示设置状态
echo_flag = True  # 是否显示udp指令中文设置消息
echo_zh_status = {
    17: '查询产品基本固化信息 ',
    19: '设置通信控制信息  ',
    23: '设置通道控制信息 ',
    25: '设置设备功能控制信息 ',
    26: '执行开关控制命令 ',
    28: '执行重启命令 ',
    29: '执行执行保存配置命令 '
}

# 新建防区缺省配置
# work_mode 表示工作模式：1-标准周界、4-自适应周界、3-标准地波、5-自适应地波
# procee_mode 表示采集模式 1-预处理、2-原始数据、3-混合模式
# alarm_sensitivity 表示灵敏度
# alarm_resp_time 表示响应时间
# alarm_resistant_factor 表示抗干扰因子
# alarm_resistant_factor_gsd 表示地波预警率
# sensitivity 表示数字放大
pa_default_val = {
    "default": {
        "work_mode": 4,
        "process_mode": 1,
        "alarm_sensitivity": 80,
        "alarm_resp_time": 3,
        "alarm_resistant_factor": 2,
        "alarm_resistant_factor_gsd": 50,
        "sensitivity": 128
    },
    "gsd": {
        "work_mode": 5,
        "process_mode": 2,
        "alarm_sensitivity": 40,
        "alarm_resp_time": 3,
        "alarm_resistant_factor": 2,
        "alarm_resistant_factor_gsd": 80,
        "sensitivity": 128
    }
}
