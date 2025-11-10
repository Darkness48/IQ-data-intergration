#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: chaejin
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
import osmosdr
import time
import sip
import threading
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation

import numpy as np
import time
from gnuradio import gr

class file_sink_10s(gr.sync_block):
    """
    300초 단위로 새로운 파일에 저장하고 평균 계산
    입력: float 벡터
    """
    def __init__(self, base_path="/home/chaejin/Downloads/dd/data", vec_len=8192):
        gr.sync_block.__init__(self,
            name="file_sink_300s",
            in_sig=[(np.float32, vec_len)],  # 벡터 길이 지정
            out_sig=None)

        self.base_path = base_path
        self.buffer = []
        self.start_time = time.time()
        self.file_index = 0
        self.vec_len = vec_len

    def work(self, input_items, output_items):
        data = input_items[0]
        self.buffer.extend(data.tolist())

        # 300초 경과 체크
        if time.time() - self.start_time >= 300:
            self.file_index += 1
            filename = f"{self.base_path}_{self.file_index:09d}.bin"
            np.array(self.buffer, dtype=np.float32).tofile(filename)

            print(f"Saved {filename}, samples={len(self.buffer)}")

            # 초기화
            self.buffer = []
            self.start_time = time.time()

        return len(data)

import numpy as np
import time
from gnuradio import gr

class please(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "please")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.vec = vec = 8192
        self.thro = thro = 2500000
        self.low = low = 1422000000
        self.hydro = hydro = 1420000000
        self.high = high = 1418000000

        ##################################################
        # Blocks
        ##################################################

        self.rtlsdr_source_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + "rtl=0"
        )
        self.rtlsdr_source_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0.set_sample_rate(thro)
        self.rtlsdr_source_0.set_center_freq(hydro, 0)
        self.rtlsdr_source_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0.set_gain(10, 0)
        self.rtlsdr_source_0.set_if_gain(20, 0)
        self.rtlsdr_source_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0.set_antenna('', 0)
        self.rtlsdr_source_0.set_bandwidth(0, 0)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            vec, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            hydro, #fc
            0, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/thro)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(True)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.fft_vxx_0 = fft.fft_vcc(vec, True, window.blackmanharris(8192), True, 1)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, thro, True, 0 if "auto" == "auto" else max( int(float(0.1) * thro) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, vec)
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(10, 1/10, 4000, 8192)
        self.blocks_python_file_10s = file_sink_10s("/home/chaejin/Downloads/dd/back_correction")
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(vec)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_python_file_10s, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.rtlsdr_source_0, 0), (self.qtgui_sink_x_0, 0))




    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "please")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_vec(self):
        return self.vec

    def set_vec(self, vec):
        self.vec = vec

    def get_thro(self):
        return self.thro

    def set_thro(self, thro):
        self.thro = thro
        self.blocks_throttle2_0.set_sample_rate(self.thro)
        self.rtlsdr_source_0.set_sample_rate(self.thro)

    def get_low(self):
        return self.low

    def set_low(self, low):
        self.low = low

    def get_hydro(self):
        return self.hydro

    def set_hydro(self, hydro):
        self.hydro = hydro
        self.qtgui_sink_x_0.set_frequency_range(self.hydro, 0)
        self.rtlsdr_source_0.set_center_freq(self.hydro, 0)

    def get_high(self):
        return self.high

    def set_high(self, high):
        self.high = high




def main(top_block_cls=please, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()

