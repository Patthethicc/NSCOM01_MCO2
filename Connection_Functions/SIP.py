from Packets import SIP_packet

#Class for SIP connection functions
class SIP:

    def __init__(self):
        self.packet = None

    def make_start_line_send(method, ip_add):
        return f"{method} sip:{ip_add} SIP/2.0"
    
    def make_start_line_receive(status_code, reason):
        return f"SIP/2.0 {status_code} {reason}"

    def make_packet(self, start_line, via, to, _from, call_id, cseq, content_type=None, content_length=0, body=""):
        self.packet = SIP_packet(start_line, via, to, _from, call_id, cseq, content_type, content_length, body)

    def to_bytes(self):
        return self.packet.to_bytes()
    
    def from_bytes(self, data):
        return SIP_packet.from_bytes(data)

    #def check_packet(self, packet):
