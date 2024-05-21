#!/usr/bin/env python3
"""Convert incoming triggers to gates or gates to triggers

Also outputs a toggle input which changes state every time an incoming gate is received, or when either button is
pressed.

@author Chris Iverach-Brereton <ve4cib@gmail.com>
@year   2023
"""

import time

from europi import *
from europi_script import EuroPiScript
from math import sqrt

from experimental.screensaver import Screensaver

## Trigger outputs are 10ms long (rising/falling edges of gate signals)
TRIGGER_DURATION_MS = 10

def median(l):
    """Get the median value from an array

    This is a cheater median, as we always choose the lower value if the length is even
    """
    if len(l) == 0:
        return 0
    arr = [i for i in l]
    arr.sort()
    return arr[len(arr) // 2]

class MedianAnalogInput:
    """A wrapper for an analogue input (e.g. knob, ain) that provides additional smoothing & debouncing
    """

    ## How many samples do we use when reading the raw input?
    HW_SAMPLES = 500

    ## The number of samples in our median window
    WINDOW_SIZE = 5

    def __init__(self, analog_in):
        """Create the wrapper

        @param analog_in  The input we're wrapping
        """
        self.analog_in = analog_in

        self.samples = []

    def percent(self):
        """Read the hardware percentage and apply our additional smoothing

        Smoothing is done using a simple 5-window median filter
        """
        self.samples.append(self.analog_in.percent(self.HW_SAMPLES))

        if len(self.samples) > self.WINDOW_SIZE:
            self.samples.pop(0)

        return median(self.samples)


class GatesAndTriggers(EuroPiScript):
    def __init__(self):
        super().__init__()

        self.on_incoming_rise_start_time = 0
        self.on_incoming_fall_start_time = 0

        self.ain = MedianAnalogInput(ain)
        self.k1 = MedianAnalogInput(k1)
        self.k2 = MedianAnalogInput(k2)

        # assign each of the CV outputs to specific duties
        self.gate_out = cv1
        self.incoming_rise_out = cv2
        self.incoming_fall_out = cv3
        self.gate_fall_out = cv4
        self.toggle_out = cv5
        self.toggle_fall_out = cv6

        turn_off_all_cvs()

        self.last_rise_at = 0
        self.last_fall_at = 0
        self.force_toggle = False

        self.last_user_interaction_at = 0

        self.screensaver = Screensaver()

        @din.handler
        def on_din_rising():
            self.last_rise_at = time.ticks_ms()

        @din.handler_falling
        def on_din_falling():
            self.last_fall_at = time.ticks_ms()

        @b1.handler
        def on_b1_press():
            now = time.ticks_ms()
            self.last_rise_at = now
            self.last_user_interaction_at = now

        @b1.handler_falling
        def on_b1_release():
            self.last_fall_at = time.ticks_ms()

        @b2.handler
        def on_b2_press():
            self.force_toggle = True
            self.last_user_interaction_at = time.ticks_ms()

    def quadratic_knob(self, x):
        """Some magic math to give us a quadratic response on the knob percentage

        This gives us 50ms @ 0% and 1000ms @ 100% with greater precision at the higher end
        where the differences will be more noticeable

        @param x  The value of the knob in the range [0, 100]
        """
        MIN_GATE = 50
        MAX_GATE = 1000
        if x <= 0:
            return MIN_GATE

        return (MAX_GATE - MIN_GATE)/10 * sqrt(x) + MIN_GATE  # 10 = sqrt(x) at maximum value

    def main(self):
        ui_dirty = True
        gate_duration = 0
        gate_on = False
        gate_fall_at = 0
        toggle = False
        toggle_on = False
        toggle_fall_at = 0

        last_k1_percent = 0
        last_k2_percent = 0
        last_gate_duration = 0

        while(True):
            # read the knobs with higher samples
            # keep 1 decimal place
            k1_percent = round(self.k1.percent() * 100)         # 0-100
            k2_percent = round(self.k2.percent() * 100) / 100   # 0-1
            cv_percent = round(self.ain.percent() * 100) / 100  # 0-1

            gate_duration = max(
                round(self.quadratic_knob(k1_percent) + cv_percent * k2_percent * 2000),
                TRIGGER_DURATION_MS
            )

            # Refresh the GUI if the knobs have moved or the gate duration has changed
            ui_dirty = last_k1_percent != k1_percent or last_k2_percent != k2_percent or last_gate_duration != gate_duration

            now = time.ticks_ms()
            time_since_rise = time.ticks_diff(now, self.last_rise_at)
            time_since_fall = time.ticks_diff(now, self.last_fall_at)

            # CV1: gate output based on rising edge of din/b1
            if time_since_rise >= 0 and time_since_rise < gate_duration:
                self.gate_out.on()
                if not gate_on:
                    gate_on = True
                    toggle = not toggle
            elif gate_on:
                gate_on = False
                gate_fall_at = now
                self.gate_out.off()
            else:
                self.gate_out.off()

            # CV2: trigger output for the rising edge of din/b1
            if time_since_rise >= 0 and time_since_rise <= TRIGGER_DURATION_MS:
                self.incoming_rise_out.on()
            else:
                self.incoming_rise_out.off()

            # CV3: trigger output for falling edge if din/b1
            if time_since_fall >= 0 and time_since_fall <= TRIGGER_DURATION_MS:
                self.incoming_fall_out.on()
            else:
                self.incoming_fall_out.off()

            # CV4: trigger output for falling edge of cv1
            time_since_gate_fall = time.ticks_diff(now, gate_fall_at)
            if time_since_gate_fall >= 0 and time_since_gate_fall <= TRIGGER_DURATION_MS:
                self.gate_fall_out.on()
            else:
                self.gate_fall_out.off()

            # CV5: toggle output; flips state every time we get a rising edge on din/b1/b2
            if self.force_toggle:
                toggle = not toggle
                self.force_toggle = False
            if toggle:
                self.toggle_out.on()
                toggle_on = True
            elif not toggle and toggle_on:
                self.toggle_out.off()
                toggle_on = False
                toggle_fall_at = now
            else:
                self.toggle_out.off()

            # CV6: trigger output for falling edge of cv5
            time_since_toggle_fall = time.ticks_diff(now, toggle_fall_at)
            if time_since_toggle_fall >= 0 and time_since_toggle_fall <= TRIGGER_DURATION_MS:
                self.toggle_fall_out.on()
            else:
                self.toggle_fall_out.off()

            last_k1_percent = k1_percent
            last_k2_percent = k2_percent
            last_gate_duration = gate_duration

            if ui_dirty:
                self.last_user_interaction_at = now
                oled.centre_text(f"Gate: {gate_duration}ms")
                ui_dirty = False
            elif time.ticks_diff(now, self.last_user_interaction_at) > self.screensaver.ACTIVATE_TIMEOUT_MS:
                self.screensaver.draw()
                self.last_user_interaction_at = time.ticks_add(now, -self.screensaver.ACTIVATE_TIMEOUT_MS)


if __name__=="__main__":
    GatesAndTriggers().main()
