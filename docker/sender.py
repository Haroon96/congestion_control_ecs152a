import socket

# total packet size
PACKET_SIZE = 1024
# bytes reserved for sequence id
SEQ_ID_SIZE = 4
# bytes available for message
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE
# total packets to send
WINDOW_SIZE = 5
ACKS = {}

# read data
with open('file.mp3', 'rb') as f:
    data = f.read()
 
# create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:

    # bind the socket to a OS port
    udp_socket.bind(("localhost", 5000))
    udp_socket.settimeout(1)
    
    # start sending data from 0th sequence
    seq_id = 0
    while seq_id < len(data):
        
        # create messages
        messages = []
        acks = {}
        seq_id_tmp = seq_id
        for i in range(WINDOW_SIZE):
            # construct messages
            # sequence id of length SEQ_ID_SIZE + message of remaining PACKET_SIZE - SEQ_ID_SIZE bytes
            message_data = data[seq_id_tmp : seq_id_tmp + MESSAGE_SIZE]
            message = int.to_bytes(seq_id_tmp, SEQ_ID_SIZE, byteorder='big', signed=True) + message_data
            messages.append((seq_id_tmp, message))
            # check if not last message
            if len(message_data) == 0:
                break
            # create ack
            acks[seq_id_tmp] = False
            # move seq_id tmp pointer ahead
            seq_id_tmp += len(message_data)

        # send messages
        for sid, message in messages:
            print('sending', sid)
            udp_socket.sendto(message, ('localhost', 5001))
        
        # wait for acknowledgement
        while True:
            try:
                # wait for ack
                ack, _ = udp_socket.recvfrom(PACKET_SIZE)
                
                # extract ack id
                ack_id = int.from_bytes(ack[:SEQ_ID_SIZE], byteorder='big')
                
                # update acks below cumulative ack
                for _id in acks:
                    if _id < ack_id:
                        acks[_id] = True
                        
                ACKS[ack_id] = ACKS.get(ack_id, 0) + 1
                
                # all acks received, move on
                if all(acks.values()):
                    break
            except socket.timeout:
                # no ack received, resend unacked messages
                for sid, message in messages:
                    if not acks[sid]:
                        print('sending', sid)
                        udp_socket.sendto(message, ('localhost', 5001))
                
        # move sequence id forward
        seq_id = seq_id_tmp
        
    # send final closing message
    print('here')
    udp_socket.sendto(int.to_bytes(seq_id, 4, signed=True, byteorder='big'), ('localhost', 5001))
    
    
print(ACKS)