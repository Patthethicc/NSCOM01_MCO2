from Connection_Functions.SIP import SIP
from Packets.SDP_packet import SDP_packet

def recv_invite(receiver_ip, receiver_port, packet, socket, sender_ip, sender_port):
    try:
        sip = SIP()

        sdp = SDP_packet(origin=f"- 696969 696969 IN IP {receiver_ip}", connection_data=f"IN IP {receiver_ip}", 
            media=f"audio {receiver_port} RTP/AVP 0", attribute="rtpmap:0 PCMU/8000").to_string()
        
        start_line = sip.make_start_line_receive("200", "OK")

        sip.make_packet(start_line=start_line, 
            via=packet.via,         
            to=packet.to,           
            _from=packet._from,     
            call_id=packet.call_id,
            cseq=packet.cseq,
            content_type="application/sdp",
            content_length=len(sdp),
            body=sdp)
        
        sip_string = sip.to_bytes()

        socket.sendto(sip_string, (sender_ip, sender_port))

        print(f"200 OK (Accept) sent to {sender_ip}. Waiting for ACK...")
        return True

    except Exception as e:
        print(f"Error sending 200 OK for INVITE: {e}")
        return False
    
def recv_bye(packet, socket, sender_ip, sender_port):
    try:
        sip = SIP()

        start_line = sip.make_start_line_receive("200", "OK")

        sip.make_packet(start_line=start_line, 
            via=packet.via,         
            to=packet.to,           
            _from=packet._from,     
            call_id=packet.call_id,
            cseq=packet.cseq,
            content_type=None,
            content_length=0,
            body="")
        
        sip_string = sip.to_bytes()

        socket.sendto(sip_string, (sender_ip, sender_port))

        print(f"200 OK (Accept) sent to {sender_ip} for BYE.")
        return True

    except Exception as e:
        print(f"Error sending 200 OK for BYE: {e}")
        return False
    
def send_error(error_code, error_reason,packet, sender_ip, sender_port, socket):
    try:
        sip = SIP()
        
        start_line = sip.make_start_line_receive(error_code, error_reason)

        sip.make_packet(
            start_line=start_line, 
            via=packet.via,         
            to=packet.to,           
            _from=packet._from,     
            call_id=packet.call_id, 
            cseq=packet.cseq,       
            content_type=None,
            content_length=0,
            body=""
        )
        
        sip_string = sip.to_bytes()

        socket.sendto(sip_string, (sender_ip, sender_port))

        print(f"Error {start_line} sent to {sender_ip}.")
        return True
        
    except Exception as e:
        print(f"Failed to send error: {e}")
        return False