from scipy.signal import butter, lfilter, iirnotch
import scipy.signal
import numpy as np

'''
 Class of different filters that can be applied to the data.
'''

class FiltersGalore:

  def butter_bandpass(self, lowcut, highcut, fs, order=5):
      nyq = fs / 2;
      low = lowcut / nyq
      high = highcut / nyq
      b, a = butter(order, [low, high], btype='band')
      return b, a

  def butter_bandpass_filter(self, data, lowcut, highcut, fs, order=5):
      b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
      y = lfilter(b, a, data)
      return y

  def notch_it(self, f0, fs, order=5):
      lo = f0 - 2;
      hi = f0 + 2;
      bs = np.array([lo, hi]);
      w0 = bs/(fs/2) # Normalize freq
      b, a = butter(order, w0, 'bandstop');
      return b, a

  def notch_filter(self, data, cut, fs, order=5):
      b, a = self.notch_it(cut, fs, order)
      y = lfilter(b, a, data)
      return y
