from europi_config import europi_config

from framebuf import FrameBuffer, MONO_HLSB
from machine import I2C, Pin
import ssd1306
from ssd1306 import SSD1306_I2C


# Default font is 8x8 pixel monospaced font.
CHAR_WIDTH = 8
CHAR_HEIGHT = 8


# OLED component display dimensions.
OLED_WIDTH = europi_config.DISPLAY_WIDTH
OLED_HEIGHT = europi_config.DISPLAY_HEIGHT
OLED_I2C_SDA = europi_config.DISPLAY_SDA
OLED_I2C_SCL = europi_config.DISPLAY_SCL
OLED_I2C_CHANNEL = europi_config.DISPLAY_CHANNEL
OLED_I2C_FREQUENCY = europi_config.DISPLAY_FREQUENCY


class DummyDisplay:
    """A placeholder for the display that can be used if the display hardware is not connected"""

    def show(self):
        pass

    # The following are just wrappers for the functions in the Display class to allow 1:1 access
    # See europi.Display for documentation details

    def fill(self, color):
        pass

    def text(self, string, x, y, color=1):
        pass

    def centre_text(self, text, clear_first=True, auto_show=True):
        pass

    def line(self, x1, y1, x2, y2, color=1):
        pass

    def hline(self, x, y, length, color=1):
        pass

    def vline(self, x, y, length, color=1):
        pass

    def rect(self, x, y, width, height, color=1):
        pass

    def fill_rect(self, x, y, width, height, color=1):
        pass

    def blit(self, buffer, x, y):
        pass

    def scroll(self, x, y):
        pass

    def invert(self, color=1):
        pass

    def contrast(self, contrast):
        pass

    def pixel(self, x, y, color=1):
        pass


class Display(SSD1306_I2C):
    """A class for drawing graphics and text to the OLED.

    The OLED Display works by collecting all the applied commands and only
    updates the physical display when ``oled.show()`` is called. This allows
    you to perform more complicated graphics without slowing your program, or
    to perform the calculations for other functions, but only update the
    display every few steps to prevent lag.

    To clear the display, simply fill the display with the colour black by using ``oled.fill(0)``

    More explanations and tips about the the display can be found in the oled_tips file
    `oled_tips.md <https://github.com/Allen-Synthesis/EuroPi/blob/main/software/oled_tips.md>`_
    """

    def __init__(
        self,
        sda=OLED_I2C_SDA,
        scl=OLED_I2C_SCL,
        width=OLED_WIDTH,
        height=OLED_HEIGHT,
        channel=OLED_I2C_CHANNEL,
        freq=OLED_I2C_FREQUENCY,
    ):
        i2c = I2C(channel, sda=Pin(sda), scl=Pin(scl), freq=freq)
        self.width = width
        self.height = height

        if len(i2c.scan()) == 0:
            if not TEST_ENV:
                raise Exception(
                    "EuroPi Hardware Error:\nMake sure the OLED display is connected correctly"
                )
        super().__init__(self.width, self.height, i2c)
        self.rotate(europi_config.ROTATE_DISPLAY)

    def rotate(self, rotate):
        """Flip the screen from its default orientation

        @param rotate  True or False, indicating whether we want to flip the screen from its default orientation
        """
        # From a hardware perspective, the default screen orientation of the display _is_ rotated
        # But logically we treat this as right-way-up.
        if rotate:
            rotate = 0
        else:
            rotate = 1
        if not TEST_ENV:
            self.write_cmd(ssd1306.SET_COM_OUT_DIR | ((rotate & 1) << 3))
            self.write_cmd(ssd1306.SET_SEG_REMAP | (rotate & 1))

    def centre_text(self, text, clear_first=True, auto_show=True):
        """Display one or more lines of text centred both horizontally and vertically.

        @param text  The text to display
        @param clear_first  If true, the screen buffer is cleared before rendering the text
        @param auto_show  If true, oled.show() is called after rendering the text. If false, you must call oled.show() yourself
        """
        if clear_first:
            self.fill(0)
        # Default font is 8x8 pixel monospaced font which can be split to a
        # maximum of 4 lines on a 128x32 display, but the maximum_lines variable
        # is rounded down for readability
        lines = str(text).split("\n")
        maximum_lines = round(self.height / CHAR_HEIGHT)
        if len(lines) > maximum_lines:
            raise Exception("Provided text exceeds available space on oled display.")
        padding_top = (self.height - (len(lines) * (CHAR_HEIGHT + 1))) / 2
        for index, content in enumerate(lines):
            x_offset = int((self.width - ((len(content) + 1) * (CHAR_WIDTH - 1))) / 2) - 1
            y_offset = int((index * (CHAR_HEIGHT + 1)) + padding_top) - 1
            self.text(content, x_offset, y_offset)

        if auto_show:
            self.show()
