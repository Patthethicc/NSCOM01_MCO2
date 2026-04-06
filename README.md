# NSCOM01_MCO2
**Real-Time Communication Project**

## Instructions for Compiling and Running the Program

### **Prerequisites & Setup**
1. Ensure Python 3.x is installed on your system.
2. Install the required environment variable library:
   ```bash
   pip install python-dotenv

### **For the Main Specs**
1. Set up the .env file to this format
  ``` bash
  SENDER_IP=""
  SENDER_PORT=""
  RECEIVER_IP=""
  RECEIVER_PORT=""
  ```
2. For two devices make sure that the ip addresses are different but the port remains the same. For one device, make sure that the ports are different but the ip address remains the same.

3. In the first device run the sender file
  ```bash
  python Main_Specs/Sender_Main.py
  ```
4. For the second device, run the receiver file
  ```bash
  python Main_Specs/Receiver_Main.py
  ```
5. Follow the terminal prompts to initiate a connection and send a .wav file.

### **For the Bonus Specs**
1. Set up the .env file to this format
  ``` bash
  SENDER_IP=""
  SENDER_PORT=""
  RECEIVER_IP=""
  RECEIVER_PORT=""
  ```
2. For two devices make sure that the ip addresses are different but the port remains the same. For one device, make sure that the ports are different but the ip address remains the same.

3. Press I on either terminal to call the other user.

**Note: Press ENTER after connecting to start the microphone for each side**

## Description of the Implemented Features

### **Packets**
 - **SIP Packets:** Custom string-based packet generation parsing text-based headers for standard SIP methods (INVITE, 200 OK, ACK, BYE).
 - **RTP Packets:** Binary packing and unpacking using the struct module. Extracts a 12-byte header containing Payload Type, Sequence Numbers (to prevent UDP out-of-order distortion), and Timestamps.
 - **RTCP Packets:** Sender Report generation to track packet counts and octet counts for session statistics.

### **Sender**
- Manages outgoing SIP requests and waits for specific responses. 
- Uses libraries to automatically read .wav files selected by the user which is then sent to the receiver.

### **Receiver**
- Receives SIP packets and sends specific startlines for the sender to acknowledge.
- Plays audio once all RTP packets are sent and received.

### **Bonus**
- Two-way communication along with real time microphone communication is implemented.

## Test Cases and Sample Outputs