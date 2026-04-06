from Packets.RTCP_packet import RTCPSenderReport

# Function to send an RTCP Sender Report
def send_rtcp_report(sock, receiver_ip, receiver_port, ssrc, timestamp, packet_count, octet_count):
    # RTCP usually goes to (RTP Port + 1)
    rtcp_port = receiver_port + 1
    
    # Creates the RTCP Sender Report
    report = RTCPSenderReport(
        ssrc=ssrc,
        rtp_timestamp=timestamp,
        packet_count=packet_count,
        octet_count=octet_count
    )
    
    # Sends the RTCP Sender Report to the receiver
    try:
        sock.sendto(report.to_bytes(), (receiver_ip, rtcp_port))
        # print(f"RTCP Sender Report sent to {receiver_ip}:{rtcp_port}")
    except Exception as e:
        print(f"RTCP Error: {e}")