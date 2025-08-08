import numpy as np
from gnuradio import gr
import pmt
from colorama import Fore, Style, init

# Initialize Colorama (for colored debug output in console)
init(autoreset=True)

class ManchesterDecoderBlock(gr.basic_block):
    def __init__(self, tag_name="packet_len"):
        gr.basic_block.__init__(
            self,
            name="ManchesterDecoder",
            in_sig=[np.uint8],   # input: stream of 8-bit (char) samples (0 or 1)
            out_sig=[np.uint8]   # output: stream of 8-bit decoded bytes
        )
        self.tag_name = pmt.intern(tag_name)
        self.set_tag_propagation_policy(gr.TPP_DONT)   # handle tags manually&#8203;:contentReference[oaicite:6]{index=6}

        # State for collecting packet bits
        self._collecting = False
        self._buffer = []       # buffer for Manchester bits of the current packet
        self._needed_bits = 0   # how many more bits are needed to complete current packet

        # Ensure output buffer can accommodate full packets (15 bytes)
        self.set_output_multiple(15)

    def forecast(self, noutput_items, ninput_items):
        """
        Tell GR how many input items are required on each input port
        to produce noutput_items on the output port.

        Since we only ever want to process full 240‐sample bursts:
          - If we’re not currently collecting a packet, we need 240 samples
          - If we’re mid‐packet, we need however many bits remain
        """
        if self._collecting:
            # we’re in the middle of gathering a packet:
            needed = self._needed_bits
        else:
            # waiting for a new packet start → need full burst
            needed = 240

        # return a tuple (one entry per input port)
        return (needed,)


    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]
        n_in = len(in0)

        # If not currently in a packet, look for a 'packet_len' tag to start a new burst
        if not self._collecting:
            # No ongoing packet, search for the start tag in this input window
            tags = self.get_tags_in_window(0, 0, n_in, self.tag_name)
            if len(tags) == 0:
                # No packet start tag found in this chunk
                if n_in > 0:
                    # print(Fore.YELLOW + f"No packet tag found in {n_in} samples – dropping them." + Style.RESET_ALL)
                    self.consume(0, n_in)  # discard irrelevant samples
                return 0  # no output produced

            # We found at least one tag; consider the first tag as start of a new packet
            tags.sort(key=lambda t: t.offset)
            tag = tags[0]
            tag_offset = tag.offset - self.nitems_read(0)  # relative index of tag in the buffer&#8203;:contentReference[oaicite:7]{index=7}
            if tag_offset > 0:
                # Skip any samples preceding the tag (shouldn't contain valid data)
                # print(Fore.MAGENTA + f"Skipping {tag_offset} pre-tag sample(s) (noise/preamble)." + Style.RESET_ALL)
                self.consume(0, tag_offset)
                # Adjust input array to start at the tag position
                in0 = in0[tag_offset:]
                n_in -= tag_offset
                tag_offset = 0

            # Initialize a new packet collection
            self._collecting = True
            # Determine expected packet length from tag (should be 240)
            pkt_len = pmt.to_python(tag.value)
            if isinstance(pkt_len, (list, tuple)):  # safety: convert PMT vector or u64 to int
                pkt_len = int(pkt_len[0] if pkt_len else 0)
            else:
                pkt_len = int(pkt_len)
            expected_bits = pkt_len
            if expected_bits != 240:
                # Log a warning if the tag length is not the expected 240
                print(Fore.YELLOW + f"Warning: tag indicates {expected_bits} bits (expected 240)." + Style.RESET_ALL)
            self._needed_bits = expected_bits
            self._buffer = []
            print(Fore.CYAN + f"Packet start detected (tag at input 0). Expecting {expected_bits} Manchester bits..." + Style.RESET_ALL)

            # Process available bits in this call for the new packet
            if n_in >= self._needed_bits:
                # We have the entire 240-bit burst in this chunk
                needed = self._needed_bits
                bits_chunk = in0[:needed]
                self._buffer.extend(bits_chunk.tolist())
                print(Fore.CYAN + f"Collected all {needed} bits for packet, decoding..." + Style.RESET_ALL)
                self._decode_and_output_packet(out0)  # decode and write output bytes
                # Consume the 240 input bits used for this packet
                self.consume(0, needed)
                # (If there are extra bits beyond this packet in 'in0', leave them for the next call)
                return len(out0[:15])  # produced 15 bytes (or 0 if decode failed)
            else:
                # Only a partial burst is available; buffer it and wait for more
                self._buffer.extend(in0.tolist())
                self._needed_bits -= n_in
                print(Fore.CYAN + f"Collected {n_in} bits (partial packet). Waiting for {self._needed_bits} more bits..." + Style.RESET_ALL)
                self.consume(0, n_in)  # consume all available input
                # No output yet (packet not complete)
                return 0

        else:
            # We are in the middle of gathering a packet (a previous tag was seen)
            if n_in == 0:
                return 0  # nothing to do

            if n_in >= self._needed_bits:
                # This chunk provides the remaining bits to finish the packet
                needed = self._needed_bits
                bits_chunk = in0[:needed]
                self._buffer.extend(bits_chunk.tolist())
                print(Fore.CYAN + f"Received final {needed} bits, packet complete. Decoding..." + Style.RESET_ALL)
                self._decode_and_output_packet(out0)
                self.consume(0, needed)  # consume only the bits used for this packet
                return len(out0[:15])  # 15 bytes output (or 0 if decode failed)
            else:
                # Still not enough to finish; accumulate and continue waiting
                self._buffer.extend(in0.tolist())
                self._needed_bits -= n_in
                print(Fore.CYAN + f"Received {n_in} more bits (total collected {len(self._buffer)}). Still need {self._needed_bits} bits..." + Style.RESET_ALL)
                self.consume(0, n_in)
                return 0

    def _decode_and_output_packet(self, out_buffer):
        """
        Decode the 240-bit Manchester buffer into 15 bytes and output to out_buffer.
        Attaches an output tag and prints debug info. If decode fails, drops packet.
        """
        # We expect exactly 240 bits in the buffer when called
        bits = self._buffer
        self._collecting = False   # reset state for next packet
        self._needed_bits = 0

        if len(bits) != 240:
            # Safety check (should not happen if logic is correct)
            print(Fore.RED + f"Error: Collected {len(bits)} bits, expected 240. Dropping packet." + Style.RESET_ALL)
            self._buffer = []
            return

        # Manchester decode: map (0,1)->0 and (1,0)->1
                # Manchester decode with “flatten‐to‐0” on invalid pairs
        decoded_bits = []
        for i in range(0, 240, 2):
            b0 = bits[i]
            b1 = bits[i+1]
            if (b0, b1) == (0, 1):
                decoded_bits.append(0)
            elif (b0, b1) == (1, 0):
                decoded_bits.append(1)
            else:
                # Invalid pair: flatten to 0 and keep going
                decoded_bits.append(0)
                # print(Fore.YELLOW + f"[MD][WARN] Invalid pair at {i}:({b0},{b1}), flattened to 0." + Style.RESET_ALL)


        # Clear buffer for next packet regardless of outcome
        self._buffer = []


        # Pack 120 decoded bits into 15 bytes (MSB-first in each byte)
        decoded_bytes = []
        for j in range(0, 120, 8):
            byte_val = 0
            for bit in decoded_bits[j:j+8]:
                byte_val = (byte_val << 1) | bit
            decoded_bytes.append(byte_val)
        decoded_bytes = np.array(decoded_bytes, dtype=np.uint8)  # 15-byte array

        # Add a 'packet_len' tag to mark this 15-byte packet on output&#8203;:contentReference[oaicite:8]{index=8}
        self.add_item_tag(
            0, 
            self.nitems_written(0),             # absolute position of first output byte
            self.tag_name, 
            pmt.from_long(len(decoded_bytes))   # value = 15
        )
        # Output the decoded bytes
        out_buffer[:len(decoded_bytes)] = decoded_bytes
        # Debug output of the decoded payload
        print(Fore.GREEN + f"Decoded Standard packet -> {len(decoded_bits)} bits into {len(decoded_bytes)} bytes: " 
              + ' '.join(f'0x{b:02X}' for b in decoded_bytes) + Style.RESET_ALL)
        print(Fore.GREEN + f"Emitted packet of {len(decoded_bytes)} byte(s).\n" + Style.RESET_ALL)
