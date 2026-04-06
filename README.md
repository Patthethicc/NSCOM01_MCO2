# NSCOM01_MCO2
**Real-Time Communication Project**

## Instructions for Compiling and Running the Program

### **Prerequisites & Setup**
1. Ensure Python 3.x is installed on your system.
2. Install the required environment variable library:
   ```bash
   pip install python-dotenv
   ```

### **For the Main Specs**
1. Set up the .env file to this format:
  ``` bash
  SENDER_IP=""
  SENDER_PORT=""
  RECEIVER_IP=""
  RECEIVER_PORT=""
  ```
2. For two devices make sure that the ip addresses are different but the port remains the same. For one device, make sure that the ports are different but the ip address remains the same.

3. In the first device run the sender file:
  ```bash
  python Main_Specs/Sender_Main.py
  ```
4. For the second device, run the receiver file:
  ```bash
  python Main_Specs/Receiver_Main.py
  ```
5. Follow the terminal prompts to initiate a connection and send a .wav file.

### **For the Bonus Specs**
1. Set up the .env file to this format:
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
 - **SDP Packets:** Contains the required headers for needed information for the INVITE.
 - **RTP Packets:** Binary packing and unpacking using the struct module. Extracts a 12-byte header containing Payload Type, Sequence Numbers (to prevent UDP out-of-order distortion), and Timestamps.
 - **RTCP Packets:** Sender Report generation to track packet counts and octet counts for session statistics.

### **Sender**
- Manages outgoing SIP requests and waits for specific responses. 
- Uses libraries to automatically read .wav files selected by the user which is then sent to the receiver.

### **Receiver**
- Receives SIP packets and sends specific startlines for the sender to acknowledge.
- Plays audio once all RTP packets are sent and received.

### **Bonus**
- Two-way communication along with real time microphone communication is implemented through threading and pyaudio.

## Test Cases and Sample Outputs

### **Test Case 1: Session Initiation (Main Specs)**
- **What to do:** With Receiver_Main.py listening, press Enter on the Sender_Main.py terminal to send the initial INVITE.
- **Sample Output:** 
  - **Sender:** Prints Sending INVITE...
  - **Receiver:** Catches the packet, prints Received INVITE, and replies with a 200 OK.
  - **Sender:** Catches the 200 OK, successfully establishing the session, and drops into the media selection menu.

### **Test Case 2: Audio File Streaming (Main Specs)**
- **What to do:** Chunks the audio file and streams RTP packets over UDP.
- **Sample Output:**
  - **Sender:** Chunks the audio file and streams RTP packets over UDP.
  - **Receiver:** Prints periodic sequence updates. Once the transmission completes, the socket times out, saving and playing the received .wav file seamlessly without out-of-order distortion.

### **Test Case 3: Call Termination (Main Specs)**
- **What to do:** The user types B on the Sender terminal to end the active call.
- **Sample Output:**
  - **Receiver:** Catches the BYE packet, prints Terminating call..., and cleanly exits.
  - **Sender:** Gracefully catches the receiver's socket closure (ConnectionResetError), prints Remote host successfully closed the connection, and exits without tracebacks.

### **Test Case 4: Peer-to-Peer Session Initiation (Bonus Specs)**
- **What to do:** Both users run the Twoway.py file. User 1 types I to invite User 2.
- **Sample Output:** 
  - **User 1:** State changes to is_calling = True and sends an INVITE packet.
  - **User 2:** The background listening thread intercepts the INVITE, prints an incoming call notification, auto-answers with a 200 OK, and switches to the connected state.
  - **User 1:** Receives the 200 OK, sends an ACK, and both terminals sync to the [IN CALL] menu. (If both users type I simultaneously, the node with the higher IP yields to prevent a glare collision).

  ### **Test Case 5: Real-Time Two-Way Microphone Audio (Bonus Specs)**
- **What to do:** After establishing a connection, both users press Enter to activate their PyAudio microphone streams. Both users speak into their microphones at the same time.
- **Sample Output:** 
  - **Background Sender Threads:** PyAudio captures live microphone data in small chunks, wraps them in RTP packets, and streams them continuously over the sockets.
  - **Background Receiver Threads:** Catches incoming RTP packets on the fly, extracts the payload, and pushes it directly to the PyAudio output stream. Both users can hear each other's live voices in near real-time over the network, demonstrating full-duplex VoIP functionality.

