
"""Parses biosemi data

Usage:

s1 = load_preproc_dataset('data/xtremis_subj1.bdf')
will load the given bdf file, filter and reference it,
and produce a Trials object.

You can index s1 to get a specific event in the dataset.
Each event is an Event object.

e.g.
s1[0] is the first keypress. It has these attributes:
    key:    key that was pressed
    last:   last key pressed
    next:   next key pressed
    data:   np.ndarray with shape (8, X)
            where X is the number of samples for that keypress.
"""

import pickle
from string import printable
from os import environ, path

import numpy as np
import mne
import pandas as pd


ALLOWED_CHARS = [ord(x) for x in printable]
EMG_CHANS = ["EXG%s" % i for i in range(1, 9)]

ALPHABET = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
            'q','r','s','t','u','v','w','x','y','z', ',', '.','\'','\n',' ']

try:
    N_WORKERS = environ['OMP_NUM_THREADS']
except KeyError:
    N_WORKERS = 2


class Event(object):

    def __init__(self, key, finger, onset, offset, raw):

        self.key = key
        self.onset = onset
        self.offset = offset

        self.last = ''
        self.next = ''

        self.type = finger

        self.data = raw


class BSTrials(object):
    '''
        Can adjust event markers by tweaking:
        self.bias_before:
            positive values bring the left edge closer to the trigger
            negative values bring the left edge further
        self.bias_after:
            negative values bring the right edge closer to the trigger
            positive values bring the right edge further
    '''

    def __init__(self, name, data, timebefore=75, load=True, evts=None):

        self.name = name
        self._data = data
        self.srate = data.info['sfreq']

        self.samplesbefore = int((timebefore / 1000.0) * self.srate)

        if self.name[-4:] == '.bdf':
            self.type = 'bdf'
            self.trigs = self.parse_trigs()
        elif self.name[-4:] == '.TXT':
            self.type = 'xtr'
            self.trigs = evts
        else:
            raise UserWarning("Not a .bdf or .TXT file")

        self.trig_labels = self.label_trigs()

        # load or create events
        trigname = path.splitext(name)[0] + '.trg'
        if path.exists(trigname):
            print('loading from .trg file')
            self.event = load_events(trigname)
        else:
            self.event = self.make_eventlist()

        # clear ram because now we index a list of event objects
        if load is False: del self._data

        self.bias_before = 0
        self.bias_after = 0

    def parse_trigs(self, mindiff=0.75):
        """
        mindiff: How far apart triggers need to be to keep (in milliseconds)

        Returns an mne event list with entries for each trigger:
        [latency, pre-value, value]
        """

        # override default shortest_event because we have events that are
        # 1 sample apart.
        if self.type == 'bdf':
            trigs = mne.find_events(self._data, stim_channel="STI 014",
                                    shortest_event=1)


        ## remove any events that are too close together
        latencies = trigs[:, 0]
        latencies = np.diff(latencies)

        srate = self._data.info['sfreq']
        thresh = int(mindiff * srate/1000.)

        # array of boolean, events we'll keep
        keep = latencies > thresh

        # Extend derivative by one so lengths match.
        # Default to keeping the last event (probably key release)
        keep = np.insert(keep, -1, True)
        trigs = trigs[keep]

        # bitshift to get correct events
        if self.type == 'bdf': trigs[:, 2] = (trigs[:, 2] >> 8) - 128

        return trigs

    def label_trigs(self):
        """
        Produce a list of human-readable labels for a given event list.
        """

        if self.type == 'bdf':
            return [
                chr(x) if x in ALLOWED_CHARS
                else 'REL' if x == 26
                else x
                for x in self.trigs[:, 2]
                ]

        elif self.type == 'xtr':
            trigs = [ x for x in self.trigs[:, 2]]
            print(trigs)

            return [
                "REL" if trigs[x] == trigs[x-1]
                else ALPHABET[trigs[x]-1]
                for x in range(len(trigs))
                ]

    def make_eventlist(self, defaultdur=0.075):
        """
        Creates a list of Event objects.

        Loops through the current triggers, and tries to find a key release for
        each key press. If no release is found, the epoch looks ahead by
        defaultdur seconds. (default 75ms)
        """

        events = []

        # copy the list because we'll be modifying it
        trigcopy = list(self.trig_labels)

        # loop through all key presses
        last_offset = 0

        for i, evt in enumerate(trigcopy):
            if evt not in ['REL', '_REL']:

                # assume no one starts typing 75 ms from beginning
                onset = self.trigs[i][0] - self.samplesbefore
                offset = 0 # default in case we dont find a release

                # Look up to 2 samples ahead and find a REL event
                lookahead = min(i+3, len(trigcopy) - 1)
                for j in range(i+1, lookahead):
                    evt2 = trigcopy[j]

                    # if we find a release event, mark it as used
                    if evt2 == 'REL':
                        offset = self.trigs[j][0]
                        trigcopy[j] = "_REL" # mark this release as used
                        break

                # if we didnt find a key release, use the default duration
                if offset == 0:
                    offset = int(onset + defaultdur*self.srate)

                # add a transition event if there was one
                if onset - last_offset > 0:
                    events.append(Event('0', 'TS', last_offset, onset, 0))
                last_offset = offset
                events.append(Event(evt, 'UN', onset, offset, 0))

        if events[0].type == 'TS': del events[0]

        # add the next/last events for all but the first/last events
        for i in range(1, len(events)-1):
            events[i].next = events[i+1].key
            events[i].last = events[i-1].key
        events[0].next = events[1].key
        events[-1].last = events[-2].key

        return events

    def set_event(self, idx, finger):
        self.event[idx].type = finger

    def __getitem__(self, idx):

        evt = self.event[idx]

        if evt.type == "TS":
            modifier = -1
        else:
            modifier = 1

        try:
            trig_on = evt.onset + modifier*self.bias_before
            trig_off = evt.offset + modifier*self.bias_after
            dat = self._data.get_data(start=trig_on, stop=trig_off)
            print(dat)
        except AttributeError:
            dat = 0

        return Event(evt.key, evt.type, evt.onset, evt.offset, dat)

    def __len__(self):

        return len(self.event)


def load_events(fname):

    with open(fname, 'rb') as _: events = pickle.load(_)

    return events.event


def load_xtremis(fname, srate):
    '''
    Alternative to mne.load_edf to handle xtremis files.
    Currently assuming a sample rate of 1024 Hz
    '''

    col_labels = ['sample', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7',
                  'ch8', 'tr1', 'tr2', 'tr3', 'time']
    channels = ['ch%s' % i for i in range(1,9)]

    # read as pandas dataframe
    df = pd.read_csv(fname, names=col_labels, engine='python')
    #print(df);
    # create a numpy array for the raw data
    raw_data = []
    for i in channels:
        raw_data.append(df.as_matrix([i]))
    raw_data = np.array(raw_data).squeeze()

    # create the mne compatible object
    info = mne.create_info(ch_names=channels, sfreq=srate, ch_types=['eeg']*8)
    raw = mne.io.RawArray(raw_data, info)

    # extract the triggers
    trig1 = df[pd.notnull(df.time)]
    evts = np.ndarray((len(trig1), 3), dtype=int)

    for _ in range(len(trig1)):

        evts[_, 0] = trig1.iloc[_].name
        evts[_, 1] = 0 # arbitrary filler for this project
        evts[_, 2] = trig1.iloc[_].tr2

    return raw, evts


def load_preproc_dataset(fname, hipass=10, lowpass=500, baseline=25,
                         filt=True, load=True):
    """
    Load and preprocess a dataset.
    baseline is how far before (in ms) you want to pull from a keypress

    Will filter first, then reference.
    """

    # load data
    if fname[-4:] == '.bdf':
        raw = mne.io.read_raw_edf(fname,
                                  preload=load)
        ref_chans = EMG_CHANS
        evts = None
    else:
        raw, evts = load_xtremis(fname)
        ref_chans = ['ch%s' % i for i in range(1,9)]

    # preprocess here
    if load is True:
        # drop all but emg and trigger channel
        drop = [i for i in raw.ch_names
                if i not in EMG_CHANS and i != "STI 014"]
        try:
            raw.drop_channels(drop)
        except ValueError:
            pass

    if load and filt:
        # filter
        #raw.filter(hipass, lowpass, n_jobs=N_WORKERS)
        # reference to EMG channels only
        raw.set_eeg_reference(ref_channels=ref_chans)

    return BSTrials(fname, raw, timebefore=baseline, load=load, evts=evts)

def load_as_df(fname, ref=False, filt=True, srate=1024):

    # load data


    if fname[-4:] == '.bdf':
        raw = mne.io.read_raw_edf(fname,
                                  preload=True)
        raw.drop_channels(['STI 014'])
        print("Original srate: ", raw.info['sfreq'])
        raw.resample(srate)
        ref_chans = EMG_CHANS
        evts = None
    else:
        raw, evts = load_xtremis(fname, srate)
        ref_chans = ['ch%s' % i for i in range(1,9)]

    #if filt is True:
    #    raw.notch_filter(freqs=60)

    if ref is True:
        try:
            raw.set_eeg_reference(ref_channels=ref_chans)
        except ValueError: # handle if EXG channels were excluded recording.
            pass

    #raw.notch_filter(60)
    df = pd.DataFrame(raw.get_data(), raw.ch_names)

    return df.transpose()
