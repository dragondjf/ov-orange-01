#!/usr/bin/env python
#-*-coding:utf-8-*-
import struct
import os
import wx
import glob
import wave
import time
import numpy as np

#import pylab as pl
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


#读取声音文件
def wavread(file):
    '''
    读取指定的ffile,返回声音数据，采样率，数据点数
    '''
    f=wave.open(file,u'rb')
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    str_data = f.readframes(nframes)
    f.close()
    wave_data = np.fromstring(str_data, dtype=np.short)
    return wave_data,framerate,sampwidth*8,nframes


def fft_bandpass(wave_data,M,L):
    '''
    对读取的数据wave_data进行M-L间频率的带通滤波（包括M,L）
    返回滤波后的信号
    '''
    fft_wavedata=np.fft.fft(wave_data)
    N=len(wave_data)
    H=np.zeros(N)
    H[M:(L+1)]=1
    H[N-L-1:N-M]=1 
    y=fft_wavedata*H
    xd=np.fft.ifft(y)
    xd=xd.real
    return xd


if __name__ == '__main__':
    t1=time.time()
    x,fs,bits,N=wavread(u"纪山0114.0222.688下雨.wav")
    xd=np.zeros(N)
    for i in range(3,N-3):
        #xd[i]=(x[i-2]+4*x[i-1]+6*x[i]+4*x[i+1]+x[i+2])/16  #五点重心法
        #xd[i]=(x[i-3]+6*x[i-2]+15*x[i-1]+20*x[i]+15*x[i+1]+6*x[i+2]+x[i+3])/64 #七点重心法
        xd[i]=(x[i-1]+2*x[i]+x[i+1])/4  #三点重心法
    #xd=fft_bandpass(x,1,1000)
    xd = xd.astype(np.short)
    f = wave.open(r"ChangeWav.wav", "wb")
    # 配置声道数、量化位数和取样频率
    f.setnchannels(1) 
    f.setsampwidth(2)
    f.setframerate(fs)
    # 将wav_data转换为二进制数据写入文件
    f.writeframes(xd.tostring())
    f.close()
    t2=time.time()
    t=t2-t1