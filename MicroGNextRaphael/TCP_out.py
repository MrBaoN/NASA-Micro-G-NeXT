# #!/usr/bin/env python3
# import socket
# import os
# import errno
# import zmq
# import threading
# import select

# print("STARTING TCPOUT.py")

# # connect to ZMQ TCP server
# context = zmq.Context()
# socket2 = context.socket(zmq.PUSH)
# socket2.connect("tcp://localhost:5556")

# # ——— USER CONFIG ———
# HOST       = "127.0.0.1"     # must match your GRC TCP Sink Address
# PORT       = 5005            # must match your GRC TCP Sink Port
# # CAST_PIPE  = "/tmp/cast_pipe"
# # KML_PIPE   = "/tmp/kml_pipe"
# LOG_FILE   = "output.log"

# BIT_SYNC   = "1" * 15        # 15-bit bit-sync preamble
# FRAME_SYNC = "000101111"     # 9-bit frame-sync

# # # open FIFOs (will block until someone opens them for reading)
# # cast_fd = open(CAST_PIPE, "w")
# # kml_fd  = open(KML_PIPE,  "w")
# # # open a log file
# # log_fd  = open(LOG_FILE,   "a")

# # —— set up TCP server to match your GRC “Client” ——
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
#     srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     srv.bind((HOST, PORT))
#     srv.listen(1)
#     print(f"Listening on {HOST}:{PORT}… (waiting for GRC TCP Sink)")
#     conn, addr = srv.accept()
#     print(f"GRC connected from {addr}")

#     with conn:

#         while True:
#             # read exactly 15 bytes (120 bits) from GRC
#             buf = b""
#             while len(buf) < 15:
#                 chunk = conn.recv(15 - len(buf))
#                 if not chunk:
#                     print("Connection closed by GRC.")
#                     exit(0)
#                 buf += chunk

#             # expand each byte to 8 ASCII bits
#             payload_bits = "".join(f"{b:08b}" for b in buf)

#             # build full 144-bit message
#             full_msg = BIT_SYNC + FRAME_SYNC + payload_bits
#             socket2.send_unicode(full_msg)

#             print("→ forwarded:", full_msg)

# #!/usr/bin/env python3
# # -----------------------------------------------------------
# #  TCP_out.py  –  forward decoded 406 MHz beacon packets
# # -----------------------------------------------------------
# #
# #  • Reads 15-byte payloads from a named FIFO (created with mkfifo).
# #  • Prepends 15-bit bit-sync + 9-bit frame-sync.
# #  • Sends the 144-bit string to a ZMQ PUSH socket.
# #
# #  Start order:  (1) launch this script  →  (2) start GNU Radio.
# # -----------------------------------------------------------

# import os
# import errno
# import signal
# import zmq
# from datetime import datetime

# # --------------------- USER CONFIG -------------------------
# FIFO_PATH  = "/fifos/decoder_fifo"        # must match File Sink path
# ZMQ_ENDPOINT = "tcp://localhost:5556"  # consumer should bind PULL here
# BIT_SYNC   = "1" * 15                  # 15-bit 0x7FFF pattern
# FRAME_SYNC = "000101111"               # 9-bit 0x17F
# LOG_EVERY  = 100                       # print progress every N packets
# # -----------------------------------------------------------


# def make_fifo(path: str) -> None:
#     """Create FIFO if it doesn’t exist."""
#     if not os.path.exists(path):
#         os.mkfifo(path, 0o666)       # world-rw convenient for dev


# def reopen_fifo(path: str):
#     """
#     Open FIFO for *blocking* reads.
#     If the writer (GNU Radio) isn’t up yet, this blocks until it opens.
#     """
#     print(f"[{ts()}] Waiting for writer … ({path})")
#     fifo = open(path, "rb", buffering=0)
#     print(f"[{ts()}] Writer connected.")
#     return fifo


# def ts() -> str:
#     """ISO-8601 timestamp for logs."""
#     return datetime.now().isoformat(timespec="seconds")


# def main():
#     # 0. Ensure the FIFO exists; block until writer connects.
#     make_fifo(FIFO_PATH)
#     fifo = reopen_fifo(FIFO_PATH)

#     # 1. Prepare ZMQ PUSH socket.
#     ctx = zmq.Context.instance()
#     sock = ctx.socket(zmq.PUSH)
#     # Drop packets only if >10 000 enqueued (safety valve, can increase)
#     sock.setsockopt(zmq.SNDHWM, 10_000)
#     sock.connect(ZMQ_ENDPOINT)
#     print(f"[{ts()}] ZMQ PUSH → {ZMQ_ENDPOINT}")

#     # 2. Graceful shutdown on Ctrl-C.
#     def _sigint(sig, frame):
#         print(f"\n[{ts()}] Interrupted – exiting.")
#         fifo.close()
#         sock.close(0)
#         ctx.term()
#         raise SystemExit(0)
#     signal.signal(signal.SIGINT, _sigint)

#     # 3. Packet loop.
#     pkt_count = 0
#     while True:
#         try:
#             data = fifo.read(15)          # blocks until exactly 15 bytes
#             if len(data) != 15:
#                 # Writer closed; reopen FIFO to wait for new writer
#                 if len(data) == 0:
#                     print(f"[{ts()}] Writer closed FIFO. Reopening …")
#                     fifo.close()
#                     fifo = reopen_fifo(FIFO_PATH)
#                     continue
#                 else:                     # partial read (shouldn’t happen)
#                     continue

#             payload_bits = ''.join(f"{byte:08b}" for byte in data)
#             full_msg     = BIT_SYNC + FRAME_SYNC + payload_bits

#             sock.send_string(full_msg, flags=zmq.NOBLOCK)
#             pkt_count += 1
#             if pkt_count % LOG_EVERY == 0:
#                 print(f"[{ts()}] Forwarded {pkt_count} packets.")

#         except zmq.Again:
#             # High-water mark hit; drop packet or sleep
#             print(f"[{ts()}] ZMQ queue full – packet dropped.")
#         except BrokenPipeError:
#             # Reader on the other end of FIFO disappeared – reopen
#             print(f"[{ts()}] FIFO broken pipe – reopening.")
#             fifo.close()
#             fifo = reopen_fifo(FIFO_PATH)
#         except OSError as e:
#             if e.errno == errno.EINTR:
#                 continue
#             print(f"[{ts()}] OS error {e}")
#             break


# if __name__ == "__main__":
#     main()
#!/usr/bin/env python3
# ---------------------------------------------------------------------
#  TCP_out_multi.py  –  forward 406 MHz beacon packets from N ports
# ---------------------------------------------------------------------
#  • Starts one listener thread per port in PORTS.
#  • Each thread accepts exactly one GRC connection at a time.
#  • Reads 15-byte packets, prepends bit-/frame-sync, forwards via ZMQ.
# ---------------------------------------------------------------------

import socket
import zmq
import threading
from datetime import datetime

# ============ USER CONFIG ============================================
HOST      = "127.0.0.1"            # Match your GRC TCP Sink host
PORTS     = [5005, 5006]           # List *all* ports you want to accept
ZMQ_PUSH  = "tcp://localhost:5556" # Forwarding endpoint (PULL binds)
BIT_SYNC   = "1" * 15              # 15-bit preamble
FRAME_SYNC = "000101111"           # 9-bit frame-sync
# =====================================================================


def ts() -> str:
    """timestamp for logs"""
    return datetime.now().isoformat(timespec="seconds")


def recv_exact(sock: socket.socket, n: int) -> bytes | None:
    """read exactly n bytes or return None if connection closes"""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def serve_port(port: int):
    """
    Thread target – accept one client at a time on *port* and
    forward every 15-byte packet via its own ZMQ PUSH socket.
    """
    # ZMQ socket must be created inside the thread (thread-local)
    ctx = zmq.Context.instance()
    zsock = ctx.socket(zmq.PUSH)
    zsock.connect(ZMQ_PUSH)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, port))
        srv.listen(1)
        print(f"[{ts()}] Listening on {HOST}:{port} …")

        while True:  # accept-loop
            conn, addr = srv.accept()
            print(f"[{ts()}] Port {port}: GRC connected from {addr}")
            with conn:
                while True:  # packet-loop
                    buf = recv_exact(conn, 15)
                    if buf is None:
                        print(f"[{ts()}] Port {port}: connection closed.")
                        break

                    payload_bits = ''.join(f"{b:08b}" for b in buf)
                    full_msg     = BIT_SYNC + FRAME_SYNC + payload_bits
                    zsock.send_string(full_msg, flags=zmq.NOBLOCK)
                    # Optional debug:
                    # print(f"[{ts()}] Port {port} → {full_msg}")


def main():
    print(f"[{ts()}] Forwarding to ZMQ {ZMQ_PUSH}")
    print(f"[{ts()}] Launching listeners on ports {PORTS}")

    threads = []
    for p in PORTS:
        t = threading.Thread(target=serve_port, args=(p,), daemon=True)
        t.start()
        threads.append(t)

    # Keep main thread alive; Ctrl-C to exit
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print(f"\n[{ts()}] Interrupted – shutting down.")


if __name__ == "__main__":
    main()