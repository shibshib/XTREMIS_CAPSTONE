##########################################################################
# 
# Parses converted Xtremis files
#
#
#########################################################################
import struct
import argparse
import sys

class Event:
    def __init__(self, key, finger, onset, offset, raw):
        self.key = key;
        self.onset = onset;
        self.offset = offset;

        self.last = '';
        self.next = '';

        self.type = finger;

        self.data = raw;

class XTExtractor:
    alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u'
               ,'v','w','x','y','z', ',', '.','\'','\n',' '];
 
    def __init__(self, raw_file):
        self.raw_file = raw_file;

    def extract_events(self, raw_file):
        counter = 0;
        last ="";
        with open(raw_file) as f:
            for line in f:
                if(line[0] != '%'):
                    records = line.rstrip().split(',');
                    if(len(records) > 10):
                       # print(records);
                        nh = int(float(records[11]));
                        #print(records);
                        if(last != nh):
                            print(self.alphabet[nh-1], end='');
                            counter = counter + 1;
                        last = nh;
                        #print(nh)
                        
                        #if(counter > 10):
                        #    sys.exit(0);

        print(counter);



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fname');
    args = parser.parse_args()
    fname = args.fname
    
    gain = 8.0;
    xte = XTExtractor(fname);
    xte.extract_events(fname);
