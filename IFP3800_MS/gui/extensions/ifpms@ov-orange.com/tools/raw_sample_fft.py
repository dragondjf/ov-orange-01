# -*- coding: utf-8 -*-

import os
import glob
from pylab import figure, show, savefig, title, close
import numpy as np

fft_base = 300

path = '.'
for infile in glob.glob( os.path.join(path, '*.txt') ):
    print "current file is: " + infile
    file=open(infile)
    data = [ float(x) for x in file.readlines() ]
    file.close()

    #����ԭʼ����Ƶ��
    data = data[::3]

    print "point number is %d"%len(data)

    fig = figure(figsize=(48, 64))

    for m in [10240]:
        print "fft size is %d"%m
        
        rows = len(data)/m + 1
        
        #ԭʼ����
        ax = fig.add_subplot(rows,1,1)
        ax.axis([1,len(data), 0.2, 1.6])
        ax.plot(data) #all data


        #��ÿ��m���ڵ���зֶ�
        for n in xrange(len(data)/m):
            print "point [%d-%d] "%(n*m,(n+1)*m)


            #��n��ԭʼ����
            ax = fig.add_subplot(rows,3,(n+1)*3+1)
            ax.axis([1,m, 0.2, 1.6])
            ax.plot(data[n*m:(n+1)*m]) #all data

            xf = np.fft.fft(data[n*m:(n+1)*m])

            #��n��fftƵ��
            ax = fig.add_subplot(rows,3,(n+1)*3+2)
            ax.axis([0, len(xf)/2-1, 0, 100])
            ax.plot(np.abs(xf[1:m/2-1]))

            #��n��fftƵ��, y��Ŵ�
            ax = fig.add_subplot(rows,3,(n+1)*3+3)
            ax.axis([0, len(xf)/2-1, 0, 30])
            ax.plot(np.abs(xf[1:m/2-1]))

            #show()
            #print "save file: " + infile + ".%06d.%02d.png"%(m,n)

        savefig(infile+".%06d.png"%(m), dpi=75)
        close()

        print "save file: " + infile + ".%06d.png"%m
