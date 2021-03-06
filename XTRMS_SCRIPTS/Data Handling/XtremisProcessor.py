import numpy as np
import struct


'''
This class Takes a Hex data file generated by XTREMIS
and converts it to a human-readable csv file.
'''

class HexDecConverter:
    def __init__ (self, ADS1299_gain):
        self.ADS1299_Vref = 4.5;  # reference voltage for ADC in ADS1299
        self.ADS1299_gain = ADS1299_gain;    # assumed gain setting for ADS1299
        self.scale_fac_uVolts_per_count = self.ADS1299_Vref / (float(pow(2, 23)-1)) / self.ADS1299_gain  * 1000000.0; #   ADS1299 datasheet Table 7, confirmed through experiment
        self.scale_fac_accel_G_per_count = 0.002 / (float(pow(2,4)));  # assume set to +/4G, so 2 mG per digit (datasheet). Account for 4 bits unused

    def convertToDecimal(self, raw_file, converted_file=None):
        self.raw_file = raw_file;
        self.converted_file = converted_file;
        if(converted_file is not None):
            cfile = open(converted_file, 'w');
        data = [];
        line_num = 0;
        skip_lines = 1;
        with open(self.raw_file) as f:
            for line in f:
                if(line_num >= skip_lines):
                    # Remove white spaces and carriage Returns
                    records = line.split(',');
                    floatData = [0] * len(records);
                    if(line[0] != '%'):
                        if(len(records) > 8):
                            for i in range(0, len(records)):        # Go through each record in the line.
                                h = records[i].rstrip();            # Remove any residual aux characters like newline
                                if (i > 0):
                                    if(h[0] > '7'):     # if number is negative
                                        h = 'FF' + h;      # keep it negative
                                    else:
                                        h = '00' + h;      # Keep it positive

                                if (i > 8):     # accel data needs another byte
                                    if(h[0] == 'F'):     # if number is negative
                                        h = 'FF' + records[i];      # keep it negative
                                    else:
                                        h = '00' + records[i];      # Keep it positive

                                if (len(h) % 2 == 0 and len(h) > 4):        # Make sure this is a real number
                                    floatData[i] = struct.unpack('>i', bytes.fromhex(h))[0];
                                else:
                                    floatData[i] = 0;

                                if (i >= 1 and i <= 8):
                                    floatData[i] = round(floatData[i] * self.scale_fac_uVolts_per_count,3);
                                elif (i != 0):
                                    floatData[i] = round(floatData[i] * self.scale_fac_accel_G_per_count,3);

                            # Write all this data to file
                            if(converted_file is not None):
                                for i in range(0, len(floatData)):
                                    if (i == len(floatData)-1):
                                        cfile.write(str(floatData[i]));
                                    else:
                                        cfile.write(str(floatData[i]) + ',');
                                cfile.write('\n');

                            data = np.append(data, np.asarray(floatData), axis=0);
                        line_num = line_num + 1;
                else:
                    line_num = line_num + 1;

        if(converted_file is not None):
            cfile.close();
