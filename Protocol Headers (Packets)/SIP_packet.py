#packet class for SIP
class SIP_packet:
    def __init__(self, start_line, via, to, _from, call_id, cseq, content_type=None, content_length=0, body=""):
        self.start_line = start_line
        self.via = via
        self.to = to
        self._from = _from 
        self.call_id = call_id
        self.cseq = cseq
        self.max_forwards = 70
        
        self.content_type = content_type
        self.content_length = content_length
        self.body = body

    # Builds formatted SIP string for the packet to be sent.
    def to_bytes(self):
        """Builds the strictly formatted SIP string and encodes it for the socket."""
        
        sip_str = f"{self.start_line}\r\n"
        
        sip_str += f"Via: {self.via}\r\n"
        sip_str += f"To: {self.to}\r\n"
        sip_str += f"From: {self._from}\r\n"
        sip_str += f"Call-ID: {self.call_id}\r\n"
        sip_str += f"CSeq: {self.cseq}\r\n"
        sip_str += f"Max-Forwards: {self.max_forwards}\r\n"
        
        # Add the headers of SDP
        if self.content_type and self.content_length > 0:
            sip_str += f"Content-Type: {self.content_type}\r\n"
            sip_str += f"Content-Length: {self.content_length}\r\n"
        
        sip_str += "\r\n"
        
        # Adds the SDP packet
        sip_str += self.body
        
        return sip_str.encode('utf-8')
