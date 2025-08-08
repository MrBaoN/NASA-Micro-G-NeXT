#!/usr/bin/env python3
import sys
import os
import time
import zmq

# run with python3 testPacketGenerator.py test.txt test2.txt

def main():
    context = zmq.Context()
    socket2 = context.socket(zmq.PUSH)
    socket2.connect("tcp://localhost:5556")

    input_file = "test1.txt"
    input_file2 = "test2.txt"
    
    with open(input_file, 'r') as f:
        data1 = f.read().strip()
        if not all(c in '01' for c in data1):
            print("Error: Input file should contain only 0s and 1s")
            sys.exit(1)
        binary_data1 = bytes([int(data1[i:i+8], 2) 
                    for i in range(0, len(data1), 8)])
    with open(input_file2, 'r') as f:
        data2 = f.read().strip()
        if not all(c in '01' for c in data2):
            print("Error: Input file should contain only 0s and 1s")
            sys.exit(1)
        binarydata2 = bytes([int(data2[i:i+8], 2) 
                            for i in range(0, len(data2), 8)])

    # send data / main loop
    while True:
        for i in range(10):
            socket2.send_unicode(data1)
            time.sleep(0.5)
        # socket2.send(binarydata2)

if __name__ == "__main__":
    main()
