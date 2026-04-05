from Packets.SIP_packet import SIP_packet
from Packets.RTP_packet import RTPPacket
from Connection_Functions.Receive import Recv_func

def receive_thread(socket, DEVICE1_IP, DEVICE1_PORT):
    global is_connected, is_listening, received_audio_payloads
    
    print("[Listener] Waiting for incoming packets in the background...")
    
    while is_listening:
        try:
            data, addr = socket.recvfrom(4096)
            
            if data.startswith(b"INVITE") or data.startswith(b"SIP") or data.startswith(b"ACK") or data.startswith(b"BYE"):
                packet = SIP_packet.from_bytes(data)
                receiver = Recv_func(receiver_ip=DEVICE1_IP, receiver_port=DEVICE1_PORT, socket=socket, sender_ip=addr[0], sender_port=addr[1])

                if packet.start_line.startswith("INVITE"):
                    receiver.recv_invite(packet)
                    is_connected = True # Update the state!

                elif packet.start_line.startswith("BYE"):
                    receiver.recv_bye(packet)
                    is_connected = False # Update the state!
                    
                elif packet.start_line.startswith("ACK"):
                    is_connected = True

            else:
                # IT'S RTP DATA! 
                # Keep your exact logic for appending to received_audio_payloads
                # place rtp receive logic here pookibear
                rtp_pkt = RTPPacket.from_bytes(data)
                received_audio_payloads.append(rtp_pkt.payload)
                
        except socket.timeout:
            continue