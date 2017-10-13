
# Project Title

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
#### FIRMWARE

To edit the XTREMIS firmware, you need to download the MPLAB-X IDE and MPLAB IPE software suites. You also need to download the VC32 compiler.

Download MPLAB-X IDE + MPLAB IPE: http://www.microchip.com/mplab/mplab-x-ide

After installing MPLAB-X IDE, you can also download the XC32/XC32++ compiler from the MPLAB software or from here: http://www.microchip.com/mplab/compilers

#### SCRIPTS

To run the scripts inside XTRMS_SCRIPTS, you need to install Python 2.7 or later. You will also need the MNE, TKinter, numpy, sklearn, scipy, pickle, pandas, and seaborn. You can install them using the pip python package management tool.  

```
pip install mne numpy sklearn scipy pickle pandas seaborn
```
Follow this tutorial to install TKinter: http://www.tkdocs.com/tutorial/install.html, which is necessary for the communications module.

#### GUI
To install the GUI, 

### Uploading FIRMWARE code

Use the ![ChipKIT PGM Programmer](http://chipkit.net/wp-content/uploads/2017/02/chipKIT-Programmer-obl-500-big-500x350.png)
 to upload Firmware code to the PIC32MX250F128b processor onboard XTRMS. To do so, plug the PGM programmer into the pins in the red rectangle in the photo. 
 
 ![XTRMS](https://i.imgur.com/mSIYlfm.jpg)

