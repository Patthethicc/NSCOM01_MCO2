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

## Description of the Implemented Features
## Test Cases and Sample Outputs