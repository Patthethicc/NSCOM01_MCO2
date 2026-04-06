# Class for SDP Packet
class SDP_packet:
    # Initializes the class
    def __init__(self, origin, connection_data, media, attribute):
        self.version = 0
        self.origin = origin
        self.session_name = "-" 
        self.connection_data = connection_data
        self.time = "0 0"
        self.media = media
        self.attribute = attribute

    # Converts to string for the SIP packet
    def to_string(self):
        sdp_str = f"v={self.version}\r\n"
        sdp_str += f"o={self.origin}\r\n"
        sdp_str += f"s={self.session_name}\r\n"
        sdp_str += f"c={self.connection_data}\r\n"
        sdp_str += f"t={self.time}\r\n"
        sdp_str += f"m={self.media}\r\n"
        sdp_str += f"a={self.attribute}\r\n"
        
        return sdp_str
