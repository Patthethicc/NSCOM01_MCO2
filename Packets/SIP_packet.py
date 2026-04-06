# Class for SIP Packet
class SIP_packet:
    # Initializes the class
    def __init__(self, start_line, via, to, _from, call_id, cseq, content_type=None, content_length=0, body=""):
        self.start_line = start_line
        self.via = via
        self.to = to
        self._from = _from 
        self.call_id = call_id
        self.cseq = cseq
        self.max_forwards = 70
        
        self.content_type = content_type
        self.content_length = int(content_length)
        self.body = body
    
    # Creates a start line string for sending packets, based on the method and receiver IP
    @staticmethod
    def make_start_line_send(method, ip_add):
        return f"{method} sip:{ip_add} SIP/2.0"
    
    # Creates a start line string for receiving packets, based on the status code and reason
    @staticmethod
    def make_start_line_receive(status_code, reason):
        return f"SIP/2.0 {status_code} {reason}"
    
    # Converts the packet into bytes for sending
    def to_bytes(self):
        
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
    
    # Converts the bytes into a packet object after receiving
    @classmethod
    def from_bytes(cls, packet_bytes):
        
        sip_string = packet_bytes.decode('utf-8')

        parts = sip_string.split('\r\n\r\n', 1)
        headers_block = parts[0]
        
        body = parts[1] if len(parts) > 1 else ""

        lines = headers_block.split('\r\n')

        start_line = lines[0]

        parsed_headers = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1) 
                parsed_headers[key.strip()] = value.strip() 

        via = parsed_headers.get("Via", "")
        to = parsed_headers.get("To", "")
        _from = parsed_headers.get("From", "")
        call_id = parsed_headers.get("Call-ID", "")
        cseq = parsed_headers.get("CSeq", "")
        content_type = parsed_headers.get("Content-Type")
        
        content_length = parsed_headers.get("Content-Length", 0) 

        return cls(start_line, via, to, _from, call_id, cseq, content_type, content_length, body)
