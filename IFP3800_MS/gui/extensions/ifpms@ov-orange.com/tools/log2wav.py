#!/usr/bin/env python
# -*- coding: UTF8 -*-
import wave
import logging
import os
import glob
import struct
import re
import time

class Log2Wav:
    def f_id(self, f_id):
        return int(f_id[13:])

    def FileFilter(self):
        pattern = '^.*packet\.log\.\d+$'
        filenames = []
        for filename in glob.glob('./*'):
            if re.search(pattern,filename):
                filenames.append(filename)
            else:
                pass
        filenames.sort(key = self.f_id, reverse = True)
        return filenames

    def DataWrite(self,data_list,wav_file):
        data = data_list
        if data[2] == 'Recv':
            log_data = data[3].split(' ')
            log_data = log_data[6:]
            package = [int(t,16) for t in log_data]
            for x in xrange(512):
                new_data = (package[2 *x ] * 256 + package[2 * x + 1]) * 16 -32768
                packet = struct.pack('h', new_data)
                wav_file.writeframes(packet)

    def judge(self):
        filenames = self.FileFilter()
        last_t_stamp = 0
        for filename in filenames:
            file_name = open(filename)
            for line in file_name:
                data = line.split('|')
                if data[1] == '192.168.100.101' or data[3][13] == '2':
                    continue
                elif data[1] == '192.168.100.100' and data[3][13] == '1':
                    t_stamp = time.mktime(time.strptime(data[0][:19],"%Y-%m-%d %H:%M:%S"))       #current file's beginning time
                    if t_stamp - last_t_stamp == 60 or data[0][17:19] == '00':
                        if int(data[0][20:]) < 100:
                            new_filename = data[1] + '-' + data[3][13] + '-' + data[0][2:4] + data[0][5:7] + data[0][8:10] + '-' + data[0][11:13] + data[0][14:16] + '.wav'
                            last_t_stamp = t_stamp            #last file's beginning time
                            wav_file = wave.open(new_filename, 'w')
                            wav_file.setparams((1, 2, 5120, 0, 'NONE', 'not compressed'))
                        else:
                            pass
                    elif t_stamp - last_t_stamp < 60:
                        pass
                    elif t_stamp - last_t_stamp >= 61:
                        continue
                    self.DataWrite(data, wav_file)
            file_name.close()
            os.rename(filename,filename+'.handled')
        return

if __name__ == '__main__':
    log_change_wav = Log2Wav()
    log_change_wav.judge()
