from Connection_Functions.SIP import SIP
from Packets.SDP_packet import SDP_packet

def send_invite(sender_ip, sender_port, receiver_ip, receiver_port, socket):

    try:
        sip = SIP()

        #following protocol
        sdp = SDP_packet(origin=f"- 676767 676767 IN IP {sender_ip}", connection_data=f"IN IP {sender_ip}", 
                        #Depends on type of encoder (codec payload type 0 for media)  attribute clarifies payload type
                        media=f"audio {sender_port} RTP/AVP 0", attribute="rtpmap:0 PCMU/8000").to_string()
        
        start_line = sip.make_start_line_send("INVITE", receiver_ip)

        sip.make_packet(start_line=start_line, 
                        via=f"SIP/2.0/UDP {sender_ip}:{sender_port}", 
                        to=f"sip:{receiver_ip}", 
                        _from=f"sip:{sender_ip}", 
                        call_id="WEWANT4.0", 
                        cseq="1 INVITE",
                        content_type="application/sdp",
                        content_length=len(sdp),
                        body=sdp)
        
        sip_string = sip.to_bytes()

        socket.sendto(sip_string, (receiver_ip, receiver_port))

        print(f"INVITE successfully sent to {receiver_ip}:{receiver_port}")

        return True
    except Exception as e:
        print(f"Error sending INVITE: {e}")
        return False
    
def send_ack(sender_ip, sender_port, receiver_ip, receiver_port, socket, packet):

    try:
        sip = SIP()
        
        start_line = sip.make_start_line_send("ACK", receiver_ip)

        sip.make_packet(start_line=start_line, 
                        via=f"SIP/2.0/UDP {sender_ip}:{sender_port}", 
                        to=f"sip:{receiver_ip}", 
                        _from=f"sip:{sender_ip}", 
                        call_id=packet.call_id,
                        cseq="1 ACK",
                        content_type=None,
                        content_length=0,
                        body="")
        
        sip_string = sip.to_bytes()

        socket.sendto(sip_string, (receiver_ip, receiver_port))

        print(f"ACK successfully sent to {receiver_ip}:{receiver_port}")

        return True
    except Exception as e:
        print(f"Error sending ACK: {e}")
        return False

def send_bye(sender_ip, sender_port, receiver_ip, receiver_port, socket, packet):

    try:
        sip = SIP()
        
        start_line = sip.make_start_line_send("BYE", receiver_ip)

        sip.make_packet(start_line=start_line, 
                        via=f"SIP/2.0/UDP {sender_ip}:{sender_port}", 
                        to=f"sip:{receiver_ip}", 
                        _from=f"sip:{sender_ip}", 
                        call_id=packet.call_id,
                        cseq="2 BYE",
                        content_type=None,
                        content_length=0,
                        body="")
        
        sip_string = sip.to_bytes()

        socket.sendto(sip_string, (receiver_ip, receiver_port))

        print(f"BYE successfully sent to {receiver_ip}:{receiver_port}")

        return True
    except Exception as e:
        print(f"Error sending BYE: {e}")
        return False