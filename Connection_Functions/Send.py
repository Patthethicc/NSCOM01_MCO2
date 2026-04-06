from Packets.SDP_packet import SDP_packet
from Packets.SIP_packet import SIP_packet

# Class for sending functions
class Send_func:
    # Initializes the class
    def __init__(self, sender_ip, sender_port, receiver_ip, receiver_port, socket):
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.socket = socket

    # For sending an INVITE packet to the receiver
    def send_invite(self):
        try:
            # Creates an SDP packet object
            sdp = SDP_packet(origin=f"- 676767 676767 IN IP {self.sender_ip}", connection_data=f"IN IP {self.sender_ip}", 
                            media=f"audio {self.sender_port} RTP/AVP 0", attribute="rtpmap:0 PCMU/8000").to_string()
            
            # Creates a start line for the INVITE packet
            start_line = SIP_packet.make_start_line_send("INVITE", self.receiver_ip)

            # Creates a SIP packet object for the INVITE
            sip = SIP_packet(start_line=start_line, 
                            via=f"SIP/2.0/UDP {self.sender_ip}:{self.sender_port}", 
                            to=f"sip:{self.receiver_ip}", 
                            _from=f"sip:{self.sender_ip}", 
                            call_id="WEWANT4.0", 
                            cseq="1 INVITE",
                            content_type="application/sdp",
                            content_length=len(sdp),
                            body=sdp)
            
            sip_string = sip.to_bytes()

            # Sends the INVITE packet to the receiver
            self.socket.sendto(sip_string, (self.receiver_ip, self.receiver_port))

            print(f"INVITE successfully sent to {self.receiver_ip}:{self.receiver_port}")

            return True
        except Exception as e:
            print(f"Error sending INVITE: {e}")
            return False
    
    # For sending an ACK packet to the receiver
    def send_ack(self, packet):
        try:
            # Creates a start line for the ACK packet
            start_line = SIP_packet.make_start_line_send("ACK", self.receiver_ip)

            # Creates a SIP packet object for the ACK
            sip = SIP_packet(start_line=start_line, 
                            via=f"SIP/2.0/UDP {self.sender_ip}:{self.sender_port}", 
                            to=f"sip:{self.receiver_ip}", 
                            _from=f"sip:{self.sender_ip}", 
                            call_id=packet.call_id,
                            cseq="1 ACK",
                            content_type=None,
                            content_length=0,
                            body="")
            
            sip_string = sip.to_bytes()

            # Sends the ACK packet to the receiver
            self.socket.sendto(sip_string, (self.receiver_ip, self.receiver_port))

            print(f"ACK successfully sent to {self.receiver_ip}:{self.receiver_port}")

            return True
        except Exception as e:
            print(f"Error sending ACK: {e}")
            return False

    # For sending a BYE packet to the receiver
    def send_bye(self, packet):
        try:
            # Creates a start line for the BYE packet
            start_line = SIP_packet.make_start_line_send("BYE", self.receiver_ip)

            # Creates a SIP packet object for the BYE
            sip = SIP_packet(start_line=start_line, 
                            via=f"SIP/2.0/UDP {self.sender_ip}:{self.sender_port}", 
                            to=f"sip:{self.receiver_ip}", 
                            _from=f"sip:{self.sender_ip}", 
                            call_id=packet.call_id,
                            cseq="2 BYE",
                            content_type=None,
                            content_length=0,
                            body="")
            
            sip_string = sip.to_bytes()

            # Sends the BYE packet to the receiver
            self.socket.sendto(sip_string, (self.receiver_ip, self.receiver_port))

            print(f"\nBYE successfully sent to {self.receiver_ip}:{self.receiver_port}")

            return True
        except Exception as e:
            print(f"\nError sending BYE: {e}")
            return False