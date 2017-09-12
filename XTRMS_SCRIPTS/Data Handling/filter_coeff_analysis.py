import matplotlib.pyplot as plt
import numpy as np
from scipy import signal


##################################################################
#
#
# Sandbox script to play with filter coefficients and extract them 
# to place in XTREMIS GUI to run in real time. 
#
#
#################################################################

# assumed sample rate of XTREMIS
fs_Hz = 1024.0

# create the 60 Hz filter
bp_stop_Hz = np.array([15.0, 18.0])
b, a = signal.butter(2,bp_stop_Hz/(fs_Hz / 2), 'bandstop')

# create the 50 Hz filter
bp2_stop_Hz = np.array([28, 31.0])
b2, a2 = signal.butter(2,bp2_stop_Hz/(fs_Hz / 2), 'bandstop')

# compute the frequency response
w, h = signal.freqz(b,a,3000)
w2, h2 = signal.freqz(b2,a2,3000)
f = w * fs_Hz / (2*np.pi)             # convert from rad/sample to Hz

plt.plot(f, 20*np.log10(abs(h)), 'b.-', label="Notch (60 Hz)");
plt.plot(f, 20*np.log10(abs(h2)), 'r.-', label="Notch (50 Hz)");
plt.xlim([0, 40])
plt.xlabel("Frequency (Hz)");
plt.ylabel("Response (dB)");
plt.legend()
#plt.ylim([-60, 0])
plt.grid()
plt.show()

# 60 Hz coefficients
np.set_printoptions(precision=16)
print("16 Hz Coefficients")
print(repr(b))
print(repr(a))

# 50 Hz Coefficients
print("20 Hz Coefficients")
print(repr(b2))
print(repr(a2))
'''
# assumed sample rate of OpenBCI
fs_Hz = 800.0

# create the 60 Hz filter
bp_stop_Hz = np.array([59.0, 61.0])
b, a = signal.butter(2,bp_stop_Hz/(fs_Hz / 2), 'bandstop')

# create the 50 Hz filter
bp2_stop_Hz = np.array([49, 51.0])
b2, a2 = signal.butter(2,bp2_stop_Hz/(fs_Hz / 2), 'bandstop')

# compute the frequency response
w, h = signal.freqz(b,a,1000)
w2, h2 = signal.freqz(b2,a2,1000)
f = w * fs_Hz / (2*np.pi)             # convert from rad/sample to Hz

#plt.plot(f, 20*np.log10(abs(h)), 'b.-', label="Notch (60 Hz)");
#plt.plot(f, 20*np.log10(abs(h2)), 'r.-', label="Notch (50 Hz)");
#plt.xlim([40, 70])
#plt.xlabel("Frequency (Hz)");
#plt.ylabel("Response (dB)");
#plt.legend()
#plt.ylim([-60, 0])
#plt.grid()
#plt.show()

# 60 Hz coefficients
np.set_printoptions(precision=16)
print("60 Hz Coefficients")
print(repr(b))
print(repr(a))

# 50 Hz Coefficients
print("50 Hz Coefficients")
print(repr(b2))
print(repr(a2))


# Create BP Filters
# assumed sample rate of OpenBCI
fs_Hz = 800.0


# create the 1 - 50 Hz filter
bp_range_Hz = np.array([1.0, 50.0])
b, a = signal.butter(2, bp_range_Hz/(fs_Hz / 2), btype='bandpass')
# compute the frequency response
w, h = signal.freqz(b,a,1000)
f = w * fs_Hz / (2*np.pi)

# create the 7 - 13 Hz filter
bp_range_Hz2 = np.array([7.0, 13.0])
b2, a2 = signal.butter(2, bp_range_Hz2/(fs_Hz / 2), btype='bandpass')
# compute the frequency response
w2, h2 = signal.freqz(b2,a2,1000)
f2 = w2 * fs_Hz / (2*np.pi)

# create the 15 - 50 Hz filter
bp_range_Hz3 = np.array([15.0, 50.0])
b3, a3 = signal.butter(2, bp_range_Hz3/(fs_Hz / 2), btype='bandpass')
# compute the frequency response
w3, h3 = signal.freqz(b3,a3,1000)
f3 = w3 * fs_Hz / (2*np.pi)

# create the 5 - 50 Hz filter
bp_range_Hz4 = np.array([5.0, 50.0])
b4, a4 = signal.butter(2, bp_range_Hz4/(fs_Hz / 2), btype='bandpass')
# compute the frequency response
w4, h4 = signal.freqz(b4,a4,1000)
f4 = w4 * fs_Hz / (2*np.pi)

#plt.plot(f,abs(h), 'b-', label="BP (1 - 50 Hz)");
#plt.plot(f2,abs(h2), 'r-', label="BP (17 - 13 Hz)");
#plt.plot(f3,abs(h3), 'm-', label="BP (15 - 50 Hz)");
#plt.plot(f4,abs(h4), 'm-', label="BP (5 - 50 Hz)");
#plt.plot(f, 20*np.log10(abs(h2)), 'r.-', label="BP (7 - 13 Hz)");
#plt.xlim([0, 200])
#plt.xscale('log')
#plt.xlabel("Frequency ([rad/sec])");
#plt.ylabel("Gain");
#plt.legend()
#plt.grid()
#plt.ylim([-60, 0])

np.set_printoptions(precision=16)

print("1 - 50 Hz Coefficients")
print(repr(b))
print(repr(a))

print("7 - 13 Hz Coefficients")
print(repr(b2))
print(repr(a2))

print("15 - 50 Hz Coefficients")
print(repr(b3))
print(repr(a3))

print("5 - 50 Hz Coefficients")
print(repr(b4))
print(repr(a4))

plt.show()
'''
