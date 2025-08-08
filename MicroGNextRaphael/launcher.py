#!/usr/bin/env python3
"""
launcher.py: Launch the TCP→FIFO bridge and the GNURadio decoder.
Assumes the master shell script has already created all the FIFOs.
"""

import subprocess
import threading
import time
import sys
import os


TCP_SCRIPT     = "MicroGNextRaphael/TCP_out.py"
DECODER_SCRIPT = "MicroGNextRaphael/decoder_406v5.py"

def run_python(script, label, args):
    """
    Launch a Python script under `python -u` (unbuffered),
    force ANSI colors (FORCE_COLOR=1), and stream its stdout/stderr.
    """
    cmd = [sys.executable, "-u", script] + args
    env = os.environ.copy()
    env["FORCE_COLOR"] = "1"

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,               # line-buffered
        universal_newlines=True, # text mode
        env=env
    )

    threading.Thread(target=_stream_output, args=(proc, label), daemon=True).start()
    return proc

def _stream_output(proc, label):
    """Read lines from proc.stdout and print with [label]."""
    for line in proc.stdout:
        print(f"[{label}] {line}", end="")
    proc.stdout.close()

def main():
    # 1) Sanity check: make sure the FIFO exists
    # if not os.path.exists(TpythoCP_FIFO):
    #     print(f"ERROR: FIFO '{TCP_FIFO}' not found. Did you run the master script?", file=sys.stderr)
    #     sys.exit(1)

    # 2) Launch TCP_out.py (reads FIFOs/tcpTOpd)
    print("=== Starting TCP_out.py ===")
    tcp_proc = subprocess.Popen(['python3', './MicroGNextRaphael/TCP_out.py'])
    # tcp_proc = run_python(TCP_SCRIPT, "TCP_OUT", [])


    # give it a moment to open the pipe
    time.sleep(1)

    # 3) Launch the GNURadio decoder
    print("=== Starting decoder_406v5.py ===")
    dec_proc = subprocess.Popen(['python3', './MicroGNextRaphael/decoder_406v5.py'])


    # 4) Monitor both; if one exits, shut down the other
    try:
        while True:
            if tcp_proc.poll() is not None:
                print("TCP_OUT exited; terminating DECODER.")
                dec_proc.terminate()
                break
            if dec_proc.poll() is not None:
                print("DECODER exited; terminating TCP_OUT.")
                tcp_proc.terminate()
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Interrupted; terminating both.")
        tcp_proc.terminate()
        dec_proc.terminate()

    # 5) Wait for clean exit
    tcp_proc.wait()
    dec_proc.wait()
    print("All processes exited.")

if __name__ == "__main__":
    main()
