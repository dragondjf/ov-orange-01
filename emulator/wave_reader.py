# -*- coding: utf-8 -*-
import time
import wave
import glob
import struct
import random
import functools
import datetime
import numpy as np
from config import opt, Config


class WaveReader(object):
    def __init__(self, stream, send_err, file_path, test):
        self.stream = stream
        self.send_err = send_err
        self.file_path = file_path
        self.test = test

    def fft_process(self, raw_data, win_setting):
        dmin = min(raw_data)
        dmax = max(raw_data)
        davg = np.mean(raw_data)

        fft_data = np.fft.fft(raw_data)
        fft_size = Config.get('fft_size')
        fft = np.abs(fft_data[0:fft_size / 2]) / (fft_size / 2)
        fft[0] = fft[0] / 2  # 基频仅需除以FFTSIZE
        freq_val = []
        win_set = [{'begin': 0, 'end': 0, 'noise': 0}] * len(win_setting)
        for n in xrange(len(win_setting)):
            dfreq = 0
            win_set[n]["begin"] = win_setting[n][0]
            win_set[n]["end"] = win_setting[n][1]
            win_set[n]["noise"] = win_setting[n][2]

            fft_begin = win_set[n]["begin"] - 1
            fft_end = win_set[n]["end"]
            fft_noise = win_set[n]["noise"]
            tfft = np.array(fft[fft_begin:fft_end]) - fft_noise
           #计算和
            dfreq = np.sum(tfft[tfft > 0])
            freq_val.append(int(dfreq))
        return dmin, dmax, davg, freq_val

    def dataProcess(self, packet, win_settings):
        import pkg
        raw_data_1 = ''
        raw_data_2 = ''
        for d in packet[:512]:
            raw_data_1 = raw_data_1 + struct.pack('>H', d)
        for d in packet[512:1025]:
            raw_data_2 = raw_data_2 + struct.pack('>H', d)

        l1 = len(raw_data_1)
        raw_header1 = pkg.Header(
            length=l1,
            cmd=pkg.NOTIFY_RAW_DATA,
            channel=1
        ).pack_hdr()
        raw_header2 = pkg.Header(
            length=l1,
            cmd=pkg.NOTIFY_RAW_DATA,
            channel=2
        ).pack_hdr()

        raw1_1 = raw_header1 + raw_data_1
        raw1_2 = raw_header1 + raw_data_2
        raw2_1 = raw_header2 + raw_data_1
        raw2_2 = raw_header2 + raw_data_2

        pre_bodies = []
        for ch in (0, 1):
            dmin, dmax, davg, dfreq = self.fft_process(
                packet,
                win_settings[ch]
            )
            freq_buf = [150, ] * 8
            for n in xrange(8):
                if n <= (len(win_settings[ch]) - 1):
                    freq_buf[n] = dfreq[n]
                else:
                    freq_buf[n] = 0
            body = pkg.PrepareSimplingData(
                max=int(dmax),
                min=int(dmin),
                avg=int(davg),
                data=struct.pack('>8L', *freq_buf)
            ).pack()
            pre_bodies.append(body)

        pre_pkg1 = pkg.Header(
            length=len(pre_bodies[0]),
            cmd=pkg.NOTIFY_PREPARE_SIMPLING_DATA,
            channel=1,
            data=pre_bodies[0]
        )
        pre_pkg2 = pkg.Header(
            length=len(pre_bodies[1]),
            cmd=pkg.NOTIFY_PREPARE_SIMPLING_DATA,
            channel=2,
            data=pre_bodies[1]
        )
        pre1 = pre_pkg1.pack()
        pre2 = pre_pkg2.pack()

        channel_1_buf = [raw1_1, raw1_2, pre1]
        channel_2_buf = [raw2_1, raw2_2, pre2]
        return channel_1_buf, channel_2_buf

    def send(self, *chs):
        for i, ch in enumerate(chs):
            mode = Config.get(i + 1, 'mode')
            buf = None
            if mode == opt.PreProcessing:
                buf = ch[2]
            elif mode == opt.RawData:
                buf = ch[0] + ch[1]
            elif mode == opt.MixMode:
                buf = ch[0] + ch[1] + ch[2]
            if not self.stream.closed() and buf:
                if self.send_err:
                    buf_cmd = str(random.randint(1, 4))
                    buf_ret = str(random.randint(1, 4))
                    buf_ch = str(random.randint(0, 2))
                    buf_header = '00303%s0%s0%sff' % (buf_cmd, buf_ret, buf_ch)

                    buf_body = ''.join([
                        '01ab0157017000ff00ff00ff00ff00ff0000000000000000',
                        '000000000000000000000000000000000000000000000000'
                    ])

                    buf_new = (buf_header + buf_body).decode("hex")

                    if time.localtime()[5] % 10 > 0:
                        buf = buf_new
                self.stream.write(buf)

    def start_send(self, gen):
        try:
            chs = gen.next()
        except:
            return
        self.send(*chs)
        callback = functools.partial(self.start_send, gen)
        self.stream.io_loop.add_timeout(
            datetime.timedelta(seconds=0.2),
            callback
        )

    def load_file(self):
        while True:
            for filename in glob.glob(self.file_path + "/*.wav"):
                wav_file = wave.open(filename)
                framenum = wav_file.getnframes()

                data = wav_file.readframes(framenum)
                package = list(struct.unpack('h' * framenum, data))
                for i in range(len(package) / 1024):
                    packet = package[i * 1024:(i + 1) * 1024]

                    packet = [(d + 32768) / 16 for d in packet]
                    channel_1_data, channel_2_data = self.dataProcess(
                        packet,
                        (
                            Config.get(1, 'win_settings'),
                            Config.get(2, 'win_settings')
                        )
                    )
                    yield (channel_1_data, channel_2_data)
                wav_file.close()
            if self.test:
                print "wav read over"
                break

    def run(self):
        chs = self.load_file()
        self.start_send(chs)
