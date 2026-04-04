import sys
import os
import wave
import winsound 

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import socket
from dotenv import load_dotenv
from Packets.SIP_packet import SIP_packet
from Packets.RTP_packet import RTPPacket
from Connection_Functions.Receive import Recv_func

load_dotenv()

RECEIVER_IP = os.getenv("RECEIVER_IP")
RECEIVER_PORT = int(os.getenv("RECEIVER_PORT"))
flag = True

received_audio_payloads = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.bind((RECEIVER_IP, RECEIVER_PORT))
sock.settimeout(5.0)

print(f"UDP server listening on {RECEIVER_IP}:{RECEIVER_PORT}\n\n")
print("Waiting for INVITE...\n\n")

while flag:
    try:
        data, addr = sock.recvfrom(4096)
        
        
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
                    flag = False 

                elif packet.start_line.startswith("ACK"):
                    print(f"Received ACK from {addr}. Connection Established. Receiving media...\n")
                
                else:
                    receiver.recv_error(packet, "400", "Bad Request") [cite: 55]
                    
            except Exception as e:
                print(f"Failed to parse SIP packet: {e}")
        
        else:
           
            try:
                rtp_pkt = RTPPacket.from_bytes(data)
                received_audio_payloads.append(rtp_pkt.payload)
                
                if rtp_pkt.sequence_number % 50 == 0:
                    print(f"Receiving RTP... Seq: {rtp_pkt.sequence_number}")
            except Exception:
                pass

    except socket.timeout:
        if not received_audio_payloads: 
            print(f"Awaiting incoming connections...")
        continue


if received_audio_payloads:
    output_file = "received_audio.wav"
    print(f"\nSaving received audio to {output_file}...")
    try:
        with wave.open(output_file, 'wb') as wav_file:
            
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2) 
            wav_file.setframerate(8000)
            wav_file.writeframes(b''.join(received_audio_payloads))
        
        print("File saved successfully!")
        
        
        print("Starting Auto-Playback...")
        winsound.PlaySound(output_file, winsound.SND_FILENAME)
        
    except Exception as e:
        print(f"Error handling audio: {e}")

print("\nThank you for using the program...")
sock.close()