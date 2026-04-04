import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import socket
from Packets.SIP_packet import SIP_packet
from Connection_Functions.Send import Send_func

SENDER_IP = ""
SENDER_PORT = 0
flag = True
    
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.bind((SENDER_IP, SENDER_PORT))
#set timeout to 5 seconds
sock.settimeout(5.0)

print(f"UDP server listening on {SENDER_IP}:{SENDER_PORT}\n\n")

#Add the address and port of the receiver over here!
sender = Send_func(sender_ip=SENDER_IP, sender_port=SENDER_PORT, receiver_ip="", receiver_port=0, socket=sock)

while flag:
    print("Press Enter to send an INVITE...")
    input()

    sender.send_invite()

    print(f"\n\nSending INVITE to {sender.receiver_ip}:{sender.receiver_port}...\n\n")

    try:
        data, addr = sock.recvfrom(4096)
        packet = SIP_packet.from_bytes(data)

        if packet.start_line.startswith("SIP/2.0 200 OK"):
            print(f"Received 200 OK from {addr}.\n\n")
            sender.send_ack(packet)
            flag = False
        else:
            print(f"Received unexpected response from {addr}: {packet.start_line}")
            sender.send_ack(packet)

    except socket.timeout:
        print(f"Timeout: No response from {sender.receiver_ip}:{sender.receiver_port}. Please try again.")

flag = True

while flag:
    print("Type 'S' to send an audio file or 'B' to end the call...\n\n")
    choice = input().upper()

    if choice == 'S':
        #Ask user for file -> Loop through file and blast RTP packets (JERU)
        pass
    elif choice == 'B':
        sender.send_bye()

        print(f"\n\nEnding connection with {sender.receiver_ip}:{sender.receiver_port}...\n\n")

        try:
            data, addr = sock.recvfrom(4096)
            packet = SIP_packet.from_bytes(data)

            if packet.start_line.startswith("SIP/2.0 200 OK"):
                print(f"Received 200 OK from {addr}.\n\n")
                flag = False
            else:
                print(f"Received unexpected response from {addr}: {packet.start_line}. Still ending the program.")
                flag = False

        except socket.timeout:
            print(f"Timeout: No response from {sender.receiver_ip}:{sender.receiver_port}. Ending the Program.\n\n")
            flag = False


print("Thank you for using the program...")
sock.close()