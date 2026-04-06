import time
import struct

# Class for RTCP Sender Report Packet
class RTCPSenderReport:
    # Initializes the class
    def __init__(self, ssrc, rtp_timestamp, packet_count, octet_count):
        self.version = 2
        self.padding = 0
        self.rc = 0         
        self.pt = 200       
        
        self.ssrc = ssrc
        self.rtp_timestamp = rtp_timestamp
        self.packet_count = packet_count
        self.octet_count = octet_count

    # Converts the packet into bytes for sending
    def to_bytes(self):
        byte1 = (self.version << 6) | (self.padding << 5) | self.rc
        length = 6 

        ntp_sec = int(time.time()) + 2208988800 
        ntp_frac = 0 

        return struct.pack('!BBHIIIIII', byte1, self.pt, length, self.ssrc, 
                           ntp_sec, ntp_frac, self.rtp_timestamp, 
                           self.packet_count, self.octet_count)
    
    # Converts the bytes into a packet object after receiving
    @classmethod
    def from_bytes(cls, packet_bytes):
        header_and_stats = packet_bytes[:28]
        
        byte1, pt, length, ssrc, ntp_sec, ntp_frac, rtp_timestamp, packet_count, octet_count = struct.unpack('!BBHIIIIII', header_and_stats)
        
        return cls(ssrc, rtp_timestamp, packet_count, octet_count)