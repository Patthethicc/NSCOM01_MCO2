
def media_sender_thread(target_ip, rtp_port):
    """
    The 'Discord' Model: Always captures mic, but only sends 
    packets if you are loud enough and the call is connected.
    """
    global is_connected
    # Initialize PyAudio here...
    
    while is_listening:
        if is_connected:
            # 1. Capture Mic Chunk
            # 2. Calculate RMS Volume
            # 3. IF volume > THRESHOLD:
            #    -> Wrap chunk in RTP_packet
            #    -> socket.sendto(rtp_bytes, (target_ip, rtp_port))
            pass
        else:
            # Call is not active; sleep briefly to save CPU
            time.sleep(0.1)