import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import socket
import threading
import time
from dotenv import load_dotenv
from Packets.SIP_packet import SIP_packet
from Connection_Functions.Send import Send_func
from Packets.RTP_packet import RTPPacket
from Connection_Functions.Receive import Recv_func



load_dotenv()
#IP Configuration
DEVICE1_IP = os.getenv("SENDER_IP")
DEVICE1_PORT = int(os.getenv("SENDER_PORT"))
DEVICE2_IP = os.getenv("RECEIVER_IP")
DEVICE2_PORT = int(os.getenv("RECEIVER_PORT"))

is_connected = False    # True once the SIP ACK is exchanged
is_calling = False      # True while waiting for a 200 OK
is_listening = True 
current_packet = None    # Keeps track of current packet
bye = False

def receive_thread(sock, DEVICE1_IP, DEVICE1_PORT, received_audio_payloads, sender):
    
    global is_connected, is_listening, is_calling, current_packet, bye
    
    while is_listening:
        try:
            data, addr = sock.recvfrom(4096)
            
            if data.startswith(b"INVITE") or data.startswith(b"SIP") or data.startswith(b"ACK") or data.startswith(b"BYE"):
                packet = SIP_packet.from_bytes(data)
                receiver = Recv_func(receiver_ip=DEVICE1_IP, receiver_port=DEVICE1_PORT, socket=sock, sender_ip=addr[0], sender_port=addr[1])

                if packet.start_line.startswith("INVITE"):
                    # Glare handling
                    if is_calling:
                        print("\n[WARNING] Call collision detected (Glare)!")
                        if DEVICE1_IP > receiver.sender_ip:
                            continue 
                        else:
                            is_calling = False 

                    print(f"Received INVITE from {addr}. Press ENTER to acknowledge if you still see I or Q option\n")
                    receiver.recv_invite(packet)
                    bye = False 
                    is_connected = True 
                    is_calling = False
                    current_packet = packet

                elif packet.start_line.startswith("BYE"):
                    print(f"Received BYE from {addr}. Terminating call...\n")
                    receiver.recv_bye(packet)
                    is_connected = False 
                    bye = True
                    current_packet = packet
                    
                elif packet.start_line.startswith("ACK"):
                    print(f"Received ACK from {addr}. Connection Established. Receiving media...\n")
                    if not bye:
                        is_connected = True
                        current_packet = packet

                elif packet.start_line.startswith("SIP/2.0 200 OK"):
                    print(f"Received 200 OK from {addr}.\n\n")
                    sender.send_ack(packet)
                    if not bye:
                        is_connected = True
                        is_calling = False
                        current_packet = packet 
                else:
                    print(f"Received unexpected response from {addr}: {packet.start_line}")
                    sender.send_ack(packet)

                
            else:
                rtp_pkt = RTPPacket.from_bytes(data)
                #place RTP logic here
                received_audio_payloads.append(rtp_pkt.payload)
                
                
        except socket.timeout:
            continue

        except OSError:
            break

# ADD RTP and RTCP receive function here

# ADD RTP and RTCP send function here

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.bind((DEVICE1_IP, DEVICE1_PORT))
sock.settimeout(1.0)

print(f"UDP server listening on {DEVICE1_IP}:{DEVICE1_PORT}\n")

sender = Send_func(sender_ip=DEVICE1_IP, sender_port=DEVICE1_PORT, receiver_ip=DEVICE2_IP, receiver_port=DEVICE2_PORT, socket=sock)

audio_buffer = []
recv_thread = threading.Thread(target=receive_thread, args=(sock, DEVICE1_IP, DEVICE1_PORT, audio_buffer, sender), daemon=True)
recv_thread.start()

# add the thread for RTP receive here

# add th thread for RTP send here

while is_listening:
    if not is_connected:
        command = input("\nType 'I' to invite or 'Q' to quit: ").upper()
        if command == 'I':
                bye = False
                is_calling = True  # We are now dialing!
                sender.send_invite()
        elif command == 'Q':
                is_listening = False
    else:
        command = input("\nType 'B' to disconnect: ").upper()
        if command == 'B':
            bye = True
            sender.send_bye(current_packet)
            is_connected = False

recv_thread.join()
sock.close()

print("\n\nThank you for using the program!\n")