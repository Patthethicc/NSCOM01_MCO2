from Packets.RTCP_packet import RTCPSenderReport

def send_rtcp_report(sock, receiver_ip, receiver_port, ssrc, timestamp, packet_count, octet_count):
    """
    Sends a single RTCP Sender Report to the receiver.
    """
    # RTCP usually goes to (RTP Port + 1)
    rtcp_port = receiver_port + 1
    
    report = RTCPSenderReport(
        ssrc=ssrc,
        rtp_timestamp=timestamp,
        packet_count=packet_count,
        octet_count=octet_count
    )
    
    try:
        sock.sendto(report.to_bytes(), (receiver_ip, rtcp_port))
        # print(f"RTCP Sender Report sent to {receiver_ip}:{rtcp_port}")
    except Exception as e:
        print(f"RTCP Error: {e}")