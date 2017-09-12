import argparse
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

def get_snr(ps, freqs, sig, border=2):


    window = np.where(np.logical_and(freqs > sig - border, freqs < sig +  border))

    s = integrate.cumtrapz(ps[window]**2)[-1]
    n = integrate.cumtrapz(ps**2)[-1] - s

    return 10*log10(s / n)

def remove_outliers(ts, cut=3.5):
    #median_t = np.median(ts);
    #median_abs_dev = np.median(abs(ts - median_t));
    #zscore = np.asarray([0.6745 * (ts - median_t) / median_abs_dev])

    zscore = (ts - ts.mean()) / ts.std()
    nremoved = 0
    while any(abs(zscore) > cut):

        outliers = np.where(abs(zscore) > cut)
        del ts[outliers]
        for idx in outliers[0]:
            nremoved += 1


            """
            if idx > 0 and idx < len(ts)-1:
                ts[idx] = (ts[idx+1] + ts[idx-1]) / 2
            elif idx == 0:
                ts[idx] = ts[1]
            elif idx > 0:
                ts[idx] = ts[idx-1]
            """


        zscore = (ts - ts.mean()) / ts.std()

    print("Removed %s samples " % nremoved)
    return ts, nremoved


parser = argparse.ArgumentParser()
parser.add_argument('srate')
parser.add_argument('fname')
args = parser.parse_args()

srate = int(args.srate)
fname = args.fname

filename = path.split(fname)[1]
ext = path.splitext(fname)[1]
sig = int(filename.split("_")[1][:-2]) # incoming signal

if ext == '.TXT':
    name = "XTREMIS"
else:
    name = "BIOSEMI"


# Load data file
print("Doing %s" % name)

data = load_as_df(fname, srate=srate, filt=False)


#FG = FiltersGalore()
#data = FG.notch_filter(data, 60, srate, order=2);
#data = FG.notch_filter(data, 1047, srate, order=3);


# remove inf / nan
#data = data[np.logical_not(np.isnan(data))]
#data = data[np.logical_not(np.isinf(data))]
#data = detrend(data)


# normalize
data = data / max(abs(data))
data = data - np.mean(data)

# do fft
print("\tDoing FFT..")
times = np.linspace(0, len(data)/srate, len(data))
stepper = srate/(sig*10)
time_step =  1 / (srate)

ps = np.abs(np.fft.fft(data))
freqs = np.fft.fftfreq(data.size, time_step)
idx = np.argsort(freqs)

# plot only > 0.1 Hz
idx = idx[freqs[idx] > 0.1]
freqs = freqs[idx]
ps = ps[idx]
ps = ps / max(ps)

# calculate snr
sns.set(style="whitegrid")

snr = get_snr(ps, freqs, sig)
print("SD:", np.std(ps))
print("SNR @ %s Hz of %s: %s" % (sig, name, snr))

# alternative SNR because its an AUDIO signal
chn = data;
norm = chn / max(np.amax(chn), -1 * np.amin(chn));
print("Alt SNR @ %s Hz of %s: %s" % (sig, name, stats.signaltonoise(norm)));

f, axarr = plt.subplots(2)

sns.set(style="whitegrid")

#sns.tsplot(data[4096:5121], time=times[0:1025], ax=axarr[0])
#axarr[0].plot(times[0:4097], data[0:4097])
axarr[0].plot(times, data)
#axarr[0].plot(times[:8000], data[:8000])
axarr[0].set_ylim([-1, 1])
#axarr[0].grid(b=True, axis='y', linestyle='solid', color='grey')
axarr[0].set_title("%s (%s Hz)" % (name, sig))
axarr[0].set_xlabel("Time (s)")
axarr[0].set_ylabel("Normalized Voltage")
#axarr[0].set_xlim([0, 0.15])

#sns.tsplot(ps, time=freqs, ax=axarr[1])
axarr[1].plot(freqs, ps)
#axarr[1, i].grid(b=True, axis='y', linestyle='solid', color='grey')
axarr[1].set_title("%s PSD" % name)
axarr[1].set_xlabel("Frequency (Hz)")
axarr[1].set_ylabel("Normalized PSD")

# with open('../data/fft.csv', 'a') as _:

#    _.write("\n%s,%s,%s,%s,%s,%s,%s,%s" % (freq, rms, name, nremoved, f[0], np.std(ps), np.sqrt(np.mean(np.square(data))), snr))


plt.tight_layout()
plt.show()
#plt.savefig("/home/joey/projects/xtremis/XTRMS/data/fig/%s.png" % sig)
