import serial
import XTREMIS as xt
import time
import logging
import struct

START_BYTE = 'A'  # start of data packet
END_BYTE = 0xC0  # end of data packet
END_ACCEL_TIME_SET = 0xC3
END_ACCEL_TIME_SYNCED = 0xC4

def streamData(sample):
  #os.system('clear')
	print ("----------------")
	print("%f" %(sample.id))
	print (sample.channel_data)
	print (sample.aux_data)
	print ("----------------")

if __name__ == '__main__':
    port = 'COM3';
    baud = 115200;
    logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
    logging.info('---------LOG START-------------')
    board = xt.XTREMISBoard(port=port, baud=baud, filter_data=False);
    print("Board Instantiated")
    board.ser.write(b'b')
    board.ser.write(b'A')

    time.sleep(300);
    print("Finished writing to SD card");
//    board.start_streaming(streamData);
