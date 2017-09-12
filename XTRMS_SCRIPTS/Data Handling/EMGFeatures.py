
#########################################################################
#
# This is a class that contains functions to extract features and generate
# feature vector for EMG data
#
#########################################################################
import numpy as np
from numpy.linalg import lstsq


class EMGFeatures:

    ############################################################################
    # Mean Absolute Value
    # Computes the MAV of a given channel
    # Specify channel using dim variable.
    # INPUT:    data - EMG/Accel data
    #           dim  - The dimension of the data
    #                 (channels for EMG, (x,y,z) for accel)
    #
    # OUTPUT:   MAV for given data set
    ############################################################################
    def mav(self, data, dim):
        meandat = data[dim,:].mean()
        val = 0;
        count = 0;
        for i in range(0, len(data[dim])):
            val += abs(data[dim, i] - meandat)
            count += 1
        return (val / count)

    ############################################################################
    # Zero Crossings
    # Computes the number of ZCs of a given channel
    # Specify channel using dim variable.
    # INPUT:    data        - EMG/Accel data
    #           dim         - The dimension of the data
    #                         (channels for EMG, (x,y,z) for accel)
    #           Threshold   - Threshold for which to discard data
    #
    # OUTPUT:   ZC for given data set
    ############################################################################
    def zero_crossings(self, data, dim, threshold):
        ZC = 0
        for i in range(0, len(data[dim])-1):
            sample1 = abs(data[dim, i+1] - data[dim,i]);
            sample2 = max(abs(data[dim, i+1] + data[dim,i]), threshold)
            if sample1 > sample2:
                ZC = ZC + 1
        return ZC

    ############################################################################
    # Sign Slope Changes
    # Computes the number of SSCs of a given channel
    # Specify channel using dim variable.
    # INPUT:    data        - EMG/Accel data
    #           dim         - The dimension of the data
    #                         (channels for EMG, (x,y,z) for accel)
    #           Threshold   - Threshold for which to discard data
    #
    # OUTPUT:   SSC for given data set
    ############################################################################
    def sign_slope_changes(self, data, dim, threshold):
        SSC = 0
        for i in range(1, len(data[dim])-1):
            prev_point = data[dim, i-1];
            cur_point  = data[dim, i];
            next_point = data[dim, i+1];

            cond1 = cur_point > max(prev_point, next_point)
            cond2 = cur_point < min (prev_point, next_point)
            cond3 = max(abs(next_point - cur_point),abs(cur_point - prev_point)) > threshold

            if cond1 or cond2 and cond3:
                SSC = SSC + 1

        return SSC

    ############################################################################
    # Waveform Length
    # Computes the Waveform Length of a given channel
    # Specify channel using dim variable.
    # INPUT:    data        - EMG/Accel data
    #           dim         - The dimension of the data
    #                         (channels for EMG, (x,y,z) for accel)
    #
    # OUTPUT:   WL for given data set
    ############################################################################
    def waveform_length(self, data, dim):
        WL = 0;
        for i in range(1, len(data[dim])):
            WL += abs(data[dim, i] - data[dim, i-1]);
        return WL;

    #############################################################################
    # Root Mean Square (RMS)
    # Computes the root mean square of a given channel
    # Specify channel using dim variable
    # INPUT : data      - EMG/Accel data
    #         dim       - Dimension of the data
    #
    # OUTPUT:   RMS for given data set
    #############################################################################
    def root_mean_square(self, data, dim):
        return np.sqrt(np.mean(data[dim]**2));

    ############################################################################
    #
    # First Order Differential
    # Computes the first order difference of a time series
    #
    # For a time series X = [x(1), x(2), ..., x(N)], its first order difference
    # is: Y = [x(2) - x(1), x(3) - x(2), ..., x(N) - x(N-1)]
    ############################################################################
    def first_order_diff(self, X):
        Y=[]
        for i in range(1, len(X)):
            Y.append(X[i]-X[i-1])
        return Y

    ############################################################################
    # Hjorth Parameters
    # Computes Hjorth mobility and complexity of a time series from either
    # of the two cases below:
    #       1. X, time series of type list (default)
    #       2. D, a first order differential sequence of X (if D is provided..
    #          good for speeding things up)
    # In case 1, D is computed by first_order_diff(X) function.
    # INPUT:        X        - List of Accel and EMG (time series)
    #               D        - First order differential sequence of time series
    #                          (List)
    # OUTPUT:       Hjorth mobility and Complexity
    ############################################################################
    def hjorth_parameters(self, X, D=None):
        if D is None:
            D = self.first_order_diff(X);

        D.insert(0, X[0]);   # Pad first difference
        D = np.array(D);

        n = len(X);

        M2 = float(sum(D ** 2)) / n;
        TP = sum(np.array(X) ** 2);
        M4 = 0

        for i in range(1, len(D)):
            M4 += (D[i] - D[i - 1]) ** 2;
        M4 = M4 / n;

        mobility = np.sqrt(M2 / TP);
        complexity = np.sqrt(float(M4) * TP / M2 / M2);

        return mobility, complexity;



    ############################################################################
    # This is a function made purely for curiousity..
    # Hurst
    # Compute Hurst exponent of X. If the output H=0.5, the behavior of the
    # time-series is similar to a random walk. If H<0.5, the time-series
    # covers less "distance" than a random walk, and vice versa.
    #
    # INPUT:    X       - List for Accel and EMG (time series)
    # OUTPUT:   H       - Float (Hurst Exponent)
    ############################################################################
    def hurst(self, X):
        N = len(X)

        T = np.array([float(i) for i in range(1, N+1)])
        Y = np.cumsum(X)
        Ave_T = Y/T

        S_T = [0] * N
        R_T = [0] * N

        for i in range(N):
            S_T[i] = np.std(X[:i+1])
            X_T = Y - T * Ave_T[i]
            R_T[i] = max(X_T[:i+1]) - min(X_T[:i+1])

        R_S = R_T / S_T
        R_S = np.log(R_S)
        n =np. log(T).reshape(N,1)
        H = lstsq(n[1:], R_S[1:])[0]
        return H[0]
