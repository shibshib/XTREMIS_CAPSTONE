import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from scipy.signal import correlate, detrend
from fastdtw import fastdtw

from bsparser import load_as_df

def match_sizes(arr1, arr2):
    diff = abs(len(arr1) - len(arr2));
    if (len(arr1) > len(arr2)):
        arr1 = arr1[:-diff];
    elif (len(arr1) < len(arr2)):
        arr2 = arr2[:-diff];

    return arr1, arr2

x = load_as_df('../data/xtrms/s1_data/resting_s1_conv.TXT')
y = load_as_df('../data/xtrms/s1_data/resting_s1.bdf')


# remove xtreme outliers
zscore = (x - x.mean()) / x.std()
x = x[abs(zscore) < 2]


# normalize
#x = (x - x.mean()) / (x.max() - x.min())
#y = (y - y.mean()) / (y.max() - y.min())

for i in range(8):

    ch1 = x[x.columns[i]][np.logical_not(np.isnan(x[x.columns[i]]))]
    ch2 = y[y.columns[i]][np.logical_not(np.isnan(y[y.columns[i]]))]

    ch1 = ch1[np.logical_not(np.isinf(ch1))]
    ch2 = ch2[np.logical_not(np.isinf(ch2))]

    #ch1 = detrend(ch1)
    #ch2 = detrend(ch2)

    # trim to 90% of data
    cut = int(0.05 * len(ch1))
    ch1 = ch1[cut:len(ch1)-cut]

    cut = int(0.05 * len(ch2))
    ch2 = ch2[cut:len(ch2)-cut]



    # match sizes
    maxres = 0
    for j in range(-5*1024, 5*1024):

        if j < 0:
            ch1_t, ch2_t = match_sizes (ch2[-j:], ch1[:20480])
            res = np.corrcoef(ch1_t, ch2_t)
        else:
            ch1_t, ch2_t = match_sizes (ch2[:20480], ch1[j:])
            res = np.corrcoef(ch1_t, ch2_t)

        if abs(res[1,0]) > maxres:
            maxres = abs(res[1,0])
            maxlag = j

    print(maxres)
    ch1_t, ch2_t = match_sizes (ch2, ch1)
    res = np.corrcoef(ch1_t, ch2_t)
    print("Basic Correlation %s: " % (i+1), abs(res[1, 0]));

    if maxlag < 0:
        ch1_t, ch2_t = match_sizes (ch2[-maxlag:], ch1)
        res = np.corrcoef(ch1_t, ch2_t)
    else:
        ch1_t, ch2_t = match_sizes (ch2, ch1[maxlag:])
        res = np.corrcoef(ch1_t, ch2_t)
    #print(res);

    print("Lagged Correlation %s: " % (i+1), abs(res[1, 0]));
    print("Lag: ", maxlag)

    #distance, path = fastdtw(ch1, ch2, dist=euclidean);
    #print("DTW: ", distance);
