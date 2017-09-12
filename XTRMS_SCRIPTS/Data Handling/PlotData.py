import matplotlib
import matplotlib.pyplot as plt

class PlotData:
    '''
    data is a pandas data structure.
    Column names: SN - Sample number
                  CN - channel N (N = 1, ..., 8)
    '''
    def __init__(self, data):
        self.data = data;

    def plotSingleChannel(self, channel):
        plt.plot(self.data[channel]);
        plt.show();

    def plotSingleChannelAndFFT(self, channel, Y, frq):

        fig, ax = plt.subplots(2, 1)
        ax[0].plot(channel);
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Amplitude')
        ax[1].plot(frq, abs(Y),'r') # plotting the spectrum
        ax[1].set_xlabel('Freq (Hz)')
        ax[1].set_ylabel('|Y(freq)|')
        plt.show()
