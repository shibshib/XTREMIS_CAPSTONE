import numpy as np
import struct
import time

###########################################################################
#
# Class to take hex data file generated by XTREMIS and convert
# it to a human-readable csv file.
#
# KNOWN BUG: At the time of making this, Xtremis has a bug of placing
# the time of each sample at the next line, instead of on the same line.
# This script needs to be adjusted to read a single line at a time and find
# the time at the very end of the line
#
############################################################################

class Hex2DecConverter:
    def __init__(self, ADS1299_gain):
        # Reference voltage for ADC in ADS1299
        self.ADS1299_Vref = 4.5
        # Gain setting for ADS1299
        self.ADS1299_gain = ADS1299_gain;
        # ADS1299 datasheet Table 7, confirmed thru experiment
        self.scale_fac_uVolts_per_count = self.ADS1299_Vref / (float(pow(2,23)-1)) / self.ADS1299_gain * 1000000.0;
        # Assume set to +/-4G, so 2mG per digit (datasheet). Account for 4 bits unused
        self.scale_fac_accel_G_per_count = 0.002 / (float(pow(2,4)));

    # Print iterations progress
    def printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
        """
        Call in a loop to create terminal progress bar
        @params:
             iteration   - Required  : current iteration (Int)
             total       - Required  : total iterations (Int)
             prefix      - Optional  : prefix string (Str)
             suffix      - Optional  : suffix string (Str)
             decimals    - Optional  : positive number of decimals in percent complete (Int)
             length      - Optional  : character length of bar (Int)
             fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)

        prog = '\r' + prefix + '|' + bar + '| ' + percent + '% ' + suffix +  ' #' + str(iteration) + '/' + str(total) + '\r';
        print(prog, end='')
        # Print New Line on Complete
        if iteration == total:
           print()

    def file_len(self, fname):
        with open(fname ,encoding = "ISO-8859-1") as f:
            for i, l in enumerate(f):
                pass
        return i + 1;

    def convert(self, raw_file, converted_file=None, skip_lines=0):
        if (converted_file is None):
            curtime = time.strftime("%Y-%m-%d_%I-%M-%S");
            self.converted_file = "../converted/" + curtime + ".txt";

        # Open file for writing
        cfile = open(converted_file, "w+");
        rfile = open(raw_file, 'r');

        data = [];
        line_num = 0;       # Line counter
        num_lines = self.file_len(raw_file); #sum(1 for unicode(line, errors='replace') in open(raw_file));
        print ("Converting file " + raw_file);
        # Append progress
        self.printProgressBar(0, num_lines, prefix = 'Progress:', suffix = 'Complete');

        # Right now, we are reading two lines at a time -- one for the sample, next is for the time
        while True:
            line1 = rfile.readline();
            line2 = rfile.readline();

            # After we've skipped the appropriate number of lines
            if (line_num >= skip_lines):
                if (line1[0] != '%'):
                    records = line1.split(',');
                    floatData = [0] * (len(records) + 1);
                    # Go through each record in the line.
                    if (len(records) > 8):
                        for i in range(0, len(records)):
                            # Remove any residual characters
                            h = records[i].rstrip();
                            ##########################################
                            #               EMG DATA
                            ##########################################
                            if (i > 0 and i < 9):
                                if(h[0] > '7'):     # Number is negative
                                    h = 'FF' + h    # Keep it negative
                                else:
                                    h = '00' + h;   # Keep it positive

                            # This is a real number?
                            if (len(h) % 2 == 0 and len(h) > 4):
                                floatData[i] = struct.unpack('>i', bytes.fromhex(h))[0];
                            else:
                                floatData[i] = 0;

                             # EMG channel data
                            if (i >= 1 and i <= 8):
                                floatData[i] = round(floatData[i] * self.scale_fac_uVolts_per_count,3);
                            ''' If using accelerometer data as well
                            elif (i != 0):
                                floatData[i] = round(floatData[i] * self.scale_fac_accel_G_per_count, 3);
                            '''
                            ###########################################
                            #              TRIGGER DATA
                            ###########################################
                            # If collecting with accel, need to add another block similar to this
                            if (i > 9):
                                if(h[0] > '7'):
                                    h = 'FF' + h;       # Keep it negative
                                else:
                                    h = '0000' + h;     # Keep it positive

                                nh = struct.unpack('>i', bytes.fromhex(h))[0];
                                floatData[i] = nh;


                        # Get time on second line
                        t = line2.rstrip();
                        t = '00' + t;
                        toa = struct.unpack('>i', bytes.fromhex(t))[0];
                        floatData[-1] = toa;

                        # Write all this data to file
                        for i in range(0, len(floatData)):
                            if (i == len(floatData)-1):
                                cfile.write(str(floatData[i]));
                            else:
                                cfile.write(str(floatData[i]) + ',');
                        cfile.write('\n');
                        #data = np.append(data, np.asarray(floatData), axis=0);
                line_num = line_num + 1;
            else:
                line_num = line_num + 1;

            self.printProgressBar(line_num, num_lines, prefix = 'Progress:', suffix = 'Complete');
            # EOF
            if not line2: break;
        cfile.close();
        rfile.close();
