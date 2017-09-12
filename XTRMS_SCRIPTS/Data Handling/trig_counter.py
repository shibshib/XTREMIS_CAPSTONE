##########################################################################
# Quick script to count number of triggers registered by XTREMIS board.
#########################################################################
import struct
data_dir = "C:\\Users\\Ala\\Desktop\\XTREMIS files\\XTREMIS\DData\\raw\\";
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', ',', '.','\'','\n',' '];
raw_file = data_dir + "OBCI_03.txt";
counter = 0;
last ="";
with open(raw_file) as f:
    for line in f:
        if(line[0] != '%'):
            records = line.split(',');
            if(len(records) > 9):
                h = records[10].rstrip();
                if(h[0] > '7'):     # if number is negative
                    h = 'FF' + h;      # keep it negative
                else:
                    h = '0000' + h;      # Keep it positive
                #print(h);
                nh = struct.unpack('>i', bytes.fromhex(h))[0];
                #
                if(last != alphabet[nh-1]):
                    print(alphabet[nh-1]);
                last = alphabet[nh-1];
                counter = counter + 1;

print(counter/2);
