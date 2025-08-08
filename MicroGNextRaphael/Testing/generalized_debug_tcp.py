
import socket
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

def print_debug_packet(data):
    timestamp = datetime.now().strftime("%H:%M:%S")
    hex_string = " ".join(f"{b:02X}" for b in data)
    bit_string = " ".join(f"{b:08b}" for b in data)

    print(f"{Fore.YELLOW}[{timestamp}] Packet received ({len(data)} bytes):")
    print(f"{Fore.GREEN}  Hex: {hex_string}")
    print(f"{Fore.CYAN}  Bits: {bit_string}")
    print(f"{Style.DIM}  Raw: {data!r}\n")

def run_tcp_listener(host='127.0.0.1', port=5005):
    print(f"{Fore.MAGENTA}Listening on {host}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)
    conn, addr = sock.accept()
    print(f"{Fore.GREEN}Connected by {addr}")
    
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print_debug_packet(data)
    except KeyboardInterrupt:
        print(f"{Fore.RED}\nTerminating listener.")
    finally:
        conn.close()
        sock.close()

if __name__ == "__main__":
    run_tcp_listener()
