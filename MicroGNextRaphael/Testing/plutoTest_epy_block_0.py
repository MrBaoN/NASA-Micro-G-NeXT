#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: GPL-3.0
#
# This block prints debug information for each PDU that it receives.
# It prints fixed values such as the Data Rate and SPS (samples per symbol),
# and then prints the packet payload (in hex and bits) along with any metadata.
#

import pmt
from gnuradio import gr
from colorama import init, Fore, Style

# Initialize Colorama (autoreset means color is reset after each print)
init(autoreset=True)

def format_bytes_as_hex(data_bytes):
    return ' '.join(f"{byte:02X}" for byte in data_bytes)

def format_bytes_as_bits(data_bytes):
    return ' '.join(f"{byte:08b}" for byte in data_bytes)

class debug_info_py(gr.basic_block):
    """
    This custom block prints debug information about the PDUs it receives.
    
    Parameters:
      - data_rate (int): The data rate in bits per second.
      - sps (int): The samples per symbol.
    
    It expects message PDUs on port "in", where each message is a PMT pair (meta, payload).
    The payload must be a u8vector or blob containing the packet bytes.
    It prints:
      * The fixed debug info (data rate, sps)
      * The payload in hexadecimal and in binary format
      * Any metadata converted to a Python dictionary.
    
    Attach this block (after your constellation decoder) to see a debug printout similar to your debug_tcp.
    """
    
    def __init__(self, data_rate=400, sps=170):
        gr.basic_block.__init__(self,
            name="debug_info_py",
            in_sig=[],
            out_sig=[])
        # Register a single message input port named "in"
        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)
        self.data_rate = data_rate
        self.sps = sps

    def handle_msg(self, msg):
        # Check that the incoming message is a PMT pair (meta, payload)
        if not pmt.is_pair(msg):
            print(f"{Fore.RED}[DEBUG_INFO] Received message is not a pair: {msg}")
            return

        meta = pmt.car(msg)
        data = pmt.cdr(msg)
        
        # Convert the payload to a Python list of integers.
        # It may be a u8vector or a blob. (Using PMT functions accordingly.)
        if pmt.is_u8vector(data):
            byte_data = pmt.u8vector_elements(data)
        elif pmt.is_blob(data):
            # pmt.binary_elements returns a bytes object.
            byte_data = bytearray(pmt.binary_elements(data))
        else:
            print(f"{Fore.RED}[DEBUG_INFO] Data is not a u8vector or blob: {data}")
            return

        # Print the fixed parameters (data_rate and sps)
        print(f"{Fore.CYAN}[DEBUG_INFO]{Style.RESET_ALL} Data Rate: {self.data_rate} bits/sec, SPS: {self.sps}")
        print(f"{Fore.CYAN}[DEBUG_INFO]{Style.RESET_ALL} Packet received:")
        
        # Print the payload in hex and binary format
        hex_str = format_bytes_as_hex(byte_data)
        bits_str = format_bytes_as_bits(byte_data)
        print(f"{Fore.MAGENTA}Hex: {hex_str}")
        print(f"{Fore.MAGENTA}Bits: {bits_str}")
        
        # If there is metadata, try to convert it to a Python dictionary and print it.
        meta_dict = pmt.to_python(meta)
        if meta_dict:
            print(f"{Fore.YELLOW}[DEBUG_INFO]{Style.RESET_ALL} Meta:")
            for key, val in meta_dict.items():
                print(f"  {key} : {val}")
