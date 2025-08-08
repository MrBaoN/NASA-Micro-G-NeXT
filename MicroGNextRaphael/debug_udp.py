import socket
import time
from colorama import Fore, init

init(autoreset=True)

HOST = "127.0.0.1"
PORT = 5005
PACKET_SIZE = 18   # bytes

def print_packet(packet):
    hex_str = ' '.join(f"{b:02X}" for b in packet)
    bit_str = ' '.join(f"{b:08b}" for b in packet)
    print(Fore.YELLOW + "[RECV] Packet received:")
    print(Fore.CYAN   + f"  Hex:  {hex_str}")
    print(Fore.MAGENTA+ f"  Bits: {bit_str}")

# set up UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
print(Fore.CYAN + f"[UDP] Listening on {HOST}:{PORT} …")

while True:
    packet, _ = sock.recvfrom(PACKET_SIZE)
    if len(packet) == PACKET_SIZE:
        print_packet(packet)
