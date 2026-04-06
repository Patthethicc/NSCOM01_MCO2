import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from File_Transfer_Functions.RTP import send_audio_file
from File_Transfer_Functions.RTCP import send_rtcp_report
import socket
from dotenv import load_dotenv
from Packets.SIP_packet import SIP_packet
from Connection_Functions.Send import Send_func

load_dotenv()

SENDER_IP = os.getenv("SENDER_IP")
SENDER_PORT = int(os.getenv("SENDER_PORT"))
RECEIVER_IP = os.getenv("RECEIVER_IP")
RECEIVER_PORT = int(os.getenv("RECEIVER_PORT"))
flag = True
    
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.bind((SENDER_IP, SENDER_PORT))

sock.settimeout(5.0)

print(f"UDP server listening on {SENDER_IP}:{SENDER_PORT}\n\n")


sender = Send_func(sender_ip=SENDER_IP, sender_port=SENDER_PORT, receiver_ip=RECEIVER_IP, receiver_port=RECEIVER_PORT, socket=sock)

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
    print("\nType 'S' to send an audio file or 'B' to end the call...\n")
    choice = input().upper()

    if choice == 'S':
        print("\nEnter the path to the .wav file:")
        file_path = input()
        
        
        seq, ts = send_audio_file(file_path, SENDER_IP, SENDER_PORT, RECEIVER_IP, RECEIVER_PORT, sock)
        
        
        send_rtcp_report(sock, RECEIVER_IP, RECEIVER_PORT, ssrc=12345, 
                         timestamp=ts, packet_count=seq, octet_count=seq*160)
        
    elif choice == 'B':
        sender.send_bye(packet)

        print(f"\n\nEnding connection with {sender.receiver_ip}:{sender.receiver_port}...\n\n")

        try:
            data, addr = sock.recvfrom(4096)
            packet = SIP_packet.from_bytes(data)

            if packet.start_line.startswith("SIP/2.0 200 OK"):
                print(f"\nReceived 200 OK from {addr}.\n\n")
                flag = False
            else:
                print(f"\nReceived unexpected response from {addr}: {packet.start_line}. Still ending the program.")
                flag = False

        except socket.timeout:
            print(f"Timeout: No response from {sender.receiver_ip}:{sender.receiver_port}. Ending the Program.\n\n")
            flag = False

        except ConnectionResetError:
            print("\nRemote host successfully closed the connection. Ending the Program.\n\n")
            flag = False


print("Thank you for using the program...")
sock.close()