import struct

# Class for RTP Packet
class RTPPacket:
    # Initializes the class
    def __init__(self, payload_type, sequence_number, timestamp, ssrc, payload):
        self.version = 2
        self.padding = 0
        self.extension = 0
        self.cc = 0
        self.marker = 0
        
        self.payload_type = payload_type
        self.sequence_number = sequence_number
        self.timestamp = timestamp
        self.ssrc = ssrc
        self.payload = payload

    # Converts the packet into bytes for sending
    def to_bytes(self):
        #turn into binary bytes for sending
        byte1 = (self.version << 6) | (self.padding << 5) | (self.extension << 4) | self.cc
        byte2 = (self.marker << 7) | self.payload_type
        header = struct.pack('!BBHII', byte1, byte2, self.sequence_number, self.timestamp, self.ssrc)
        return header + self.payload

    # Converts the bytes into a packet object after receiving
    @classmethod
    def from_bytes(cls, packet_bytes):
        #turn binary into object after sending
        # 1. Split the 12-byte header from the audio payload
        header = packet_bytes[:12]
        payload = packet_bytes[12:]
        
        # 2. Unpack the header integers
        byte1, byte2, seq_num, timestamp, ssrc = struct.unpack('!BBHII', header)
        
        # 3. Use Bitwise AND to extract the 7-bit Payload Type from byte 2
        # (0x7F in hex is 01111111 in binary, which masks out the Marker bit)
        payload_type = byte2 & 0x7F 
        
        # 4. Return a newly constructed RTPPacket object!
        return cls(payload_type, seq_num, timestamp, ssrc, payload)