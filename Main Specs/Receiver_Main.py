import sys
import os
import wave # Required for saving the received audio

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import socket
from dotenv import load_dotenv
from Packets.SIP_packet import SIP_packet
from Packets.RTP_packet import RTPPacket # Import your RTP class
from Connection_Functions.Receive import Recv_func

load_dotenv()

RECEIVER_IP = os.getenv("RECEIVER_IP")
RECEIVER_PORT = int(os.getenv("RECEIVER_PORT"))
flag = True

# Buffer to store audio payloads during the call
received_audio_payloads = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.bind((RECEIVER_IP, RECEIVER_PORT))
sock.settimeout(5.0)

print(f"UDP server listening on {RECEIVER_IP}:{RECEIVER_PORT}\n\n")
print("Waiting for INVITE...\n\n")

while flag:
    try:
        data, addr = sock.recvfrom(4096)
        
        # 1. Distinguish between SIP (Text) and RTP (Binary)
        # SIP packets start with a method name or SIP version string
        if data.startswith(b"INVITE") or data.startswith(b"SIP") or data.startswith(b"ACK") or data.startswith(b"BYE"):
            try:
                packet = SIP_packet.from_bytes(data)
                receiver = Recv_func(receiver_ip=RECEIVER_IP, receiver_port=RECEIVER_PORT, socket=sock, sender_ip=addr[0], sender_port=addr[1])

                if packet.start_line.startswith("INVITE"):
                    print(f"Received INVITE from {addr}.\n")
                    receiver.recv_invite(packet)

                elif packet.start_line.startswith("BYE"):
                    print(f"Received BYE from {addr}. Terminating call...\n")
                    receiver.recv_bye(packet)
                    flag = False # Exit the loop to save the file

                elif packet.start_line.startswith("ACK"):
                    print(f"Received ACK from {addr}. Connection Established. Receiving media...\n")
                
                else:
                    receiver.recv_error(packet, "400", "Bad Request")
                    
            except Exception as e:
                print(f"Failed to parse SIP packet: {e}")
        
        else:
            # 2. Handle RTP Media Packets
            try:
                rtp_pkt = RTPPacket.from_bytes(data)
                # Store the raw audio data from the RTP payload 
                received_audio_payloads.append(rtp_pkt.payload)
                
                # Optional: Print progress every 50 packets to avoid console spam
                if rtp_pkt.sequence_number % 50 == 0:
                    print(f"Receiving RTP... Seq: {rtp_pkt.sequence_number}")
            except Exception as e:
                # This could be RTCP data or a malformed packet
                pass

    except socket.timeout:
        if not received_audio_payloads: # Only print if we aren't currently in a call
            print(f"Awaiting incoming connections...")
        continue

# 3. Post-Call: Save the audio to a file [cite: 53, 81]
if received_audio_payloads:
    output_file = "received_audio.wav"
    print(f"\nSaving received audio to {output_file}...")
    try:
        with wave.open(output_file, 'wb') as wav_file:
            # Standard SIP settings: 1 channel, 2 bytes per sample, 8000Hz [cite: 52]
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2) 
            wav_file.setframerate(8000)
            wav_file.writeframes(b''.join(received_audio_payloads))
        print("File saved successfully! You can now play 'received_audio.wav'.")
    except Exception as e:
        print(f"Error saving audio file: {e}")

print("Thank you for using the program...\n")
sock.close()