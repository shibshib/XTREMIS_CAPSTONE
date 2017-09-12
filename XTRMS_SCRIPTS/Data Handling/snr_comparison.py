from math import log10
from os import path

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.integrate as integrate
from scipy.signal import detrend
import scipy.stats as stats
#from FiltersGalore import FiltersGalore
from bsparser import load_as_df, load_xtremis
import pandas as pd
import sys
import csv

csv.field_size_limit(sys.maxsize)

def find_pointy_bit(ps, freqs, maxf, thresh=0.15): 


    # find lower edge
    maxloc = np.where(ps == max(ps))
    maxloc = maxloc[0][0]
    i = maxloc - 1
    while (sum(ps[i:maxloc]) / len(ps[i:maxloc])) > thresh and i > 0:
        i -= 1

    lo_f = freqs[i]

    i = maxloc + 1
    while sum(ps[maxloc:i]) / len(ps[maxloc:i]) > thresh and i < len(ps) -1:
        i += 1

    hi_f = freqs[i]

    return lo_f, hi_f

    #np.logical_and(freqs > low_f, freqs < hi_f)


def get_snr(ps, freqs, hi_f, lo_f):


    window = np.where(np.logical_and(freqs > lo_f, freqs < hi_f))

    s = integrate.cumtrapz(ps[window]**2)[-1]
    n = integrate.cumtrapz(ps**2)[-1] - s

    return 10*log10(s / n)


df = pd.DataFrame(columns=['srate', 'signal', 'spread', 'system', 'shift', 'snr'])


srates = [1000]
FREQS = [10, 50, 100, 150, 200, 250]

pairs = [(i, j) for i in srates for j in FREQS]

for srate, f in pairs:
    fname = 'data/snr_graphs/sg_%sHz_1ksps_conv.TXT' % f

    data = load_as_df(fname, srate=srate)

    # normalize
    data = data / max(abs(data))
    data = data - np.mean(data)


    slices = range(0, len(data), len(data)//5 - 1)
    sliced_data = [ data[slices[i]:slices[i+1]] for i in range(len(slices) - 1) ]

    for this_data in sliced_data:
        # do fft
        print("\tDoing FFT..")
        times = np.linspace(0, len(this_data)/srate, len(this_data))
        #stepper = srate/(sig*10)
        time_step =  1 / (srate)

        ps = np.abs(np.fft.fft(this_data))
        freqs = np.fft.fftfreq(this_data.size, time_step)
        idx = np.argsort(freqs)

        # plot only > 0.1 Hz
        idx = idx[freqs[idx] > 0.1]
        freqs = freqs[idx]
        ps = ps[idx]
        ps = ps / max(ps)

        point = np.where(ps == max(ps))
        maxf = freqs[point][0]
        

        lo_f, hi_f = find_pointy_bit(ps, freqs, maxf)
        peak_width = hi_f - lo_f

        snr = get_snr(ps, freqs, hi_f, lo_f)

        print("\n" * 2)
        print('peak @ %s' % maxf)
        print('peak width %s' % peak_width)
        print('snr: %s' % snr)
        print(lo_f, hi_f)
        print("\n" * 2)
        
        this_row = {
            'srate': float(srate),
            'signal': float(f),
            'system': 'xtremis',
            'spread': 100*(hi_f - lo_f) / f,
            'shift': 100*(maxf - f) / f,
            'snr': snr
        }

        df = df.append(this_row, ignore_index=True)


        #fig, axarr = plt.subplots(1)
       # axarr.plot(freqs, ps)
        #axarr.set_title("%s PSD" % srate)
        #axarr.set_xlabel("Frequency (Hz)")
        #axarr.set_ylabel("Normalized PSD")
        #plt.show()

sns.set(style="darkgrid", font_scale=2)
#palette="YlGnBu_d",
fig, ax = plt.subplots()
fig.set_size_inches(18.5, 10.5)
lm = sns.regplot(x='signal', y='shift', data=df, ci=95, x_estimator=np.mean, scatter_kws={"s": 100})
plt.gca().xaxis.grid(True)

lm.set(ylim=(3, 5), xlim=(0, 256), xlabel='Input Signal (Hz)', ylabel='Signal Shift (%)')
#plt.savefig("/home/joey/xt_shift.png")
#plt.figure(figsize=(8,6))
plt.show()

lm = sns.regplot(x='signal', y='snr', data=df, ci=95, x_estimator=np.mean,scatter_kws={"s": 100})
plt.gca().xaxis.grid(True)

lm.set(ylim=(0, 30), xlim=(0, 256), xlabel='Input Signal (Hz)', ylabel='SNR (dB)')
#plt.savefig("/home/joey/xt_snr.png")
plt.show()

lm = sns.regplot(x='signal', y='spread', data=df, ci=95, x_estimator=np.mean,scatter_kws={"s": 100})
plt.gca().xaxis.grid(True)

lm.set(ylim=(0, 40), xlim=(0, 256), xlabel='Input Signal (Hz)', ylabel='Signal Spread (%)')
#plt.savefig("/home/joey/xt_spread.png")

# set figure size
#plt.figure(figsize=(8,6))
plt.show()

#plt.xlim([0, 225])
#plt.ylim([0, 20])
