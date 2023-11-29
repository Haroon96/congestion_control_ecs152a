import random
import socket

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE
EXPECTED_SEQ_ID = 0
RECEIVED_DATA = {}

def create_acknowledgement(seq_id):
    return int.to_bytes(seq_id, SEQ_ID_SIZE, signed=True, byteorder='big') + b'ack'

# create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
    # bind the socket to a OS port
    # bind to 0.0.0.0 so external 
    udp_socket.bind(("0.0.0.0", 5001))

    print("Receiver running")
    # start receiving packets
    while True:
        timeouts = 0
        try:
            # receive the packet
            packet, client = udp_socket.recvfrom(PACKET_SIZE)
            
            if random.random() < 0.1:
                continue

            # get the message id
            seq_id, message = packet[:SEQ_ID_SIZE], packet[SEQ_ID_SIZE:]
            
            # if the message id is -1, we have received all the packets
            seq_id = int.from_bytes(seq_id, signed=True, byteorder='big')
            
            print('received', seq_id)
            
            # keep track of received sequences
            RECEIVED_DATA[seq_id] = message
            
            # check if sequence id is same as expected and move forward
            if seq_id <= EXPECTED_SEQ_ID and len(RECEIVED_DATA[seq_id]) > 0:
                while EXPECTED_SEQ_ID in RECEIVED_DATA:
                    EXPECTED_SEQ_ID += len(RECEIVED_DATA[seq_id])
            
            # create ack id
            ack_id = EXPECTED_SEQ_ID
            
            
            print('sending', ack_id)
            
            # create the acknowledgement
            acknowledgement = create_acknowledgement(ack_id)

            # send the acknowledgement
            udp_socket.sendto(acknowledgement, client)
            
            # check if all data received (empty message)
            if len(message) == 0 and ack_id == seq_id:
                break
        except socket.timeout:
            timeouts += 1

with open('recv.txt', 'wb') as f:
    for sid in sorted(RECEIVED_DATA.keys()):
        f.write(RECEIVED_DATA[sid])