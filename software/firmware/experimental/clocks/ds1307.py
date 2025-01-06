"""
Interface class for the DS1307 Realtime Clock

This class is designed to work with a DS1307 chip mounted on an I2C carrier board
that can be connected to EuroPi's external I2C interface. The user us required to
1) provide their own RTC module
2) create/source an appropriate adapter to connect the GND, VCC, SDA, and SCL pins on EuroPi
   to the RTC module
3) Mount the RTC module securely in such a way that it won't come loose nor accidentally short out
   any other components.

Based on work by Mike Causer released under the MIT license (c) 2018:
https://github.com/mcauser/micropython-tinyrtc-i2c/blob/master/ds1307.py


NOTE: the author of this module does NOT have access to a DS1307 module; this class is thoroughly
untested. USE AT YOUR OWN RISK.

Hopefully I, or another EuroPi contributor, will get access to the required module to validate the code.
But at present this class is provided as-is, based wholly on Mike Causer's work with the necessary
changes to support EuroPi's RTC interface.
"""

from micropython import const
from experimental.clocks.clock_source import ExternalClockSource

DATETIME_REG = const(0) # 0x00-0x06
CHIP_HALT    = const(128)
CONTROL_REG  = const(7) # 0x07
RAM_REG      = const(8) # 0x08-0x3F


class DS1307(ExternalClockSource):
    """Driver for the DS1307 RTC."""
    def __init__(self, i2c, addr=0x68):
        super().__init__()
        self.i2c = i2c
        self.addr = addr
        self.weekday_start = 1
        self._halt = False

    def _dec2bcd(self, value):
        """Convert decimal to binary coded decimal (BCD) format"""
        return (value // 10) << 4 | (value % 10)

    def _bcd2dec(self, value):
        """Convert binary coded decimal (BCD) format to decimal"""
        return ((value >> 4) * 10) + (value & 0x0F)

    def datetime(self):
        """
        Get the current time.

        @return datetime : tuple, (0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])
        """
        buf = self.i2c.readfrom_mem(self.addr, DATETIME_REG, 7)
        return (
            self._bcd2dec(buf[6]) + 2000, # year
            self._bcd2dec(buf[5]), # month
            self._bcd2dec(buf[4]), # day
            self._bcd2dec(buf[3] - self.weekday_start), # weekday
            self._bcd2dec(buf[2]), # hour
            self._bcd2dec(buf[1]), # minute
            self._bcd2dec(buf[0] & 0x7F), # second
            0 # subseconds
        )

    def set_datetime(self, datetime):
        """
        Set the current time.

        @param datetime : tuple, (0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])
        """
        buf = bytearray(7)
        buf[0] = self._dec2bcd(datetime[6]) & 0x7F # second, msb = CH, 1=halt, 0=go
        buf[1] = self._dec2bcd(datetime[5]) # minute
        buf[2] = self._dec2bcd(datetime[4]) # hour
        buf[3] = self._dec2bcd(datetime[3] + self.weekday_start) # weekday
        buf[4] = self._dec2bcd(datetime[2]) # day
        buf[5] = self._dec2bcd(datetime[1]) # month
        buf[6] = self._dec2bcd(datetime[0] - 2000) # year
        if (self._halt):
            buf[0] |= (1 << 7)
        self.i2c.writeto_mem(self.addr, DATETIME_REG, buf)

    def halt(self, val=None):
        """Power up, power down or check status"""
        if val is None:
            return self._halt
        reg = self.i2c.readfrom_mem(self.addr, DATETIME_REG, 1)[0]
        if val:
            reg |= CHIP_HALT
        else:
            reg &= ~CHIP_HALT
        self._halt = bool(val)
        self.i2c.writeto_mem(self.addr, DATETIME_REG, bytearray([reg]))

    def square_wave(self, sqw=0, out=0):
        """Output square wave on pin SQ at 1Hz, 4.096kHz, 8.192kHz or 32.768kHz,
        or disable the oscillator and output logic level high/low."""
        rs0 = 1 if sqw == 4 or sqw == 32 else 0
        rs1 = 1 if sqw == 8 or sqw == 32 else 0
        out = 1 if out > 0 else 0
        sqw = 1 if sqw > 0 else 0
        reg = rs0 | rs1 << 1 | sqw << 4 | out << 7
        self.i2c.writeto_mem(self.addr, CONTROL_REG, bytearray([reg]))
