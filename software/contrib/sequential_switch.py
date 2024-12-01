"""Sequential switch for the EuroPi

    @author Chris Iverach-Brereton <ve4cib@gmail.com>
    @date   2023-02-13
"""

from europi import *
from europi_script import EuroPiScript

from experimental.settings_menu import *
from experimental.screensaver import OledWithScreensaver

import time
import random

## Move in order 1>2>3>4>5>6>1>2>...
MODE_SEQUENTIAL=0

## Move in order 1>6>5>4>3>2>1>6>...
MODE_REVERSE=1

## Move in order 1>2>3>4>5>6>5>4>...
MODE_PINGPONG=2

## Pick a random output, which can be the same as the one we're currently using
MODE_RANDOM=3

## Instead of a traditional sequential switch, treat the outputs like a s&h shift register
#
#  CV1 will contain the latest s&h reading, with CV2-6 outputting increasingly old readings
MODE_SHIFT=4

## How many milliseconds of idleness do we need before we trigger the screensaver?
#
#  =20 minutes
SCREENSAVER_TIMEOUT_MS = 1000 * 60 * 20

ssoled = OledWithScreensaver()


class SequentialSwitchDisplay(MenuItem):
    """
    A menu item that displays the current state of the sequential switch
    """
    def __init__(self, sequential_switch, parent=None, children=None):
        super().__init__(parent=parent, children=children)

        self.sequential_switch = sequential_switch

    def draw(self, oled=ssoled):
        if self.sequential_switch.mode.value == MODE_SHIFT:
            BAR_WIDTH = OLED_WIDTH // 6
            for i in range(self.sequential_switch.num_outputs.value):
                h = max(1, int(self.sequential_switch.shift_register[i] / MAX_OUTPUT_VOLTAGE * OLED_HEIGHT))
                oled.fill_rect(BAR_WIDTH * i + 1, OLED_HEIGHT - h, BAR_WIDTH-2, h, 1)
        else:
            # Show all 6 outputs as a string on 2 lines to mirror the panel
            switches = ""
            for i in range(2):
                for j in range(3):
                    out_no = i*3 + j
                    if out_no < self.sequential_switch.num_outputs.value:
                        # output is enabled; is it hot?
                        if self.sequential_switch.current_output == out_no:
                            switches = switches + " [*] "
                        else:
                            switches = switches + " [ ] "
                    else:
                        # output is disabled; mark it with .
                        switches = switches + "  .  "

                switches = switches + "\n"

            oled.centre_text(switches, auto_show=False)


class SequentialSwitch(EuroPiScript):
    """The main workhorse of the whole module

    Copies the analog input to one of the 6 outputs, cycling which output
    whenever a trigger is received
    """

    def __init__(self):
        super().__init__()

        @din.handler
        def on_rising_clock():
            self.on_trigger()

        @b1.handler
        def on_b1_press():
            ssoled.notify_user_interaction()
            self.active_screen.on_button1()

        self.mode = SettingMenuItem(
            config_point = ChoiceConfigPoint(
                "mode",
                [
                    MODE_SEQUENTIAL,
                    MODE_REVERSE,
                    MODE_PINGPONG,
                    MODE_RANDOM,
                    MODE_SHIFT,
                ],
                MODE_SEQUENTIAL
            ),
            title="Mode",
            labels = {
                MODE_SEQUENTIAL: "Seq.",
                MODE_REVERSE: "Rev.",
                MODE_PINGPONG: "P-P",
                MODE_RANDOM: "Rand.",
                MODE_SHIFT: "Shift",
            },
        )

        self.num_outputs = SettingMenuItem(
            config_point = IntegerConfigPoint(
                "num_outs",
                2,
                6,
                6
            ),
            title="# Outputs",
        )

        self.menu = SettingsMenu(
            knob = k2,
            button = b2,
            short_press_cb = lambda: ssoled.notify_user_interaction(),
            long_press_cb = lambda: ssoled.notify_user_interaction(),
            menu_items = [
                SequentialSwitchDisplay(
                    self,
                    children = [
                        self.mode,
                        self.num_outputs,
                    ]
                )
            ]
        )
        self.menu.load_defaults(self._state_filename)

        # The index of the current outputs
        self.current_output = 0

        # For MODE_PINGPONG, this indicates the direction of travel
        # it will always be +1 or -1
        self.direction = 1

        ## The shift register we use as s&h in MODE_SHIFT
        self.shift_register = [0] * len(cvs)

    def on_trigger(self):
        """Handler for the rising edge of the input clock

        Also used for manually advancing the output on a button press
        """
        # to save on clock cycles, don't use modular arithmetic
        # instead just to integer math and handle roll-over manually
        next_out = self.current_output
        if self.mode.value == MODE_SEQUENTIAL:
            next_out = next_out + 1
        elif self.mode.value == MODE_REVERSE:
            next_out = next_out - 1
        elif self.mode.value == MODE_PINGPONG:
            next_out = next_out + self.direction
        else:
            next_out = random.randint(0, self.num_outputs.value-1)

        if next_out < 0:
            if self.mode.value == MODE_REVERSE:
                next_out = self.num_outputs.value-1
            else:
                next_out = -next_out
                self.direction = -self.direction
        elif next_out >= self.num_outputs.value:
            if self.mode.value == MODE_SEQUENTIAL:
                next_out = 0
            else:
                next_out = self.num_outputs.value-2
                self.direction = -self.direction

        self.current_output = next_out

        if self.mode.value == MODE_SHIFT:
            self.shift_register.pop(-1)
            self.shift_register.insert(0, ain.read_voltage())

    def main(self):
        """The main loop

        Connects event handlers for clock-in and button presses
        and runs the main loop
        """
        while True:
            ssoled.fill(0)
            self.menu.draw(ssoled)
            ssoled.show()

            if self.menu.settings_dirty:
                self.menu.save(self._state_filename)

            if self.mode.value == MODE_SHIFT:
                # CV1 gets the most-recent s&h output, all the others get older values
                for i in range(self.num_outputs.value):
                    cvs[i].voltage(self.shift_register[i])

                # turn off any unused outputs
                for i in range(self.num_outputs.value, len(cvs)):
                    cvs[i].off()
            else:
                # read the input and send it to the current output
                # all other outputs should be zero
                input_volts = ain.read_voltage()
                for i in range(len(cvs)):
                    if i == self.current_output:
                        cvs[i].voltage(input_volts)
                    else:
                        cvs[i].off()

if __name__ == "__main__":
    SequentialSwitch().main()
