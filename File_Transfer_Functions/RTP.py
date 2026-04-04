import time
import wave
from Packets.RTP_packet import RTPPacket

def send_audio_file(filename, sender_ip, sender_port, receiver_ip, receiver_port, sock, ssrc=12345):
    """
    Reads a .wav file and sends it as a stream of RTP packets.
    """
    try:
        with wave.open(filename, 'rb') as wav:
            # SIP typically uses 20ms chunks for audio
            # G.711 (PCMU) at 8000Hz = 160 samples per 20ms
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            framerate = wav.getframerate()
            
            # Simplified: Read 160 frames at a time
            chunk_size = 160 
            sequence_number = 0
            timestamp = 0
            
            print(f"Starting RTP stream: {filename} to {receiver_ip}:{receiver_port}")
            
            while True:
                data = wav.readframes(chunk_size)
                if not data:
                    break
                
                # Create the RTP Packet
                # Payload Type 0 is usually PCMU (G.711)
                rtp_pkt = RTPPacket(
                    payload_type=0, 
                    sequence_number=sequence_number,
                    timestamp=timestamp,
                    ssrc=ssrc,
                    payload=data
                )
                
                # Send via the existing socket
                sock.sendto(rtp_pkt.to_bytes(), (receiver_ip, receiver_port))
                
                # Update headers
                sequence_number = (sequence_number + 1) % 65536
                timestamp += chunk_size
                
                # Real-time pacing: 20ms delay
                time.sleep(0.02)
                
            print("Audio stream finished.")
            return sequence_number, timestamp
            
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    except Exception as e:
        print(f"RTP Error: {e}") 