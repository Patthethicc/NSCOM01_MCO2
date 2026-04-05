import socket
import threading
import time
import os
import pyaudio
import audioop

#IP Configuration
DEVICE1_IP = os.getenv("SENDER_IP")
DEVICE1_PORT = int(os.getenv("SENDER_PORT"))
DEVICE2_IP = os.getenv("RECEIVER_IP")
DEVICE2_PORT = int(os.getenv("RECEIVER_PORT"))

#Microphone Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
VOICE_THRESHOLD = 800
in_call = False

def background_listener(shared_socket):
    print("Listening for incoming packets...")
    while True:
        try:
            data, addr = shared_socket.recvfrom(4096)
        except socket.timeout:
            continue # Just loop back and keep listening
        except Exception as e:
            # If the socket closes, the thread exits
            break

def mic_watcher(sip_sender):
    global in_call
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    print("Microphone is hot. Waiting for you to speak...")
    
    while True:
        if not in_call:
            # 1. Grab a tiny slice of audio (about 0.02 seconds)
            data = stream.read(CHUNK)
            
            # 2. Calculate how loud that slice is
            rms_volume = audioop.rms(data, 2) 
            
            # 3. If the volume spikes above the threshold, trigger the call!
            if rms_volume > VOICE_THRESHOLD:
                print(f"\n[VOX DETECTED] Volume spiked to {rms_volume}!")
                print(f">>> Auto-sending INVITE to {target_ip}... >>>")
                
                # Fire your SIP function
                sip_sender.send_invite(target_ip)
                
                # Lock the state so we don't spam 500 INVITEs per second
                in_call = True 
                
        else:
            # If we are already in a call, we don't need to trigger an INVITE.
            # We just sleep for a bit to let Jeru's RTP threads handle the actual speaking.
            time.sleep(0.1)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((DEVICE1_IP, DEVICE1_PORT))
sock.settimeout(2.0)

listener_thread = threading.Thread(target=background_listener, args=(sock,), daemon=True)
listener_thread.start()

vox_thread = threading.Thread(target=mic_watcher, args=(sender_object,), daemon=True)
vox_thread.start()