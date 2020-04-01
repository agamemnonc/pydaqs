import time

import numpy as np
import serial
from serial.tools import list_ports

from .base import _BaseDAQ


class ArduinoDAQ(_BaseDAQ):
    def __init__(self, s_port, baud_rate, n_channels, samples_per_read):

        # If port is not given use the first one available
        if s_port is None:
            s_port = self.get_arduino_port()

        self.s_port = s_port
        self.baud_rate = baud_rate
        self.n_channels = n_channels
        self.samples_per_read = samples_per_read

        self._init()

    def _init(self):
        self.si = serial.Serial(port=self.s_port, baudrate=self.baud_rate,
                                timeout=1, writeTimeout=1)
        self.si.flushOutput()
        self.si.flushInput()

    def __del__(self):
        """Call stop() on destruct."""
        self.stop()

    def get_arduino_port(self):
        device = None
        comports = list_ports.comports()
        for port in comports:
            if port.description.startswith('Arduino'):
                device = port.device

        if device is None:
            raise Exception("Arduino COM port not found.")
        else:
            return device

    def start(self):
        """Open port and flush input/output."""
        if not self.si.is_open:
            self.si.open()
            self.si.flushOutput()
            self.si.flushInput()

    def stop(self):
        """Flush input/output and close port."""
        if self.si.is_open:
            self.si.flushInput()
            self.si.flushOutput()
            self.si.close()


    def read(self):
        """
        Request a sample of data from the device.

        This is a blocking method, meaning it returns only once the requested
        number of samples are available. The device does not support reading
        more than one samples at a time so this is implemented in a for loop.

        Returns
        -------
        data : ndarray, shape=(n_df, samples_per_read)
            Data read from the device. Each sensor is a row and each column
            is a point in time.
        """
        # self.si.flushInput()
        data = np.zeros((self.n_channels, self.samples_per_read))
        for i in range(self.samples_per_read):
            for channel in range(self.n_channels):
                cur_data = self.si.readline()
                try:
                    data[channel, i] = cur_data.decode()
                except:
                    print(cur_data)

        return data
