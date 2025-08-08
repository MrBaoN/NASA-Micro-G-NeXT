#!/usr/bin/env python3
#
# TagRewriter.py
# Simply copies the stream and rewrites any ‘packet_len’ tag to value=240.

import numpy as np
from gnuradio import gr
import pmt

class TagRewriter(gr.basic_block):
    def __init__(self, tag_key="packet_len", new_len=240):
        gr.basic_block.__init__(
            self,
            name="TagRewriter",
            in_sig =[np.int8],    # 1‐byte symbols in
            out_sig=[np.int8]     # 1‐byte symbols out
        )
        self.key     = pmt.intern(tag_key)
        self.new_val = pmt.from_long(int(new_len))
        # disable auto‐forward of tags
        self.set_tag_propagation_policy(gr.TPP_DONT)

    def forecast(self, noutput_items, ninput_items):
        # request equal number of inputs for outputs
        return (noutput_items,)

    def general_work(self, input_items, output_items):
        in0  = input_items[0]
        out0 = output_items[0]
        # only process as many as both buffers allow
        n = min(len(in0), len(out0))
        if n == 0:
            return 0

        # 1) copy samples one-by-one (avoids shape-broadcast errors)
        for i in range(n):
            out0[i] = in0[i]

        # 2) find any 'packet_len' tags in this window [0..n)
        tags = self.get_tags_in_window(0, 0, n)
        for t in tags:
            if t.key == self.key:
                # relative offset from start of this window
                rel_off = int(t.offset - self.nitems_read(0))
                # absolute offset in output stream
                abs_off = self.nitems_written(0) + rel_off
                # re-add the same tag but with value=new_len
                self.add_item_tag(0, abs_off, self.key, self.new_val)

        # 3) consume & produce
        self.consume(0, n)
        return n
