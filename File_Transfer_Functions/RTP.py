import time
import wave
import audioop # Built-in Python library for basic audio manipulation
from Packets.RTP_packet import RTPPacket

# Function to send an audio file as RTP packets
def send_audio_file(filename, sender_ip, sender_port, receiver_ip, receiver_port, sock, ssrc=12345):
    filename = filename.strip('"').strip("'")
    target_rate = 8000 # The rate your Receiver_Main is expecting

    try:
        # Opens the .wav file and resamples it to the target rate
        with wave.open(filename, 'rb') as wav:
            original_rate = wav.getframerate()
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            
            print(f"\nOriginal Rate: {original_rate}Hz | Target Rate: {target_rate}Hz")
            
   
            raw_data = wav.readframes(wav.getnframes())

 
            if n_channels > 1:
                raw_data = audioop.tomono(raw_data, sample_width, 0.5, 0.5)


            
            resampled_data, _ = audioop.ratecv(raw_data, sample_width, 1, original_rate, target_rate, None)

            print(f"DEBUG: Resampled data length: {len(resampled_data)} bytes")
            
            # Configures RTP packet parameters
            chunk_size = 320 
            sequence_number = 0
            timestamp = 0

            # Send RTP packets in chunks
            for i in range(0, len(resampled_data), chunk_size):
                data_chunk = resampled_data[i:i + chunk_size]
                
                
                if len(data_chunk) < chunk_size:
                    data_chunk = data_chunk.ljust(chunk_size, b'\x00')

                rtp_pkt = RTPPacket(0, sequence_number, timestamp, ssrc, data_chunk)
                sock.sendto(rtp_pkt.to_bytes(), (receiver_ip, receiver_port))
                
                sequence_number = (sequence_number + 1) % 65536
                timestamp += 160
                time.sleep(0.02)

            return sequence_number, timestamp

    except Exception as e:
        print(f"RTP Resampling Error: {e}")
        return 0, 0