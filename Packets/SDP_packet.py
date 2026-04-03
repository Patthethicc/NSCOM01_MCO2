#packet class for SDP
class SDP_packet:
    def __init__(self, origin, connection_data, media, attribute):
        self.version = 0
        self.origin = origin
        self.session_name = "" 
        self.connection_data = connection_data
        self.time = "0 0"
        self.media = media
        self.attribute = attribute
