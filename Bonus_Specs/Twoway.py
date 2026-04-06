import sys
import os
import socket
import threading
import time
import pyaudio
from dotenv import load_dotenv

# Places the file in the root directory to access all modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Packets.SIP_packet import SIP_packet
from Packets.RTP_packet import RTPPacket
from Connection_Functions.Send import Send_func
from Connection_Functions.Receive import Recv_func
from File_Transfer_Functions.RTCP import send_rtcp_report 

load_dotenv()

# Env variables for the user
DEVICE1_IP = os.getenv("SENDER_IP")
DEVICE1_PORT = int(os.getenv("SENDER_PORT"))
DEVICE2_IP = os.getenv("RECEIVER_IP")
DEVICE2_PORT = int(os.getenv("RECEIVER_PORT"))

# Global state variables
is_connected = False   
is_calling = False      
is_listening = True     
current_packet = None   
bye_received = False

# Audio settings
CHUNKS = 160            
RATE = 8000
FORMAT = pyaudio.paInt16
CHANNELS = 1

# Function to capture audio from the microphone and send it as RTP packets in a thread
def rtp_send_thread(sock, target_ip, target_port):
    global is_connected
    p = pyaudio.PyAudio()
    # Sets up microphone   
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNKS)
    
    seq, ts = 0, 0
    ssrc = 12345

    # Ayy talk to me! Talk to yourself! 
    print("\nMicrophone active... Talk to me!")

    while is_connected:
        try:
            # Sends chunks of audio data as RTP packets
            data = stream.read(CHUNKS, exception_on_overflow=False)
            rtp_pkt = RTPPacket(payload_type=0, sequence_number=seq, timestamp=ts, ssrc=ssrc, payload=data)
            sock.sendto(rtp_pkt.to_bytes(), (target_ip, target_port))
            
            # Sends RTCP report
            if seq % 100 == 0:
                from File_Transfer_Functions.RTCP import send_rtcp_report
                send_rtcp_report(sock, target_ip, target_port, ssrc, ts, seq, seq * CHUNKS)

            seq = (seq + 1) % 65536
            ts += CHUNKS
        except Exception as e:
            print(f"\nErrpr in Mic Stream: {e}")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Microphone closed.")


# Function to receive SIP and RTP packets in a separate thread
def receive_thread(sock, local_ip, local_port, sender_obj):

    global is_connected, is_listening, is_calling, current_packet, bye_received
    
    p_out = pyaudio.PyAudio()
    out_stream = p_out.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)

    # Main loop to receive packets
    while is_listening:
        try:
            data, addr = sock.recvfrom(4096)
            
            # Checks if the packet is a SIP message based on the start line
            if data.startswith(b"INVITE") or data.startswith(b"SIP") or data.startswith(b"ACK") or data.startswith(b"BYE"):
                packet = SIP_packet.from_bytes(data)
                receiver = Recv_func(receiver_ip=local_ip, receiver_port=local_port, socket=sock, sender_ip=addr[0], sender_port=addr[1])
                
                # Handles different SIP messages based on the start line and updates the call state accordingly
                if packet.start_line.startswith("INVITE"):
                    
                    if is_calling and local_ip > addr[0]:
                        continue 
                    
                    print(f"\nReceived INVITE from {addr}")
                    receiver.recv_invite(packet)
                    bye_received = False 
                    is_connected = True 
                    is_calling = False
                    current_packet = packet

                elif packet.start_line.startswith("BYE"):
                    print(f"\nReceived BYE. Ending call...") 
                    receiver.recv_bye(packet)
                    is_connected = False 
                    bye_received = True
                    current_packet = packet
                    
                elif packet.start_line.startswith("ACK"):
                    print("\nACK Received. Call Established.") 
                    is_connected = True
                    current_packet = packet

                # Sends ACK for OK responses
                elif packet.start_line.startswith("SIP/2.0 200 OK"):
                    print(f"\nReceived 200 OK from {addr}.") 
                    sender_obj.send_ack(packet)
                    is_connected = True
                    is_calling = False
                    current_packet = packet 

            else:
                try:
                    # Writes received RTP packets to the audio output stream
                    rtp_pkt = RTPPacket.from_bytes(data)
                    out_stream.write(rtp_pkt.payload)
                except Exception:
                    pass

        except socket.timeout:
            continue
        except OSError:
            break

    out_stream.stop_stream()
    out_stream.close()
    p_out.terminate()


# Sets up the UDP socket 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.bind((DEVICE1_IP, DEVICE1_PORT))
sock.settimeout(1.0)

# Creates a sender object to handle sending SIP and RTP packets
sender = Send_func(sender_ip=DEVICE1_IP, sender_port=DEVICE1_PORT, 
                   receiver_ip=DEVICE2_IP, receiver_port=DEVICE2_PORT, socket=sock)

# Creates a thread to listen for incoming SIP and RTP packets
rx_thread = threading.Thread(target=receive_thread, args=(sock, DEVICE1_IP, DEVICE1_PORT, sender), daemon=True)
rx_thread.start()

print(f"Two-Way SIP Client Active on {DEVICE1_IP}:{DEVICE1_PORT}")

# Main loop for call handling
try:
    while is_listening:
        # If not connected, prompts the user to send an INVITE or quit.
        if not is_connected:
            cmd = input("\n'I' to Invite, 'Q' to Quit: ").upper()
            if cmd == 'I':
                bye_received = False
                is_calling = True
                sender.send_invite() 
            elif cmd == 'Q':
                is_listening = False
        else:

            # Creates a thread to capture audio from the microphone and send it as RTP packets while the call is active
            audio_thread = threading.Thread(target=rtp_send_thread, args=(sock, DEVICE2_IP, DEVICE2_PORT))
            audio_thread.start()
            
            cmd = input("\nYou are currently in call, press 'B' to Disconnect: ").upper()
            # Ends call
            if cmd == 'B':
                is_connected = False
                sender.send_bye(current_packet) 
                time.sleep(1) 

except KeyboardInterrupt:
    is_listening = False

sock.close()
print("\nThank you for using the program!")