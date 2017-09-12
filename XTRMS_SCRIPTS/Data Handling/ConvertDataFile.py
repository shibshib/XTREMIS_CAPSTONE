import time
from Hex_SD_File_Converter import HexDecConverter
from FiltersGalore import FiltersGalore
from PlotData import PlotData
import pandas as pd
import sys
import numpy as np

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

if __name__ == '__main__':
    gain = 8.0;
    Fs_Hz = 1024;
    hex_file = "../DData/raw/OBCI_02.txt";
    data_dir = "C:\\Users\\Ala\\Desktop\\XTREMIS files\\XTREMIS\DData\\converted\\";
    curtime = time.strftime("%Y-%m-%d_%I-%M-%S");

    converted_file = "../DData/converted/SDconverted-BLANK1KSPSTRIGTEST-"+ curtime + ".txt";
    #converted_file = data_dir + "SDconverted-HB1KSPSDE-2017-06-30_01-34-08.txt"

    #filtered_converted_file = data_dir + "SDconverted-HB1KSPSDE-2017-06-30_01-34-08_filtered.txt"
    filtered_converted_file = data_dir + "SDconverted-HB1KSPSDE-" + curtime + "_filtered.txt";
    # For testing purposes

    converter = HexDecConverter(gain);
    converter.convertToDecimal(hex_file, converted_file);

    headers = ['SN', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
    data = pd.read_csv(converted_file, skiprows=1, names=headers,na_values=["nan"])
    data = clean_data(data, headers, Fs_Hz);
    data.to_csv(filtered_converted_file, index=False);
