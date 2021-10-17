from socket import *
from threading import Thread
import random
import time

serverIP = '127.0.0.1' # special IP for local host
serverPort = 12000
clientPort = 12001

win = 10      # window size
no_pkt = 1000 # the total number of packets to send
send_base = 0 # oldest packet sent
loss_rate = 0.01 # loss rate
seq = 0        # initial sequence number
timeout_flag = 0 # timeout trigger
timeout_interval = 10  # timeout interval



sent_time = [0 for i in range(2000)]



clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(('', clientPort))
clientSocket.setblocking(0)

# thread for receiving and handling acks
def handling_ack():
    print("thread")
    global clientSocket
    global send_base
    global timeout_flag
    global sent_time

    timeout_interval=10
    estimate_RTT = 0
    dev_RTT = 0
    
    while True:

        if sent_time[send_base] != 0: 
            pkt_delay = time.time() - sent_time[send_base]
     
            
        if pkt_delay > timeout_interval and timeout_flag == 0:    # timeout detected
            print("timeout detected:", str(send_base), flush=True)
            timeout_flag = 1

        try:
            ack, serverAddress = clientSocket.recvfrom(2048)
            ack_n = int(ack.decode())

            sample_RTT = time.time() - sent_time[send_base]

            estimate_RTT = 0.875*estimate_RTT+0.125*sample_RTT
            dev_RTT = (0.75)*dev_RTT + 0.25*abs(sample_RTT - estimate_RTT)

            timeout_interval = estimate_RTT + 4*dev_RTT

            print(ack_n, flush=True)
        except BlockingIOError:
            continue
            
        # window is moved upon receiving a new ack
        # window stays for cumulative ack
        send_base = ack_n + 1
        
        if ack_n == 999:
            break;

# running a thread for receiving and handling acks
th_handling_ack = Thread(target = handling_ack, args = ())
th_handling_ack.start()

while seq < no_pkt:
    while seq < send_base + win: # send packets within window
        if random.random() < 1 - loss_rate: # emulate packet loss
            clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))  
        sent_time[seq] = time.time()    
        seq = seq + 1
        
    if timeout_flag == 1: # retransmission
        seq = send_base 
        clientSocket.sendto(str(seq).encode(), (serverIP, serverPort))
        sent_time[seq] = time.time()    
        seq = seq + 1
        timeout_flag = 0
        print("retransmission:", str(seq), flush=True)
        
th_handling_ack.join() # terminating thread

print ("done")

clientSocket.close()

