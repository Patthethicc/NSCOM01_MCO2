import sys
import os
import wave
import winsound
import socket
import time
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Packets.SIP_packet import SIP_packet
from Packets.RTP_packet import RTPPacket
from Connection_Functions.Receive import Recv_func

load_dotenv()

RECEIVER_IP = os.getenv("RECEIVER_IP")
RECEIVER_PORT = int(os.getenv("RECEIVER_PORT"))
flag = True

received_audio_payloads = {}
last_packet_time = None 
session_active = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.bind((RECEIVER_IP, RECEIVER_PORT))
sock.settimeout(1.0) 

print(f"UDP server listening on {RECEIVER_IP}:{RECEIVER_PORT}\n")

def save_and_play_session(payloads_dict):
    """Utility to finalize a media burst without ending the script."""
    if not payloads_dict:
        return
    
    timestamp = int(time.time())
    output_file = f"received_media_{timestamp}.wav"
    print(f"\n---> Media burst finished. Saving to {output_file}...")
    
    try:
        sorted_keys = sorted(payloads_dict.keys())
        sorted_payloads = [payloads_dict[seq] for seq in sorted_keys]
        
        with wave.open(output_file, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2) 
            wav_file.setframerate(8000)
            wav_file.writeframes(b''.join(sorted_payloads))
        
        print(f"---> Playing {output_file} now...")
        winsound.PlaySound(output_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print(f"Playback Error: {e}")

while flag:
    try:
        data, addr = sock.recvfrom(4096)
        
        if data.startswith(b"INVITE") or data.startswith(b"SIP") or data.startswith(b"ACK") or data.startswith(b"BYE"):
            try:
                packet = SIP_packet.from_bytes(data)
                receiver = Recv_func(receiver_ip=RECEIVER_IP, receiver_port=RECEIVER_PORT, socket=sock, sender_ip=addr[0], sender_port=addr[1])

                if packet.start_line.startswith("INVITE"):
                    print(f"Received INVITE from {addr}")
                    receiver.recv_invite(packet)
                    session_active = True
                
                elif packet.start_line.startswith("BYE"):
                    print("\nReceived BYE. Closing program...")
                    
                    save_and_play_session(received_audio_payloads)
                    flag = False 
                
                elif packet.start_line.startswith("ACK"):
                    print("ACK Received. Call Established.")
            except Exception as e:
                print(f"SIP Parse Error: {e}")
        
        else:
            
            try:
                rtp_pkt = RTPPacket.from_bytes(data)
                received_audio_payloads[rtp_pkt.sequence_number] = rtp_pkt.payload
                last_packet_time = time.time()
                
                if rtp_pkt.sequence_number % 50 == 0:
                    print(f"Receiving RTP... Seq: {rtp_pkt.sequence_number}")
            except Exception:
                pass

    except socket.timeout:
        
        if received_audio_payloads and last_packet_time:
            if time.time() - last_packet_time > 2.0:

                save_and_play_session(received_audio_payloads)
                
                received_audio_payloads = {}
                last_packet_time = None
                print("\nReady for next media stream or BYE...")
        continue

print("\nThank you for using the program...")
sock.close()