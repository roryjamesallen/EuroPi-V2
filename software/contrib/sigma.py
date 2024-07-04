#!/usr/bin/env python3
"""Gaussian-based, clocked, quantized CV generator

Inspired by Magnetic Freak's Gaussian module.

@author  Chris Iverach-Brereton
@year    2024
"""

from europi import *
from europi_script import EuroPiScript

import configuration
import time

from experimental.knobs import *
from experimental.random_extras import normal
from experimental.screensaver import Screensaver


def bisect_left(a, x, lo=0, hi=None, *, key=None):
    """Return the index where to insert item x in list a, assuming a is sorted.

    The return value i is such that all e in a[:i] have e < x, and all e in
    a[i:] have e >= x.  So if x already appears in the list, a.insert(i, x) will
    insert just before the leftmost x already there.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.

    A custom key function can be supplied to customize the sort order.

    Copied from https://github.com/python/cpython/blob/3.12/Lib/bisect.py
    """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    # Note, the comparison uses "<" to match the
    # __lt__() logic in list.sort() and in heapq.
    if key is None:
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] < x:
                lo = mid + 1
            else:
                hi = mid
    else:
        while lo < hi:
            mid = (lo + hi) // 2
            if key(a[mid]) < x:
                lo = mid + 1
            else:
                hi = mid
    return lo


class OutputBin:
    """Generic class for different output modes"""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def closest(self, v):
        """Abstract function to be implemented by subclasses

        @param v  The input voltage to assign to a bin
        """
        raise Exception("Not implemented")


class ContinuousBin(OutputBin):
    """Smooth, continuous output"""
    def __init__(self, name):
        super().__init__(name)

    def closest(self, v):
        return v


class VoltageBin(OutputBin):
    """Quantizes a random voltage to the closest bin"""
    def __init__(self, name, bins):
        """Create a new set of bins

        @param name  The human-readable display name for this set of bins
        @param bins  A list of voltages we are allowed to output
        """
        super().__init__(name)
        self.bins = [float(b) for b in bins]
        self.bins.sort()

    def closest(self, v):
        """Quantize an input voltage to the closest bin. If two bins are equally close, choose the lower one.

        Our internal bins are sorted, so we can do a binary search for that sweet, sweet O(log(n)) efficiency

        @param v  A voltage in the range 0-10 to quantize
        @return   The closest voltage bin to @v
        """
        i = bisect_left(self.bins, v)
        if i == 0:
            return self.bins[0]
        if i == len(self.bins):
            return self.bins[-1]
        prev = self.bins[i - 1]
        next = self.bins[i + 1]
        if abs(v - next) < abs(v - prev):
            return next
        else:
            return prev


class DelayedOutput:
    """A class that handles setting a CV output on or after a given tick"""

    STATE_IDLE = 0
    STATE_WAITING = 1

    def __init__(self, cv):
        self.cv = cv
        self.state = self.STATE_IDLE

    def process(self, now=None):
        if self.state == self.STATE_IDLE:
            return

        if now is None:
            now = time.ticks_ms()

        if time.ticks_diff(now, self.target_tick) >= 0:
            self.cv.voltage(self.target_volts)
            self.state = self.STATE_IDLE

    def voltage_at(self, v, tick):
        """Specify the voltage we want to apply at the desired tick

        Call @process() to actually apply the voltage if needed

        @param v     The desired voltags (volts)
        @param tick  The tick (ms) we want the voltage to change at
        """
        self.state = self.STATE_WAITING
        self.target_volts = v
        self.target_tick = tick


class Sigma(EuroPiScript):
    """The main class for this script

    Handles all I/O, renders the UI
    """

    AIN_ROUTE_NONE = 0
    AIN_ROUTE_MEAN = 1
    AIN_ROUTE_STDEV = 2
    AIN_ROUTE_JITTER = 3
    AIN_ROUTE_BIN = 4
    N_AIN_ROUNTES = 5

    AIN_ROUTE_NAMES = [
        "None",
        "Mean",
        "Spread",
        "Jitter",
        "Bin"
    ]

    def __init__(self):
        super().__init__()

        self.outputs = [
            DelayedOutput(cv) for cv in cvs
        ]

        ## Voltage bins for bin mode
        self.voltage_bins = [
            ContinuousBin("Continuous"),
            VoltageBin("Bin 2", [0, 10]),
            VoltageBin("Bin 3", [0, 5, 10]),
            VoltageBin("Bin 6", [0, 2, 4, 6, 8, 10]),
            VoltageBin("Bin 7", [0, 1.7, 3.4, 5, 6.6, 8.3, 10]),
            VoltageBin("Bin 9", [0, 1.25, 2.5, 3.75, 5, 6.25, 7.5, 8.75, 10])
        ]

        # create bins for the quantized 1V/oct modes
        VOLTS_PER_TONE = 1.0 / 6
        VOLTS_PER_SEMITONE = 1.0 / 12
        VOLTS_PER_QUARTERTONE = 1.0 / 24
        tones = []
        semitones = []
        quartertones = []
        for oct in range(10):
            for tone in range(6):
                tones.append(oct + VOLTS_PER_TONE * tone)

            for semitone in range(12):
                semitones.append(oct + VOLTS_PER_SEMITONE * semitone)

            for quartertone in range(24):
                quartertones.append(oct + VOLTS_PER_QUARTERTONE * quartertone)

        self.voltage_bins.append(VoltageBin("Tone", tones))
        self.voltage_bins.append(VoltageBin("Semitone", semitones))
        self.voltage_bins.append(VoltageBin("Quartertone", quartertones))

        cfg = self.load_state_json()

        self.mean = cfg.get("mean", 0.5)
        self.stdev = cfg.get("stdev", 0.5)
        self.ain_route = cfg.get("ain_route", 0)
        self.voltage_bin = cfg.get("bin", 0)
        self.jitter = cfg.get("jitter", 0)

        # create the lockable knobs
        #  Note that this does mean _sometimes_ you'll need to sweep the knob all the way left/right
        #  to unlock it
        self.k1_bank = (
            KnobBank.builder(k1)
            .with_unlocked_knob("mean")
            .with_locked_knob("jitter", initial_percentage_value=cfg.get("jitter", 0.5))
            .build()
        )
        self.k2_bank = (
            KnobBank.builder(k2)
            .with_unlocked_knob("stdev")
            .with_locked_knob("bin", initial_percentage_value=int(self.voltage_bin / len(self.voltage_bins)))
            .build()
        )

        self.config_dirty = False
        self.output_dirty = False

        self.last_interaction_at = time.ticks_ms()
        self.screensaver = Screensaver()

        self.last_clock_at = time.ticks_ms()

        self.clock_duration_ms = 0

        @b1.handler
        def on_b1_rise():
            self.k1_bank.next()
            self.k2_bank.next()
            self.last_interaction_at = time.ticks_ms()

        @b1.handler_falling
        def on_b1_fall():
            self.k1_bank.next()
            self.k2_bank.next()
            self.config_dirty = True

        @b2.handler
        def on_b2_rise():
            self.ain_route = (self.ain_route + 1) % self.N_AIN_ROUNTES
            self.config_dirty = True
            self.last_interaction_at = time.ticks_ms()

        @din.handler
        def on_din_rise():
            self.output_dirty = True
            now = time.ticks_ms()
            self.clock_duration_ms = time.ticks_diff(now, self.last_clock_at)
            self.last_clock_at = now

    def save(self):
        """Save the current state to the persistence file"""
        self.config_dirty = False
        cfg = {
            "ain_route": self.ain_route,
            "mean": self.mean,
            "jitter": self.jitter,
            "stdev": self.stdev,
            "bin": self.voltage_bin,
        }
        self.save_state_json(cfg)

    def read_inputs(self):
        self.mean = self.k1_bank["mean"].percent()
        self.stdev = self.k2_bank["stdev"].percent()
        self.jitter = self.k1_bank["jitter"].percent()
        self.voltage_bin = int(self.k2_bank["bin"].percent() * len(self.voltage_bins))

        # Apply attenuation to our CV-controlled input
        if self.ain_route == self.AIN_ROUTE_MEAN:
            self.mean = self.mean * ain.percent()
        elif self.ain_route == self.AIN_ROUTE_STDEV:
            self.stdev = self.stdev * ain.percent()
        elif self.ain_route == self.AIN_ROUTE_JITTER:
            self.jitter = self.jitter * ain.percent()
        elif self.ain_route == self.AIN_ROUTE_BIN:
            self.voltage_bin = int(self.k2_bank["bin"].percent() * ain.percent() * len(self.voltage_bins))

        if self.voltage_bin == len(self.voltage_bins):
            self.voltage_bin = self.voltage_bin - 1  # keep the index in bounds if we reach 1.0

    def set_outputs(self, now):
        for cv in self.outputs:
            cv.process(now)

    def calculate_jitter(self, now):
        self.output_dirty = False

        for cv in self.outputs:
            if cv == self.outputs[0]:
                target_tick = now
            else:
                target_tick = time.ticks_add(now, int(abs(normal(mean = 0, stdev = self.jitter) * self.clock_duration_ms / 4)))

            x = normal(mean = self.mean * MAX_OUTPUT_VOLTAGE, stdev = self.stdev * 2)
            v = self.voltage_bins[self.voltage_bin].closest(x)
            cv.voltage_at(
                v,
                target_tick
            )

    def main(self):
        turn_off_all_cvs()

        self.ui_dirty = True

        DISPLAY_PRECISION = 100
        prev_mean = int(self.mean * DISPLAY_PRECISION)
        prev_stdev = int(self.stdev * DISPLAY_PRECISION)
        prev_jitter = int(self.jitter * DISPLAY_PRECISION)

        while True:
            now = time.ticks_ms()

            self.read_inputs()
            if self.output_dirty:
                self.calculate_jitter(now)
            self.set_outputs(now)

            new_mean = int(self.mean * DISPLAY_PRECISION)
            new_stdev = int(self.stdev * DISPLAY_PRECISION)
            new_jitter = int(self.jitter * DISPLAY_PRECISION)

            self.ui_dirty = (self.ui_dirty or
                self.config_dirty or
                new_mean != prev_mean or
                new_stdev != prev_stdev or
                new_jitter != prev_jitter
            )

            if self.ui_dirty:
                self.last_interaction_at = now

            prev_mean = new_mean
            prev_stdev = new_stdev
            prev_jitter = new_jitter

            if self.config_dirty:
                self.save()

            if time.ticks_diff(now, self.last_interaction_at) > self.screensaver.ACTIVATE_TIMEOUT_MS:
                self.screensaver.draw()
                last_interaction_at = time.ticks_add(now, -self.screensaver.ACTIVATE_TIMEOUT_MS*2)
            elif self.ui_dirty:
                self.ui_dirty = False
                oled.fill(0)
                oled.centre_text(f"""{self.mean:0.2f} {self.stdev:0.2f} {self.jitter:0.2f}
{self.voltage_bins[self.voltage_bin]}
CV: {self.AIN_ROUTE_NAMES[self.ain_route]}""")

if __name__ == "__main__":
    Sigma().main()
