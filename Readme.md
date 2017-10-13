
# Project Title

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Setup
#### MCU FIRMWARE

To edit the XTREMIS firmware, you need to download the MPLAB-X IDE and MPLAB IPE software suites. You also need to download the VC32 compiler.

Download MPLAB-X IDE + MPLAB IPE: http://www.microchip.com/mplab/mplab-x-ide

After installing MPLAB-X IDE, you can also download the XC32/XC32++ compiler from the MPLAB software or from here: http://www.microchip.com/mplab/compilers

#### WI-FI FIRMWARE

To edit the Wi-Fi firmware, you need to download the Arduino IDE environment from here: https://www.arduino.cc/en/Main/Software
***DO NOT DOWNLOAD THE IDE FROM THE WINDOWS OR MAC OS X APP STORE***

Once you have your IDE installed and running, you have to install the ESP8266 compilers by going to *Tools -> Boards -> Boards Manager*. Search for "ESP8266" without the quotes and install the library. Once you have that installed, go to *Tools -> Boards -> Generic ESP8266 Module*.

#### SCRIPTS

To run the scripts inside XTRMS_SCRIPTS, you need to install Python 2.7 or later. You will also need the MNE, TKinter, numpy, sklearn, scipy, pickle, pandas, and seaborn. You can install them using the pip python package management tool.  

```
pip install mne numpy sklearn scipy pickle pandas seaborn
```
Follow this tutorial to install TKinter: http://www.tkdocs.com/tutorial/install.html, which is necessary for the communications module.

#### GUI
To install the GUI, you must download and install the Processing 3.3.6 environment. **NOTE: The libraries for XTREMIS are dependent on the version of Processing. Make sure you have 3.3.6 or later. If you still run into errors, find and install version 3.3.6 from the Processing archives**

Once you have installed Processing, place the contents of XTRMS_GUI inside the sketch folder for Processing. If you are using Windows, the sketch folder will be in 

```
C:\Users\Username\Documents\Processing
```
wheras if you're using Mac OS X it will be in:

```
Users/your_user_name/Documents/Processing
```

Once you have done so, open Processing and go to File -> Sketchbook. You should find XTRMS_GUI there, double click it and it will load up the system as in the photo below. Press play to run the code. 

![XTRMS_GUI](https://i.imgur.com/VVOuvoZ.png)

As it currently stands, the system has 3 modes: LIVE, PLAYBACK, and SYNTHETIC. 

LIVE mode allows you to connect to an XTREMIS board wirelessly by clicking "Autoconnect and Start System", the other options are still in beta mode and are not stable yet. 

PLAYBACK mode is finished, it allows you to either select a playback file (a converted file that is ready for reading) or select an SD file (a raw hex file generated when collecting data from XTREMIS). 

SYNTHETIC mode simply generates random signals on the GUI itself as a demonstration of how it should work. 

### Uploading FIRMWARE and flashing

MAKE SURE THAT THE SYSTEM IS POWERED **ON**. 

Use the ChipKIT PGM Programmer (pictured below) to upload or flash Firmware code to the PIC32MX250F128b processor onboard XTRMS using MPLAB IDE to upload or IPE to flash XTRMS. 

![ChipKIT PGM Programmer](http://chipkit.net/wp-content/uploads/2017/02/chipKIT-Programmer-obl-500-big-500x350.png)
 
To do so, plug the PGM programmer into the pins in the red rectangle in the photo below. Make sure that the white rectangle on the programmer is facing towards the right of the board and is placed on the top pin of the J5 header.  

#### This is to program the First gen. XTRMS Wi-Fi code
In contrast to the FIRMARE upload/flash, MAKE SURE THE SYSTEM IS POWERED **OFF**.

To program the Wi-Fi module, first make sure that you have wiped the firmware off the processor by using the MPLAB IPE and the ChipKIT PGM Programmer. Once you have done so, short the pins in the blue box by placing a jumper on them, and connecting the USB-to-UART cable/module to the TX, RX, and GND in the magenta box. **MAKE SURE YOU CONNECT TX ON XTREMIS TO RX ON THE CABLE, AND RX ON XTREMIS TO TX ON THE CABLE**.

Once you are ready to upload your code to the Wi-Fi module, click upload and keep XTREMIS **OFF**. Once compilation is finished, turn XTREMIS **ON** to go into bootloader mode so that the code can be uploaded safely. 
 
![XTRMS](https://i.imgur.com/mSIYlfm.jpg)







