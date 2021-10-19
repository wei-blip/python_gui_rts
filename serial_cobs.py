#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from serial.threaded import Packetizer
from cobs import cobs

class COBSPacketizer(Packetizer):
    """
    Read and write COBS packets from/to serial port.
    """
    
    TERMINATOR = b'\0'

    def handle_packet(self, packet):
        self.handle_cobs(cobs.decode(packet))

    def handle_cobs(self, data):
        """Process packets - to be overridden by subclassing"""
        raise NotImplementedError('please implement functionality in handle_cobs')

    def write_cobs(self, data):
        packet = cobs.encode(data) + self.TERMINATOR
        self.transport.write(packet)
