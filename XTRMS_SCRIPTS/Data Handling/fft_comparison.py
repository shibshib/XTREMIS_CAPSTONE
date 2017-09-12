import argparse
from math import log10

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.integrate as integrate
from scipy.signal import detrend

from bsparser import load_as_df


parser = argparse.ArgumentParser()
parser.add_argument('fname')
args = parser.parse_args()
fname = args.fname

srate = 1024
freq = fname[3:6]
rms = fname[9:12]
SNR_WINDOW = 5 # how many Hz around max PSD to look for SN

f, axarr = plt.subplots(2, 2)

sns.set(style="whitegrid")

def get_snr(ps, freqs):

    ps_tmp = ps.copy()
    ps_tmp[np.where(np.logical_and(freqs > 55, freqs < 65))] = 0
    maxfreq = freqs[np.where(ps == max(ps_tmp))]

    window = np.where(np.logical_and(freqs > maxfreq * 0.975, freqs < maxfreq *1.025))

    s = integrate.cumtrapz(ps[window]**2)[-1]
    n = integrate.cumtrapz(ps**2)[-1] - s

    return maxfreq, 10*log10(s / n)

def remove_outliers(ts, cut=2.5):

    zscore = (ts - ts.mean()) / ts.std()
    nremoved = 0
    while any(abs(zscore) > cut):

        for idx in np.where(abs(zscore) > cut):
            nremoved += 1
            ts[idx] = (ts[idx+1] + ts[idx-1]) / 2

        zscore = (ts - ts.mean()) / ts.std()

    print("Removed %s samplePs " % nremoved)
    return ts, nremoved


for i in range(2):

    # Load data file
    if i == 0:
        ext = 'TXT'
        name = "XTREMIS"
    else:
        ext = 'bdf'
        name = "BIOSEMI"

    print("Doing %s" % name)

    x = load_as_df('%s.%s' % (fname, ext))
    data = x[x.columns[0]].values
    # keep 10 to 70 seconds
    data = data[10*1024:70*1024]

    # remove xtreme outliers
    data, nremoved = remove_outliers(data)

    # remove inf / nan
    data = data[np.logical_not(np.isnan(data))]
    data = data[np.logical_not(np.isinf(data))]
    data = detrend(data)

    # normalize
    data = data / max(abs(data))
    data = data - np.mean(data)

    print("mean:", np.mean(data))
    print("RMS:", np.sqrt(np.mean(np.square(data))))

    # do fft
    print("\tDoing FFT..")
    times = np.linspace(0, len(data)/srate, len(data))
    time_step = 1 / srate
    ps = np.abs(np.fft.fft(data))
    freqs = np.fft.fftfreq(data.size, time_step)
    idx = np.argsort(freqs)

    # plot only > 10 Hz
    idx = idx[freqs[idx] > 0.1]
    freqs = freqs[idx]
    ps = ps[idx]
    ps = ps / max(ps)

    # calculate snr
    sns.set(style="whitegrid")

    f, snr = get_snr(ps, freqs)
    print("SD:", np.std(ps))
    print("SNR @ %s Hz of %s: %s" % (f[0], name, snr))

    #sns.tsplot(data[4096:5121], time=times[0:1025], ax=axarr[0,i])
    axarr[0, i].plot(times[0:4097], data[4096:8193])
    axarr[0,i].set_ylim([-1, 1])
    #axarr[0, i].grid(b=True, axis='y', linestyle='solid', color='grey')
    axarr[0, i].set_title("%s %suV (%s Hz)" % (name, rms, freq))
    axarr[0, i].set_xlabel("Time (s)")
    axarr[0, i].set_ylabel("Normalized Voltage")

    #sns.tsplot(ps, time=freqs, ax=axarr[1, i])
    axarr[1, i].plot(freqs, ps)
    #axarr[1, i].grid(b=True, axis='y', linestyle='solid', color='grey')
    axarr[1, i].set_title("%s PSD" % name)
    axarr[1, i].set_xlabel("Frequency (Hz)")
    axarr[1, i].set_ylabel("Normalized PSD")

   # with open('../data/fft.csv', 'a') as _:

    #    _.write("\n%s,%s,%s,%s,%s,%s,%s,%s" % (freq, rms, name, nremoved, f[0], np.std(ps), np.sqrt(np.mean(np.square(data))), snr))



plt.tight_layout()
plt.show()
#plt.savefig("../data/fig/%s.png" % fname)
