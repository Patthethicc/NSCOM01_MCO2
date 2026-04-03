import time
import struct

class RTCPSenderReport:
    def __init__(self, ssrc, rtp_timestamp, packet_count, octet_count):
        self.version = 2
        self.padding = 0
        self.rc = 0         
        self.pt = 200       
        
        self.ssrc = ssrc
        self.rtp_timestamp = rtp_timestamp
        self.packet_count = packet_count
        self.octet_count = octet_count

    def to_bytes(self):
        #turn into binary bytes for sending
        byte1 = (self.version << 6) | (self.padding << 5) | self.rc
        length = 6 

        ntp_sec = int(time.time()) + 2208988800 
        ntp_frac = 0 

        return struct.pack('!BBHIIIIII', byte1, self.pt, length, self.ssrc, 
                           ntp_sec, ntp_frac, self.rtp_timestamp, 
                           self.packet_count, self.octet_count)

    @classmethod
    def from_bytes(cls, packet_bytes):
        #turn binary into object after sending
        # A standard Sender Report with 0 report blocks is exactly 28 bytes
        header_and_stats = packet_bytes[:28]
        
        # Unpack all 9 fields
        byte1, pt, length, ssrc, ntp_sec, ntp_frac, rtp_timestamp, packet_count, octet_count = struct.unpack('!BBHIIIIII', header_and_stats)
        
        # Return a newly constructed RTCPSenderReport object!
        return cls(ssrc, rtp_timestamp, packet_count, octet_count)