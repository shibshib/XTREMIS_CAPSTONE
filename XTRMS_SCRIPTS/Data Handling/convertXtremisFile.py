import argparse
import time
from XtremisProcessor2 import Hex2DecConverter

'''
def clean_data(data, headers, Fs_Hz):
    num_channels = len(headers);
    FG = FiltersGalore();
    # Remove NaNs
    inds = pd.isnull(data).any(1).nonzero()[0]
    for i in range(0, len(inds)):
        for j in range(0, len(headers)):
            del data[headers[j]][inds[i]];

    # Notch filter remove 60 Hz noise
    for i in range(1, num_channels):
        cn = str(headers[i]);
        # Apply BP filter
        #filtered_channel = pd.Series(FG.butter_bandpass_filter(data[cn], 5, 500, Fs_Hz, 4));
        # Update channel with filtered channel
        #data[cn].update(filtered_channel);

        filtered_channel = pd.Series(FG.butter_bandpass_filter(data[cn], 7, 17, Fs_Hz, 2));
        # Update channel with filtered channel
        data[cn].update(filtered_channel);

        # Apply Notch filter
        filtered_channel = pd.Series(FG.notch_filter(data[cn], 60, Fs_Hz, 2));
        # Update channel with filtered channel
        data[cn].update(filtered_channel);

    return data;
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    args = parser.parse_args()
    fname = args.fname
    namebase = fname[:-4]

    gain = 8.0
    Fs_Hz = 4096
    converter = Hex2DecConverter(gain)
    for i in range(2,4):
        hex_file = fname
        data_dir = "../converted/"
        curtime = time.strftime("%Y-%m-%d_%I-%M-%S")

        converted_file = namebase + "_conv.TXT"

        converter.convert(hex_file, converted_file)

    print("Conversion finished!")
