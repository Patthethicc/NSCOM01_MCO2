import socket
import threading
import time
import os

#IP Configuration
DEVICE1_IP = os.getenv("SENDER_IP")
DEVICE1_PORT = int(os.getenv("SENDER_PORT"))
DEVICE2_IP = os.getenv("RECEIVER_IP")
DEVICE2_PORT = int(os.getenv("RECEIVER_PORT"))

is_connected = False    # True once the SIP ACK is exchanged
is_calling = False      # True while waiting for a 200 OK
flag = True     # Keeps the app alive

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.bind((DEVICE1_IP, DEVICE1_PORT))

print(f"UDP server listening on {DEVICE1_IP}:{DEVICE1_PORT}\n")

while flag:
    if not is_connected:
        command = input("\nType 'I' to invite or 'Q' to quit: ").upper()
        if command == 'I':
                target = input("Enter Target IP: ")
                # Trigger SIP_Sender.send_invite(target)
        elif command == 'Q':
                is_listening = False
    else:
        command = input("\nType 'B' to disconnect: ").upper()
        if command == 'B':
            # Trigger SIP_Sender.send_bye()
            is_connected = False