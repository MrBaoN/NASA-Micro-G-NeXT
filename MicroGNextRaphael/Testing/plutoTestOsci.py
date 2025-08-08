#!/usr/bin/env python3
from gnuradio import gr, blocks, qtgui, iio
from PyQt5 import Qt
import sip
import sys

class PlutoLoopback(gr.top_block, Qt.QWidget):
    def __init__(self):
        gr.top_block.__init__(self, "Pluto TX→RX Loopback Visual Test")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Pluto Loopback")
        self.layout = Qt.QVBoxLayout(self)

        ##################################################
        # Parameters
        ##################################################
        freq = int(915e6)
        samp_rate = int(1e6)
        tx_gain = 0
        rx_gain = 40
        buffer_size = 32768

        ##################################################
        # TX: Constant 1+0j
        ##################################################
        const_src = blocks.vector_source_c([1+0j], True)

        tx = iio.pluto_sink(
            uri="ip:192.168.2.1",
            frequency=freq,
            samplerate=samp_rate,
            buffer_size=buffer_size,
            cyclic=True,
            quadrature=True,
            rf_bandwidth=samp_rate,
            attenuation=tx_gain
        )

        self.connect(const_src, tx)

        ##################################################
        # RX: Pluto Source
        ##################################################
        rx = iio.pluto_source(
            uri="ip:192.168.2.1",
            frequency=freq,
            samplerate=samp_rate,
            buffer_size=buffer_size,
            quadrature=True,
            rf_bandwidth=samp_rate,
            gain=rx_gain
        )

        ##################################################
        # Visual Sinks
        ##################################################

        # Time Domain
        time_sink = qtgui.time_sink_c(1024, samp_rate, "RX Time", 1)
        self.layout.addWidget(sip.wrapinstance(time_sink.pyqwidget(), Qt.QWidget))
        self.connect(rx, time_sink)

        # Constellation
        const_sink = qtgui.const_sink_c(1024, "RX Constellation", 1)
        self.layout.addWidget(sip.wrapinstance(const_sink.pyqwidget(), Qt.QWidget))
        self.connect(rx, const_sink)

if __name__ == '__main__':
    app = Qt.QApplication(sys.argv)
    tb = PlutoLoopback()
    tb.start()
    tb.show()
    app.exec_()
    tb.stop()
    tb.wait()
