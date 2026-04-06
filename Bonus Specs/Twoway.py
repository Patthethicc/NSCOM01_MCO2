import sys
import os
import socket
import threading
import time
import pyaudio
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Packets.SIP_packet import SIP_packet
from Packets.RTP_packet import RTPPacket
from Connection_Functions.Send import Send_func
from Connection_Functions.Receive import Recv_func
from File_Transfer_Functions.RTCP import send_rtcp_report 

load_dotenv()


DEVICE1_IP = os.getenv("SENDER_IP")
DEVICE1_PORT = int(os.getenv("SENDER_PORT"))
DEVICE2_IP = os.getenv("RECEIVER_IP")
DEVICE2_PORT = int(os.getenv("RECEIVER_PORT"))


is_connected = False   
is_calling = False      
is_listening = True     
current_packet = None   
bye_received = False


CHUNKS = 160            
RATE = 8000
FORMAT = pyaudio.paInt16
CHANNELS = 1


def rtp_send_thread(sock, target_ip, target_port):
    """Bonus: Real-time microphone capture and transmission """
    global is_connected
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNKS)
    
    seq, ts = 0, 0
    ssrc = 12345
    print("\n[AUDIO] Microphone active. Sending live stream...")

    while is_connected:
        try:
            data = stream.read(CHUNKS, exception_on_overflow=False)
            rtp_pkt = RTPPacket(payload_type=0, sequence_number=seq, timestamp=ts, ssrc=ssrc, payload=data)
            sock.sendto(rtp_pkt.to_bytes(), (target_ip, target_port))
            
            
            if seq % 100 == 0:
                from File_Transfer_Functions.RTCP import send_rtcp_report
                send_rtcp_report(sock, target_ip, target_port, ssrc, ts, seq, seq * CHUNKS)

            seq = (seq + 1) % 65536
            ts += CHUNKS
        except Exception as e:
            print(f"\n[ERROR] Mic Stream: {e}")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()
    print("[AUDIO] Microphone closed.")



def receive_thread(sock, local_ip, local_port, sender_obj):
    """Handles SIP Signaling and Incoming RTP Playback """
    global is_connected, is_listening, is_calling, current_packet, bye_received
    
    p_out = pyaudio.PyAudio()
    out_stream = p_out.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)

    while is_listening:
        try:
            data, addr = sock.recvfrom(4096)
            
            
            if data.startswith(b"INVITE") or data.startswith(b"SIP") or data.startswith(b"ACK") or data.startswith(b"BYE"):
                packet = SIP_packet.from_bytes(data)
                receiver = Recv_func(receiver_ip=local_ip, receiver_port=local_port, socket=sock, sender_ip=addr[0], sender_port=addr[1])

                if packet.start_line.startswith("INVITE"):
                    
                    if is_calling and local_ip > addr[0]:
                        continue 
                    
                    print(f"\n[SIP] Received INVITE from {addr}. Auto-responding with 200 OK...")
                    receiver.recv_invite(packet)
                    bye_received = False 
                    is_connected = True 
                    is_calling = False
                    current_packet = packet

                elif packet.start_line.startswith("BYE"):
                    print(f"\n[SIP] Received BYE from {addr}. Call ended.") 
                    receiver.recv_bye(packet)
                    is_connected = False 
                    bye_received = True
                    current_packet = packet
                    
                elif packet.start_line.startswith("ACK"):
                    print(f"\n[SIP] Received ACK. Media session active.") 
                    is_connected = True
                    current_packet = packet

                elif packet.start_line.startswith("SIP/2.0 200 OK"):
                    print(f"\n[SIP] Received 200 OK. Sending ACK...") 
                    sender_obj.send_ack(packet)
                    is_connected = True
                    is_calling = False
                    current_packet = packet 

            else:
                try:
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



sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.bind((DEVICE1_IP, DEVICE1_PORT))
sock.settimeout(1.0)

sender = Send_func(sender_ip=DEVICE1_IP, sender_port=DEVICE1_PORT, 
                   receiver_ip=DEVICE2_IP, receiver_port=DEVICE2_PORT, socket=sock)


rx_thread = threading.Thread(target=receive_thread, args=(sock, DEVICE1_IP, DEVICE1_PORT, sender), daemon=True)
rx_thread.start()

print(f"Two-Way SIP Client Active on {DEVICE1_IP}:{DEVICE1_PORT}")

try:
    while is_listening:
        if not is_connected:
            cmd = input("\n[IDLE] 'I' to Invite, 'Q' to Quit: ").upper()
            if cmd == 'I':
                bye_received = False
                is_calling = True
                sender.send_invite() 
            elif cmd == 'Q':
                is_listening = False
        else:

            audio_thread = threading.Thread(target=rtp_send_thread, args=(sock, DEVICE2_IP, DEVICE2_PORT))
            audio_thread.start()
            
            cmd = input("\n[IN-CALL] 'B' to Disconnect: ").upper()
            if cmd == 'B':
                is_connected = False
                sender.send_bye(current_packet) 
                time.sleep(1) 

except KeyboardInterrupt:
    is_listening = False

sock.close()
print("\nProgram Terminated. ")