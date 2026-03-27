# NSCOM01_MCO2
Real time communication

# Pat
- SIP HANDSHAKE
  - Sends INVITE
  - Processes 200 OK
  - Sends ACK 
- SDP Negotiation
  - Correctly embeds SDP in INVITE
  - Parses SDP from 200 OK to obtain remote IP/port and codec info
- RTP Packet Generation
  - Builds valid RTP headers (sequence, timestamp, SSRC).
  - Sends audio frames from a file in a timely manner.

# Joruel
- RTP Receiving & Playback
  - Accurately receives incoming RTP packets.
  - Plays the audio (or outputs it properly). 
- RTCP Usage
  - Periodically sends RTCP (e.g., Sender Reports) and optionally processes Receiver Reports (stats, etc.).  
- Call Teardown
  - Uses a BYE message to gracefully end the call. Closes sockets and frees resources.
