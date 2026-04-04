import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import socket
from dotenv import load_dotenv
from Packets.SIP_packet import SIP_packet
from Connection_Functions.Receive import Recv_func

load_dotenv()

RECEIVER_IP = os.getenv("RECEIVER_IP")
RECEIVER_PORT = int(os.getenv("RECEIVER_PORT"))
flag = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.bind((RECEIVER_IP, RECEIVER_PORT))
#set timeout to 5 seconds
sock.settimeout(5.0)

print(f"UDP server listening on {RECEIVER_IP}:{RECEIVER_PORT}\n\n")

print("Waiting for INVITE...\n\n")

while flag:
    try:
        data, addr = sock.recvfrom(4096)

        receiver = Recv_func(receiver_ip=RECEIVER_IP, receiver_port=RECEIVER_PORT, socket=sock, sender_ip=addr[0], sender_port=addr[1])

        try:
            packet = SIP_packet.from_bytes(data)
        except Exception as e:
            print(f"Failed to parse incoming packet: {e}")
            continue

        if packet.start_line.startswith("INVITE"):
            print(f"Received INVITE from {addr}.\n\n")
            receiver.recv_invite(packet)

        elif packet.start_line.startswith("BYE"):
            print(f"Received BYE from {addr}.\n\n")
            receiver.recv_bye(packet)

            flag = False

        elif packet.start_line.startswith("ACK"):
            print(f"Received ACK from {addr}.\n\n")
            print("Connection Established... Waiting for next process...\n\n")

            # Initialize RTP port -> Loop to receive packets, strip headers, and play audio or store then play audio (JERU)
            #place code here
        
        else:
            print(f"Received unexpected packet from {addr}: {packet.start_line}\n\n")
            receiver.recv_error(packet, "400", "Bad Request")

    except socket.timeout:
        print(f"Awaiting incoming connections...\n\n")
        continue

print("Thank you for using the program...\n\n")
sock.close()

