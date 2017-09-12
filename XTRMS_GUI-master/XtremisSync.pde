///////////////////////////////////////////////////////////////////////////////
//
// This class configures and manages the connection to WiserLab's XTREMIS
// The connection is implemented via a TCP connection to a TCP port.
// The Gagnlion is configured using single letter text commands sent from the
// PC to the TCP server.  The EEG data streams back from the XT, to the
// TCP server and back to the PC continuously (once started).
//
// Created: AJ Keller, August 2016
//
/////////////////////////////////////////////////////////////////////////////

// import java.io.OutputStream; //for logging raw bytes to an output file

//------------------------------------------------------------------------
//                       Global Functions
//------------------------------------------------------------------------

boolean wereWifiPacketsDropped= false;
int numWifiPacketsDroppedGang = 0;

void clientEvent(Client someClient) {
  //  print("Server Says:");

  int p = xt.tcpBufferPositon;
  xt.tcpBuffer[p] = xt.tcpClient.readChar();
  xt.tcpBufferPositon++;

  if (p > 2) {
    String posMatch  = new String(xt.tcpBuffer, p - 2, 3);

    if (posMatch.equals(xt.TCP_STOP)) {
     if (!xt.nodeProcessHandshakeComplete) {
        xt.nodeProcessHandshakeComplete = true;
        xt.setHubIsRunning(true);
        println("xtSync: clientEvent: handshake complete");
      }
      // Get a string from the tcp buffer
      String msg = new String(xt.tcpBuffer, 0, p);
      // Send the new string message to be processed
      xt.parseMessage(msg);
      // Check to see if the xt ble list needs to be updated
      if (xt.deviceListUpdated) {
        xt.deviceListUpdated = false;
        controlPanel.bleBox.refreshBLEList();
      }
      // Reset the buffer position
      xt.tcpBufferPositon = 0;
    }
  }
}

class XTREMIS {
  final static String TCP_CMD_ACCEL = "a";
  final static String TCP_CMD_CONNECT = "c";
  final static String TCP_CMD_COMMAND = "k";
  final static String TCP_CMD_DISCONNECT = "d";
  final static String TCP_CMD_DATA= "t";
  final static String TCP_CMD_ERROR = "e";
  final static String TCP_CMD_IMPEDANCE = "i";
  final static String TCP_CMD_LOG = "l";
  final static String TCP_CMD_SCAN = "s";
  final static String TCP_CMD_STATUS = "q";
  final static String TCP_STOP = ",;\n";
  final static String TCP_POKE = "p";

  final static String TCP_ACTION_START = "start";
  final static String TCP_ACTION_STATUS = "status";
  final static String TCP_ACTION_STOP = "stop";

  final static String XT_BOOTLOADER_MODE = ">";

  final static byte BYTE_START = (byte)0xA0;
  final static byte BYTE_END = (byte)0xC0;

  // States For Syncing with the hardware
  final static int STATE_NOCOM = 0;
  final static int STATE_COMINIT = 1;
  final static int STATE_SYNCWITHHARDWARE = 2;
  final static int STATE_NORMAL = 3;
  final static int STATE_STOPPED = 4;
  final static int COM_INIT_MSEC = 3000; //you may need to vary this for your computer or your Arduino

  final static int NUM_ACCEL_DIMS = 3;

  final static int RESP_ERROR_UNKNOWN = 499;
  final static int RESP_ERROR_BAD_PACKET = 500;
  final static int RESP_ERROR_BAD_NOBLE_START = 501;
  final static int RESP_ERROR_ALREADY_CONNECTED = 408;
  final static int RESP_ERROR_COMMAND_NOT_RECOGNIZED = 406;
  final static int RESP_ERROR_DEVICE_NOT_FOUND = 405;
  final static int RESP_ERROR_NO_OPEN_BLE_DEVICE = 400;
  final static int RESP_ERROR_UNABLE_TO_CONNECT = 402;
  final static int RESP_ERROR_UNABLE_TO_DISCONNECT = 401;
  final static int RESP_ERROR_SCAN_ALREADY_SCANNING = 409;
  final static int RESP_ERROR_SCAN_NONE_FOUND = 407;
  final static int RESP_ERROR_SCAN_NO_SCAN_TO_STOP = 410;
  final static int RESP_ERROR_SCAN_COULD_NOT_START = 412;
  final static int RESP_ERROR_SCAN_COULD_NOT_STOP = 411;
  final static int RESP_XT_FOUND = 201;
  final static int RESP_SUCCESS = 200;
  final static int RESP_SUCCESS_DATA_ACCEL = 202;
  final static int RESP_SUCCESS_DATA_IMPEDANCE = 203;
  final static int RESP_SUCCESS_DATA_SAMPLE = 204;
  final static int RESP_STATUS_CONNECTED = 300;
  final static int RESP_STATUS_DISCONNECTED = 301;
  final static int RESP_STATUS_SCANNING = 302;
  final static int RESP_STATUS_NOT_SCANNING = 303;

  private int state = STATE_NOCOM;
  int prevState_millis = 0; // Used for calculating connect time out

  private int nEEGValuesPerPacket = NCHAN_XT; // Defined by the data format sent by openBCI boards
  private int nAuxValuesPerPacket = NUM_ACCEL_DIMS; // Defined by the arduino code

  private int tcpXtremisPort = 9999;
  private String tcpXtremisIP = "192.168.11.125";
  private String tcpXtremisFull = tcpXtremisIP + ":" + tcpXtremisPort;
  private boolean tcpClientActive = false;
  private int tcpTimeout = 1000;

  private final float fs_Hz = 500.0f;  //sample rate used by XT board... set by its Arduino code
  private final float ADS1299_Vref = 4.5f;  // reference voltage for ADC in MCP3912 set in hardware
  private float ADS1299_gain = 8.0;  //assumed gain setting for MCP3912.  NEEDS TO BE ADJUSTABLE JM
  private float scale_fac_uVolts_per_count = ADS1299_Vref / ((float)(pow(2, 23)-1)) / ADS1299_gain  * 1000000.f; 
  // private float scale_fac_accel_G_per_count = 0.032;
  private final float scale_fac_accel_G_per_count = 0.002 / ((float)pow(2, 4));
  // private final float scale_fac_accel_G_per_count = 0.002 / ((float)pow(2,4));  //assume set to +/4G, so 2 mG per digit (datasheet). Account for 4 bits unused
  // private final float leadOffDrive_amps = 6.0e-9;  //6 nA, set by its Arduino code

  private int bleErrorCounter = 0;
  private int prevSampleIndex = 0;

  private DataPacket_ADS1299 dataPacket;

  public Client tcpClient;
  private boolean portIsOpen = false;
  private boolean connected = false;

  public int numberOfDevices = 0;
  public int maxNumberOfDevices = 10;
  public String[] deviceList = new String[0];
  public boolean deviceListUpdated = false;
  private boolean hubRunning = false;
  public char[] tcpBuffer = new char[1024];
  public int tcpBufferPositon = 0;

  private boolean waitingForResponse = false;
  private boolean nodeProcessHandshakeComplete = false;
  public boolean shouldStartNodeApp = false;
  private boolean checkingImpedance = false;
  private boolean accelModeActive = false;
  private boolean newAccelData = false;
  private int[] accelArray = new int[NUM_ACCEL_DIMS];

  public boolean impedanceUpdated = false;
  public int[] impedanceArray = new int[NCHAN_XT + 1];

  // Getters
  public float get_fs_Hz() { 
    return fs_Hz;
  }
  public boolean isPortOpen() { 
    return portIsOpen;
  }
  public float get_scale_fac_uVolts_per_count() { 
    return scale_fac_uVolts_per_count;
  }
  public float get_scale_fac_accel_G_per_count() { 
    return scale_fac_accel_G_per_count;
  }
  public boolean isCheckingImpedance() { 
    return checkingImpedance;
  }
  public boolean isAccelModeActive() { 
    return accelModeActive;
  }

  private PApplet mainApplet;

  //constructors
  XTREMIS() {
  };  //only use this if you simply want access to some of the constants
  XTREMIS(PApplet applet) {
    mainApplet = applet;

    // Able to start tcpClient connection?
    //  startTCPClient(mainApplet);

    // For storing data into
    dataPacket = new DataPacket_ADS1299(nEEGValuesPerPacket, nAuxValuesPerPacket);  //this should always be 8 channels
    for (int i = 0; i < nEEGValuesPerPacket; i++) {
      dataPacket.values[i] = 0;
    }
    for (int i = 0; i < nAuxValuesPerPacket; i++) {
      dataPacket.auxValues[i] = 0;
    }
  }

  /**
   * @descirpiton Used to `try` and start the tcpClient
   * @param applet {PApplet} - The main applet.
   * @return {boolean} - True if able to start.
   */
  public boolean startTCPClient() {
    println("Starting XTREMIS TCP...");
    try {
      tcpClient = new Client(mainApplet, tcpXtremisIP, tcpXtremisPort);
      return true;
    } 
    catch (Exception e) {
      println("startTCPClient: ConnectException: " + e);
      return false;
    }
  }


  /**
   * Sends a status message to the node process.
   */
  public boolean getStatus() {
    try {
      safeTCPWrite(TCP_CMD_STATUS + TCP_STOP);
      waitingForResponse = true;
      return true;
    } 
    catch (NullPointerException E) {
      // The tcp client is not initalized, try now

      return false;
    }
  }

  public void setHubIsRunning(boolean isRunning) {
    hubRunning = isRunning;
  }

  // Return true if the display needs to be updated for the BLE list
  public void parseMessage(String msg) {
    println(msg);
    String[] list = split(msg, ',');
    switch (list[0].charAt(0)) {
    case 'c': // Connect
      processConnect(msg);
      break;
    case 'a': // Accel
      processAccel(msg);
      break;
    case 'd': // Disconnect
      processDisconnect(msg);
      break;
    case 'i': // Impedance
      processImpedance(msg);
      break;
    case 't': // Data
      processData(msg);
      break;
    case 'e': // Error
      println("XTREMIS: parseMessage: error: " + list[2]);
      break;
    case 's': // Scan
      processScan(msg);
      break;
    case 'l':
      println("XTREMIS: Log: " + list[1]);
      break;
    case 'q':
      processStatus(msg);
      break;
    default:
      println("XTREMIS: parseMessage: default: " + msg);
      break;
    }
  }

  private void processAccel(String msg) {
    String[] list = split(msg, ',');
    if (Integer.parseInt(list[1]) == RESP_SUCCESS_DATA_ACCEL) {
      for (int i = 0; i < NUM_ACCEL_DIMS; i++) {
        accelArray[i] = Integer.parseInt(list[i + 2]);
      }
      newAccelData = true;
    }
  }

  private void processConnect(String msg) {
    String[] list = split(msg, ',');
    if (isSuccessCode(Integer.parseInt(list[1]))) {
      println("XTREMIS: parseMessage: connect: success!");
      output("XTREMIS: The GUI is done intializing. Click outside of the control panel to interact with the GUI.");
      systemMode = 10;
      connected = true;
      controlPanel.close();
    } else {
      println("XTREMIS: parseMessage: connect: failure!");
      haltSystem();
      initSystemButton.setString("START SYSTEM");
      controlPanel.open();
      abandonInit = true;
      output("Unable to connect to XTREMIS! Please ensure board is powered on and in range!");
      connected = false;
    }
  }

  private void processData(String msg) {
    String[] list = split(msg, ',');
    int code = Integer.parseInt(list[1]);
    if (eegDataSource == DATASOURCE_XTREMIS && systemMode == 10 && isRunning) {
      if (Integer.parseInt(list[1]) == RESP_SUCCESS_DATA_SAMPLE) {
        // Sample number stuff
        dataPacket.sampleIndex = int(Integer.parseInt(list[2]));
        if ((dataPacket.sampleIndex - prevSampleIndex) != 1) {
          if (dataPacket.sampleIndex != 0) {  // if we rolled over, don't count as error
            bleErrorCounter++;

            wereWifiPacketsDropped = true; //set this true to activate packet duplication in serialEvent
            if (dataPacket.sampleIndex < prevSampleIndex) {   //handle the situation in which the index jumps from 250s past 255, and back to 0
              numPacketsDroppedGang = (dataPacket.sampleIndex+200) - prevSampleIndex; //calculate how many times the last received packet should be duplicated...
            } else {
              numPacketsDroppedGang = dataPacket.sampleIndex - prevSampleIndex; //calculate how many times the last received packet should be duplicated...
            }
            println("XTREMIS: apparent sampleIndex jump from Serial data: " + prevSampleIndex + " to  " + dataPacket.sampleIndex + ".  Keeping packet. (" + bleErrorCounter + ")");
            println("numPacketsDropped = " + numPacketsDropped);
          }
        }
        prevSampleIndex = dataPacket.sampleIndex;

        // Channel data storage
        for (int i = 0; i < NCHAN_XT; i++) {
          dataPacket.values[i] = Integer.parseInt(list[3 + i]);
        }
        if (newAccelData) {
          newAccelData = false;
          for (int i = 0; i < NUM_ACCEL_DIMS; i++) {
            dataPacket.auxValues[i] = accelArray[i];
            dataPacket.rawAuxValues[i][0] = byte(accelArray[i]);
          }
        }
        getRawValues(dataPacket);
        // println(binary(dataPacket.values[0], 24) + '\n' + binary(dataPacket.rawValues[0][0], 8) + binary(dataPacket.rawValues[0][1], 8) + binary(dataPacket.rawValues[0][2], 8) + '\n');
        curDataPacketInd = (curDataPacketInd+1) % dataPacketBuff.length; // This is also used to let the rest of the code that it may be time to do something

        xt.copyDataPacketTo(dataPacketBuff[curDataPacketInd]);  // Resets isNewDataPacketAvailable to false

        // KILL SPIKES!!!
        if (wereWifiPacketsDropped) {
          // println("Packets Dropped ... doing some stuff...");
          for (int i = numPacketsDroppedGang; i > 0; i--) {
            int tempDataPacketInd = curDataPacketInd - i; //
            if (tempDataPacketInd >= 0 && tempDataPacketInd < dataPacketBuff.length) {
              // println("i = " + i);
              xt.copyDataPacketTo(dataPacketBuff[tempDataPacketInd]);
            } else {
              xt.copyDataPacketTo(dataPacketBuff[tempDataPacketInd+200]);
            }
            //put the last stored packet in # of packets dropped after that packet
          }

          //reset werePacketsDropped & numPacketsDropped
          wereWifiPacketsDropped = false;
          numPacketsDroppedGang = 0;
        }

        switch (outputDataSource) {
        case OUTPUT_SOURCE_ODF:
          fileoutput_odf.writeRawData_dataPacket(dataPacketBuff[curDataPacketInd], xt.get_scale_fac_uVolts_per_count(), get_scale_fac_accel_G_per_count());
          break;
        case OUTPUT_SOURCE_BDF:
          // curBDFDataPacketInd = curDataPacketInd;
          // thread("writeRawData_dataPacket_bdf");
          fileoutput_bdf.writeRawData_dataPacket(dataPacketBuff[curDataPacketInd]);
          break;
        case OUTPUT_SOURCE_NONE:
        default:
          // Do nothing...
          break;
        }
        newPacketCounter++;
      } else {
        bleErrorCounter++;
        println("XTREMIS: parseMessage: data: bad");
      }
    }
  }

  private void handleError(int code, String msg) {
    output("Code " + code + "Error: " + msg);
    println("Code " + code + "Error: " + msg);
  }

  private void processDisconnect(String msg) {
    if (!waitingForResponse) {
      haltSystem();
      initSystemButton.setString("START SYSTEM");
      controlPanel.open();
      output("Dang! Lost connection to XTREMIS. Please move closer or get a new battery!");
    } else {
      waitingForResponse = false;
    }
  }

  private void processImpedance(String msg) {
    String[] list = split(msg, ',');
    if (Integer.parseInt(list[1]) == RESP_SUCCESS_DATA_IMPEDANCE) {
      int channel = Integer.parseInt(list[2]);
      if (channel < 5) {
        int value = Integer.parseInt(list[3]);
        impedanceArray[channel] = value;
        if (channel == 0) {
          impedanceUpdated = true;
          println("Impedance for channel reference is " + value + " ohms.");
        } else {
          println("? for channel " + channel + " is " + value + " ohms.");
        }
      }
    }
  }

  private void processStatus(String msg) {
    String[] list = split(msg, ',');
    int code = Integer.parseInt(list[1]);
    if (waitingForResponse) {
      waitingForResponse = false;
      println("Node process up!");
    }
    if (code == RESP_ERROR_BAD_NOBLE_START) {
      println("XTREMIS: processStatus: Problem in the Hub");
      output("Problem starting XTREMIS Hub. Please make sure compatible USB is configured, then restart this GUI.");
    } else {    
      println("XTREMIS: processStatus: Started Successfully");
    }
  }

  private void processScan(String msg) {
    String[] list = split(msg, ',');
    int code = Integer.parseInt(list[1]);
    switch(code) {
    case RESP_XT_FOUND:
      // Sent every time a new XT device is found
      if (searchDeviceAdd(list[2])) {
        deviceListUpdated = true;
      }
      break;
    case RESP_ERROR_SCAN_ALREADY_SCANNING:
      // Sent when a start send command is sent and the module is already
      //  scanning.
      handleError(code, list[2]);
      break;
    case RESP_SUCCESS:
      // Sent when either a scan was stopped or started Successfully
      String action = list[2];
      switch (action) {
      case TCP_ACTION_START:
        break;
      case TCP_ACTION_STOP:
        break;
      }
      break;
    case RESP_ERROR_SCAN_COULD_NOT_START:
      // Sent when err on search start
      handleError(code, list[2]);
      break;
    case RESP_ERROR_SCAN_COULD_NOT_STOP:
      // Send when err on search stop
      handleError(code, list[2]);
      break;
    case RESP_STATUS_SCANNING:
      // Sent when after status action sent to node and module is searching
      break;
    case RESP_STATUS_NOT_SCANNING:
      // Sent when after status action sent to node and module is NOT searching
      break;
    case RESP_ERROR_SCAN_NO_SCAN_TO_STOP:
      // Sent when a 'stop' action is sent to node and there is no scan to stop.
      handleError(code, list[2]);
      break;
    case RESP_ERROR_UNKNOWN:
    default:
      handleError(code, list[2]);
      break;
    }
  }

  void writeRawData_dataPacket_bdf() {
    fileoutput_bdf.writeRawData_dataPacket(dataPacketBuff[curBDFDataPacketInd]);
  }

  public int copyDataPacketTo(DataPacket_ADS1299 target) {
    return dataPacket.copyTo(target);
  }

  private void getRawValues(DataPacket_ADS1299 packet) {
    for (int i=0; i < nchan; i++) {
      int val = packet.values[i];
      //println(binary(val, 24));
      byte rawValue[] = new byte[3];
      // Breakdown values into
      rawValue[2] = byte(val & 0xFF);
      //println("rawValue[2] " + binary(rawValue[2], 8));
      rawValue[1] = byte((val & (0xFF << 8)) >> 8);
      //println("rawValue[1] " + binary(rawValue[1], 8));
      rawValue[0] = byte((val & (0xFF << 16)) >> 16);
      //println("rawValue[0] " + binary(rawValue[0], 8));
      // Store to the target raw values
      packet.rawValues[i] = rawValue;
      //println();
    }
  }

  // TODO: Figure out how to ping the server at localhost listening on port 10996
  // /**
  //  * Used to ping the local hub tcp server and check it's status.
  //  */
  // public boolean pingHub() {
  //   boolean pingStat;
  //
  //  Ganglionry {
  //     println("XTSync: pingHub: trying... ");
  //     pingStat = InetAddress.getByName("127.0.0.1:10996").isReachable(tcpTGanglioneout);
  //     print("XTSync: pingHub: ");
  //     println(pingStat);
  //     return pingStat;
  //   }
  //   catch(Exception E){
  //     E.printStackTrace();
  //     return false;
  //   }
  // }

  public boolean isSuccessCode(int c) {
    return c == RESP_SUCCESS;
  }

  // SCANNING/SEARHING FOR DEVICES

  public void searchDeviceStart() {
    deviceList = null;
    numberOfDevices = 0;
    safeTCPWrite(TCP_CMD_SCAN + ',' + TCP_ACTION_START + TCP_STOP);
  }

  public void searchDeviceStop() {
    safeTCPWrite(TCP_CMD_SCAN + ',' + TCP_ACTION_STOP + TCP_STOP);
  }

  public boolean searchDeviceAdd(String XTLocalName) {
    if (numberOfDevices == 0) {
      numberOfDevices++;
      deviceList = new String[numberOfDevices];
      deviceList[0] = XTLocalName;
      return true;
    } else {
      boolean willAddToDeviceList = true;
      for (int i = 0; i < numberOfDevices; i++) {
        if (XTLocalName.equals(deviceList[i])) {
          willAddToDeviceList = false;
          break;
        }
      }
      if (willAddToDeviceList) {
        numberOfDevices++;
        String[] tempList = new String[numberOfDevices];
        arrayCopy(deviceList, tempList);
        tempList[numberOfDevices - 1] = XTLocalName;
        deviceList = tempList;
        return true;
      }
    }
    return false;
  }

  // CONNECTION
  public void connectWIFI(String id) {
    safeTCPWrite(TCP_CMD_CONNECT + "," + id + TCP_STOP);
  }

  public void disconnectWIFI() {
    waitingForResponse = true;
    safeTCPWrite(TCP_CMD_DISCONNECT + TCP_STOP);
  }

  public void updateSyncState() {
    //has it been 3000 milliseconds since we initiated the serial port? We want to make sure we wait for the OpenBCI board to finish its setup()
    if ((millis() - prevState_millis > COM_INIT_MSEC) && (prevState_millis != 0) && (state == openBCI.STATE_COMINIT) ) {
      // We are synced and ready to go!
      state = STATE_SYNCWITHHARDWARE;
      println("XTREMIS: Sending reset command");
      // serial_openBCI.write('v');
    }
  }

  /**
   * @description Sends a start streaming command to the XT Node module.
   */
  void startDataTransfer() {
    changeState(STATE_NORMAL);  // make sure it's now interpretting as binary
    println("XTREMIS: startDataTransfer(): sending \'" + command_startBinary);
    safeTCPWrite(TCP_CMD_COMMAND + "," + command_startBinary + TCP_STOP);
  }

  /**
   * @description Sends a stop streaming command to the XT Node module.
   */
  public void stopDataTransfer() {
    changeState(STATE_STOPPED);  // make sure it's now interpretting as binary
    println("XTREMIS: stopDataTransfer(): sending \'" + command_stop);
    safeTCPWrite(TCP_CMD_COMMAND + "," + command_stop + TCP_STOP);
  }

  /**
   * @description Write to TCP server
   * @params out {String} - The string message to write to the server.
   * @returns {boolean} - True if able to write, false otherwise.
   */
  public boolean safeTCPWrite(String out) {
    try {
      tcpClient.write(out);
      return true;
    } 
    catch (Exception e) {
      println("Error: Attempted to TCP write with no server connection initialized");
      return false;
    }
    // return false;
    // if (nodeProcessHandshakeComplete) {
    //   try {
    //     tcpClient.write(out);
    //     return true;
    //   } catch (NullPointerException e) {
    //     println("Error: Attempted to TCP write with no server connection initialized");
    //     return false;
    //   }
    // } else {
    //   println("Waiting on node handshake!");
    //   return false;
    // }
  }

  private void printXT(String msg) {
    print("XTREMIS: "); 
    println(msg);
  }

  public int changeState(int newState) {
    state = newState;
    prevState_millis = millis();
    return 0;
  }

  // Channel setting
  //activate or deactivate an EEG channel...channel counting is zero through nchan-1
  public void changeChannelState(int Ichan, boolean activate) {
    if (connected) {
      if ((Ichan >= 0)) {
        if (activate) {
          println("XTREMIS: changeChannelState(): activate: sending " + command_activate_channel[Ichan]);
          safeTCPWrite(TCP_CMD_COMMAND + "," + command_activate_channel[Ichan] + TCP_STOP);
          w_timeSeries.hsc.powerUpChannel(Ichan);
        } else {
          println("XTREMIS: changeChannelState(): deactivate: sending " + command_deactivate_channel[Ichan]);
          safeTCPWrite(TCP_CMD_COMMAND + "," + command_deactivate_channel[Ichan] + TCP_STOP);
          w_timeSeries.hsc.powerDownChannel(Ichan);
        }
      }
    }
  }

  /**
   * Used to start accel data mode. Accel arrays will arrive asynchronously!
   */
  public void accelStart() {
    println("XTREMIS: accell: START");
    safeTCPWrite(TCP_CMD_ACCEL + "," + TCP_ACTION_START + TCP_STOP);
    accelModeActive = true;
  }

  /**
   * Used to stop accel data mode. Some accel arrays may arrive after stop command
   *  was sent by this function.
   */
  public void accelStop() {
    println("XTREMIS: accel: STOP");
    safeTCPWrite(TCP_CMD_ACCEL + "," + TCP_ACTION_STOP + TCP_STOP);
    accelModeActive = false;
  }

  /**
   * Used to start impedance testing. Impedances will arrive asynchronously!
   */
  public void impedanceStart() {
    println("XTREMIS: impedance: START");
    safeTCPWrite(TCP_CMD_IMPEDANCE + "," + TCP_ACTION_START + TCP_STOP);
    checkingImpedance = true;
  }

  /**
   * Used to stop impedance testing. Some impedances may arrive after stop command
   *  was sent by this function.
   */
  public void impedanceStop() {
    println("XTREMIS: impedance: STOP");
    safeTCPWrite(TCP_CMD_IMPEDANCE + "," + TCP_ACTION_STOP + TCP_STOP);
    checkingImpedance = false;
  }

  /**
   * Puts the XT in bootloader mode.
   */
  public void enterBootloaderMode() {
    println("XTREMIS: Entering Bootloader Mode");
    safeTCPWrite(TCP_CMD_COMMAND + "," + XT_BOOTLOADER_MODE + TCP_STOP);
    delay(500);
    disconnectWIFI();
    haltSystem();
    initSystemButton.setString("START SYSTEM");
    controlPanel.open();
    output("XT now in bootloader mode! Enjoy!");
  }
};