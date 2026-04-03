# Listen on SIP port -> Receive INVITE (PAT)

    #place code here

# Send 200 OK with Receiver's SDP rules attached (PAT)

    #place code here

# Wait for ACK from Sender (PAT)

    #place code here

# Initialize RTP port -> Loop to receive packets, strip headers, and play audio or store then play audio (JERU)

    #place code here

# Receive BYE on SIP port from Sender (PAT) 

    #place code here

# Send final 200 OK -> Close application (PAT)

    #place code here