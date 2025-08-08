#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: decoder_406v5
# Author: rclar
# GNU Radio version: 3.10.10.0

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
from gnuradio import network
import decoder_406v5_packet_extractor as packet_extractor  # embedded python block
import decoder_406v5_packet_extractor_0 as packet_extractor_0  # embedded python block
import decoder_406v5_tag_setter as tag_setter  # embedded python block
import decoder_406v5_tag_setter_0 as tag_setter_0  # embedded python block
import math




class decoder_406v5(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "decoder_406v5", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.variable_constellation_rect_0 = variable_constellation_rect_0 = digital.constellation_rect([-1, +1,], [0, 1],
        4, 2, 2, 1, 1).base()
        self.samp_rate = samp_rate = 680000
        self.decim = decim = 85
        self.sps = sps = 850
        self.samples_per_bit = samples_per_bit = 1700
        self.decim_taps = decim_taps = firdes.low_pass(1.0, samp_rate, samp_rate/decim,samp_rate/decim/8, window.WIN_HAMMING, 6.76)
        self.cma_aa_1 = cma_aa_1 = digital.adaptive_algorithm_cma( digital.constellation_bpsk().base(), .0001, 2).base()
        self.cma_aa = cma_aa = digital.adaptive_algorithm_cma( variable_constellation_rect_0, .0001, 2).base()
        self.carrier_frequency = carrier_frequency = 2000

        ##################################################
        # Blocks
        ##################################################

        self.tag_setter_0 = tag_setter_0.TagRewriter(tag_key="packet_len", new_len=240)
        self.tag_setter = tag_setter.TagRewriter(tag_key="packet_len", new_len=240)
        self.packet_extractor_0 = packet_extractor_0.ManchesterDecoderBlock(tag_name="packet_len")
        self.packet_extractor = packet_extractor.ManchesterDecoderBlock(tag_name="packet_len")
        self.network_tcp_sink_0_0 = network.tcp_sink(gr.sizeof_char, 1, '127.0.0.1', 5006,1)
        self.network_tcp_sink_0 = network.tcp_sink(gr.sizeof_char, 1, '127.0.0.1', 5005,1)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                (10*samp_rate/sps),
                (2*samp_rate/sps),
                window.WIN_HAMMING,
                6.76))
        self.interp_fir_filter_xxx_0 = filter.interp_fir_filter_ccc(1, [1/sps,] * int(sps))
        self.interp_fir_filter_xxx_0.declare_sample_delay(0)
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32('ip:192.168.4.1' if 'ip:192.168.4.1' else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0.set_len_tag_key("")
        self.iio_pluto_source_0.set_frequency(406025000)
        self.iio_pluto_source_0.set_samplerate(samp_rate)
        self.iio_pluto_source_0.set_gain_mode(0, 'fast_attack')
        self.iio_pluto_source_0.set_gain(0, 37)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.digital_symbol_sync_xx_0_0_0 = digital.symbol_sync_cc(
            digital.TED_ZERO_CROSSING,
            850,
            (2*math.pi*.04),
            1,
            1.0,
            1.5,
            2,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_linear_equalizer_0 = digital.linear_equalizer(15, 2, cma_aa, False, [ ], 'corr_est')
        self.digital_costas_loop_cc_0_0 = digital.costas_loop_cc(.350, 2, False)
        self.digital_correlate_access_code_tag_xx_0_0 = digital.correlate_access_code_tag_bb('010101100110101010', 0, "packet_len")
        self.digital_correlate_access_code_tag_xx_0 = digital.correlate_access_code_tag_bb('010101100110101010', 0, "packet_len")
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(variable_constellation_rect_0)
        self.dc_blocker_xx_1 = filter.dc_blocker_cc((8*sps), True)
        self.blocks_xor_xx_0 = blocks.xor_bb()
        self.blocks_tagged_stream_align_0_0 = blocks.tagged_stream_align(gr.sizeof_char*1, "packet_len")
        self.blocks_tagged_stream_align_0 = blocks.tagged_stream_align(gr.sizeof_char*1, "packet_len")
        self.blocks_tag_gate_0 = blocks.tag_gate(gr.sizeof_gr_complex * 1, False)
        self.blocks_tag_gate_0.set_single_key("")
        self.analog_pwr_squelch_xx_0 = analog.pwr_squelch_cc((-50), (1e-3), 0, False)
        self.analog_const_source_x_0 = analog.sig_source_b(0, analog.GR_CONST_WAVE, 0, 0, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_xor_xx_0, 1))
        self.connect((self.analog_pwr_squelch_xx_0, 0), (self.digital_costas_loop_cc_0_0, 0))
        self.connect((self.blocks_tag_gate_0, 0), (self.analog_pwr_squelch_xx_0, 0))
        self.connect((self.blocks_tagged_stream_align_0, 0), (self.packet_extractor, 0))
        self.connect((self.blocks_tagged_stream_align_0_0, 0), (self.packet_extractor_0, 0))
        self.connect((self.blocks_xor_xx_0, 0), (self.digital_correlate_access_code_tag_xx_0_0, 0))
        self.connect((self.dc_blocker_xx_1, 0), (self.digital_symbol_sync_xx_0_0_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.blocks_xor_xx_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.digital_correlate_access_code_tag_xx_0, 0))
        self.connect((self.digital_correlate_access_code_tag_xx_0, 0), (self.tag_setter, 0))
        self.connect((self.digital_correlate_access_code_tag_xx_0_0, 0), (self.tag_setter_0, 0))
        self.connect((self.digital_costas_loop_cc_0_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.digital_linear_equalizer_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.digital_symbol_sync_xx_0_0_0, 0), (self.digital_linear_equalizer_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.blocks_tag_gate_0, 0))
        self.connect((self.interp_fir_filter_xxx_0, 0), (self.dc_blocker_xx_1, 0))
        self.connect((self.low_pass_filter_0, 0), (self.interp_fir_filter_xxx_0, 0))
        self.connect((self.packet_extractor, 0), (self.network_tcp_sink_0, 0))
        self.connect((self.packet_extractor_0, 0), (self.network_tcp_sink_0_0, 0))
        self.connect((self.tag_setter, 0), (self.blocks_tagged_stream_align_0, 0))
        self.connect((self.tag_setter_0, 0), (self.blocks_tagged_stream_align_0_0, 0))


    def get_variable_constellation_rect_0(self):
        return self.variable_constellation_rect_0

    def set_variable_constellation_rect_0(self, variable_constellation_rect_0):
        self.variable_constellation_rect_0 = variable_constellation_rect_0
        self.digital_constellation_decoder_cb_0.set_constellation(self.variable_constellation_rect_0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_decim_taps(firdes.low_pass(1.0, self.samp_rate, self.samp_rate/self.decim, self.samp_rate/self.decim/8, window.WIN_HAMMING, 6.76))
        self.iio_pluto_source_0.set_samplerate(self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (10*self.samp_rate/self.sps), (2*self.samp_rate/self.sps), window.WIN_HAMMING, 6.76))

    def get_decim(self):
        return self.decim

    def set_decim(self, decim):
        self.decim = decim
        self.set_decim_taps(firdes.low_pass(1.0, self.samp_rate, self.samp_rate/self.decim, self.samp_rate/self.decim/8, window.WIN_HAMMING, 6.76))

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.interp_fir_filter_xxx_0.set_taps([1/self.sps,] * int(self.sps))
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (10*self.samp_rate/self.sps), (2*self.samp_rate/self.sps), window.WIN_HAMMING, 6.76))

    def get_samples_per_bit(self):
        return self.samples_per_bit

    def set_samples_per_bit(self, samples_per_bit):
        self.samples_per_bit = samples_per_bit

    def get_decim_taps(self):
        return self.decim_taps

    def set_decim_taps(self, decim_taps):
        self.decim_taps = decim_taps

    def get_cma_aa_1(self):
        return self.cma_aa_1

    def set_cma_aa_1(self, cma_aa_1):
        self.cma_aa_1 = cma_aa_1

    def get_cma_aa(self):
        return self.cma_aa

    def set_cma_aa(self, cma_aa):
        self.cma_aa = cma_aa

    def get_carrier_frequency(self):
        return self.carrier_frequency

    def set_carrier_frequency(self, carrier_frequency):
        self.carrier_frequency = carrier_frequency




def main(top_block_cls=decoder_406v5, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
