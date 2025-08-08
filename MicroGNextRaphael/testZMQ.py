#!/usr/bin/env python3
import socket
import os
import errno
import time
import zmq

# connect to ZMQ TCP server
context = zmq.Context()
socket2 = context.socket(zmq.REQ)
socket2.connect("tcp://localhost:5556")
while True:
    socket2.send(b"Hello from TCP_out.py")
    time.sleep(1)