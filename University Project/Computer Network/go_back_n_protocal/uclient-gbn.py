from socket import *
from threading import Thread
import time
import random

serverIP = '127.0.0.1' # special IP for local host
serverPort = 12000

win = 10      # window size
no_pkt = 1000 # the total number of packets to send
send_base = 0 # oldest packet sent
loss_rate = 0.01 # loss rate
seq = 0        # initial sequence number
reset=0
prv_ack=-1

clientSocket = socket(AF_INET, SOCK_DGRAM)

# thread for receiving and handling acks
def handling_ack():
    print("thread")
    global clientSocket
    global send_base
    global reset
    global seq
    global prv_ack

    
    while True:
        ack, serverAddress = clientSocket.recvfrom(2048)
        ack_n = int(ack.decode())

        print(ack_n)
        
        if(prv_ack+1!=ack_n):
            seq = ack_n
        else:
            send_base = ack_n + 1

        prv_ack = ack_n
        # window is moved upon receiving a new ack
        # window stays for cumulative ack

        
        if ack_n == 999:
            break;

# running a thread for receiving and handling acks
th_handling_ack = Thread(target = handling_ack, args = ())
th_handling_ack.start()

while seq < no_pkt:
    while seq < send_base + win: # send packets within window
        if random.random() < 1 - loss_rate: # emulate packet loss
            clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))
            time.sleep(0.01)
    
        seq = seq + 1
        
th_handling_ack.join() # terminating thread

print ("done")

clientSocket.close()

