from Packets.SDP_packet import SDP_packet
from Packets.SIP_packet import SIP_packet

# Class for receiving functions
class Recv_func:
    # Initializes the class
    def __init__(self, receiver_ip, receiver_port, socket, sender_ip, sender_port):
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.socket = socket
        self.sender_ip = sender_ip
        self.sender_port = sender_port

    # For receiving an INVITE packet and sending a 200 OK response
    def recv_invite(self, packet):
        try:
            # Creates an SDP packet object
            sdp = SDP_packet(origin=f"- 696969 696969 IN IP {self.receiver_ip}", connection_data=f"IN IP {self.receiver_ip}", 
                media=f"audio {self.receiver_port} RTP/AVP 0", attribute="rtpmap:0 PCMU/8000").to_string()
            
            # Creates a start line for the 200 OK packet
            start_line = SIP_packet.make_start_line_receive("200", "OK")

            # Creates a SIP packet object for the 200 OK
            sip = SIP_packet(start_line=start_line, 
                via=packet.via,         
                to=packet.to,           
                _from=packet._from,     
                call_id=packet.call_id,
                cseq=packet.cseq,
                content_type="application/sdp",
                content_length=len(sdp),
                body=sdp)
            
            sip_string = sip.to_bytes()

            # Sends the 200 OK packet to the receiver
            self.socket.sendto(sip_string, (self.sender_ip, self.sender_port))

            print(f"200 OK (Accept) sent to {self.sender_ip}. Waiting for ACK...")
            return True

        except Exception as e:
            print(f"Error sending 200 OK for INVITE: {e}")
            return False
    
    # For receiving a BYE packet and sending a 200 OK response
    def recv_bye(self, packet):
        try:
            # Creates a start line for the 200 OK packet
            start_line = SIP_packet.make_start_line_receive("200", "OK")

            # Creates a SIP packet object for the 200 OK
            sip = SIP_packet(start_line=start_line, 
                via=packet.via,         
                to=packet.to,           
                _from=packet._from,     
                call_id=packet.call_id,
                cseq=packet.cseq,
                content_type=None,
                content_length=0,
                body="")
            
            sip_string = sip.to_bytes()

            # Sends the 200 OK packet to the receiver
            self.socket.sendto(sip_string, (self.sender_ip, self.sender_port))

            print(f"200 OK (Accept) sent to {self.sender_ip} for BYE.")
            return True

        except Exception as e:
            print(f"Error sending 200 OK for BYE: {e}")
            return False
        
    # For sending an error response for any unexpected packets
    def send_error(self, error_code, error_reason, packet):
        try:
            # Creates a start line for the error packet
            start_line = SIP_packet.make_start_line_receive(error_code, error_reason)

            # Creates a SIP packet object for the error
            sip = SIP_packet(start_line=start_line, 
                via=packet.via,         
                to=packet.to,           
                _from=packet._from,     
                call_id=packet.call_id, 
                cseq=packet.cseq,       
                content_type=None,
                content_length=0,
                body="")
            
            sip_string = sip.to_bytes()

            # Sends the error packet to the receiver
            self.socket.sendto(sip_string, (self.sender_ip, self.sender_port))

            print(f"Error {start_line} sent to {self.sender_ip}.")
            return True
            
        except Exception as e:
            print(f"Failed to send error: {e}")
            return False