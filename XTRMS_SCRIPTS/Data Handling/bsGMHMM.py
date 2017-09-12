import bsparser
import argparse
import sys
from EMGFeatures import EMGFeatures
import numpy as np
from hmmlearn.hmm import GaussianHMM, GMMHMM, _BaseHMM
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
import os
import pickle
from pathlib import Path

class classifier:
    num_channels = 8;
    zc_t = 1e-6;
    ssc_t = 1e-3;

    ############################################################################
    #
    # Function to extract features from bdf or TXT data passed.
    # Input:        - BS or XT object
    # Output:       - Feature vector X
    #
    ############################################################################
    def extract_subject_features(self, subject_data, start, end):
        fingers = ['RP', 'RR', 'RM', 'RI', 'RT', 'L'];
        EMGF = EMGFeatures();
        sdata = subject_data;
        X = None;
        labels = [];
        # For each event in subject data
        for ev in range(start, end):
            # Only process the relevent finger data
            if(sdata[ev].type in fingers):
                #data = subject_data[ev];
                mav = np.zeros(self.num_channels);
                zc  = np.zeros(self.num_channels);
                ssc = np.zeros(self.num_channels);
                wl  = np.zeros(self.num_channels);
                rms = np.zeros(self.num_channels);
                mobility = np.zeros(self.num_channels);
                complexity  = np.zeros(self.num_channels);


                # Extract features for each channel
                # Refer to EMGFeatures.py for more info on features
                for i in range(0, self.num_channels):
                    mav[i] = EMGF.mav(sdata[ev].data, i);
                    zc[i]  = EMGF.zero_crossings(sdata[ev].data, i, self.zc_t);
                    ssc[i] = EMGF.sign_slope_changes(sdata[ev].data, i, self.ssc_t);
                    wl[i]  = EMGF.waveform_length(s[ev].data, i);
                    rms[i] = EMGF.root_mean_square(sdata[ev].data, i);
                    mobility[i],complexity[i]  = EMGF.hjorth_parameters(sdata[ev].data[i]);


                # Append label
                labels.append(sdata[ev].type);

                if(X is None):
                    Y = np.asarray([mav, zc, ssc, rms, wl, mobility, complexity]);
                    Y = Y.flatten();
                    X = np.column_stack(Y);
                else:
                    Y = np.asarray([mav, zc, ssc, rms, wl, mobility, complexity]);
                    Y = Y.flatten();
                    X = np.vstack((X, np.column_stack(Y)));

        return X, labels;

    ############################################################################
    #
    # Function to apply GMHMM.
    # Input:        - Feature vector
    #
    ############################################################################
    def GMHMMFit(self, X, gmm_mixes, startprob, transmat, means, covs):
        print("Fitting to HMM and decoding ...");
        model = GMMHMM(n_components=116, n_mix=gmm_mixes, n_iter=1000);
        model.startprob_ = startprob;       # start with left hand
        model.transmat_ = transmat;
        model.means_ = means;
        model.covars_ = covs;
        model.fit(X);
        return model;

    ############################################################################
    #
    # Function to construct GMHMM transition matrix
    # Input:        - vector of labels
    # Output:       - Transition matrix
    #
    ############################################################################
    def constructTransMat(self, labels):
        transmat = np.zeros((6,6));
        counters = np.zeros(6);
        fingers = ['RP', 'RR', 'RM', 'RI', 'RT', 'L'];
        np.set_printoptions(precision=3)
        for l in range(0, len(labels)-1):
            i1 = fingers.index(labels[l]);
            i2 = fingers.index(labels[l+1]);
            transmat[i1,i2] = transmat[i1,i2] + 1;
            counters[i1] = counters[i1] + 1;

        # Compute percentages
        for i in range(0, len(counters)):
            if(counters[i] != 0):
                transmat[i,:] = transmat[i,:] / counters[i];
        return transmat

    ############################################################################
    #
    # Function to retrieve means and covariances of each state
    # Input:        - feature vector
    #               - label vector
    # Output:       - vectors of means and covariances
    #
    ############################################################################
    def getMeansCovs(self, X, labels):
        fingers = ['RP', 'RR', 'RM', 'RI', 'RT', 'L'];
        lowest_bic = np.infty;

        for f in fingers:
            component = [];
            # Collect all features for this state
            for i in range(0, len(labels)):
                if(labels[i] == f):
                    component.append(X[i]);

            component = np.asarray(component);

            # Extract gaussian mixture by finding best number of components
            best_gmm,bic,states = self.compute_lowest_bic(X);
            if(bic < lowest_bic):
                lowest_bic = bic;
                tru_gmm = best_gmm;

            # Extract mean and covariance
            means = tru_gmm.means_;
            covs = tru_gmm.covariances_;

        return means, covs[0], states;

    ############################################################################
    #
    # Function to compute the bayesian information criterion
    # Input:        - multidimension np array of features
    # Output:       - model with lowest BIC score
    #
    ############################################################################
    def compute_lowest_bic(self, X):
        states = [1, 2, 3, 4, 5, 6];
        lowest_bic = np.infty;
        best_state = 0;
        for s in states:
            gmm = GaussianMixture(n_components=s, covariance_type="full", max_iter=50);
            gmm.fit(X);
            new_bic = gmm.bic(X)
            if(new_bic < lowest_bic):
                lowest_bic = new_bic;
                best_gmm = gmm;
                best_state = s;

        return best_gmm, lowest_bic, best_state;

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    args = parser.parse_args()
    fname = args.fname
    extension = fname[-4:];

    s = bsparser.load_preproc_dataset(fname);

    cls = classifier();
    start1 = 0;
    end1 = 4000;
    start2 = 4000;
    end2 = 8000;

    X1,label1 = cls.extract_subject_features(s, start1, end1);
    X2,label2 = cls.extract_subject_features(s, start2, end2);

    startprob1 = [0., 0., 0., 0., 0., 1.];
    startprob2 = [0., 0., 0., 0., 0., 1.];

    transmat1 = cls.constructTransMat(label1);
    transmat2 = cls.constructTransMat(label2);

    means1,covs1,gmm_mixes1 = cls.getMeansCovs(X1, label1);
    means2,covs2,gmm_mixes2 = cls.getMeansCovs(X2, label2);

    m1 = cls.GMHMMFit(X1, gmm_mixes1, startprob1, transmat1, means1, covs1);
    m2 = cls.GMHMMFit(X2, gmm_mixes2, startprob2, transmat2, means2, covs2);


    print("Likelihood of M1: ", m1.score(X1));
    print("Likelihood of M2: ", m2.score(X2));
