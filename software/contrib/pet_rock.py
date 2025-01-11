"""
A clone of Pet Rock by Jonah Senzel.

Tracks the phase of the moon using a realtime clock and generates
pseudo-random gate sequences based on the date & moon phase
"""

from europi import *
from europi_script import EuroPiScript

from framebuf import FrameBuffer, MONO_HLSB
import math
import random
import time

from experimental.a_to_d import AnalogReaderDigitalWrapper
from experimental.math_extras import rescale
from experimental.rtc import *


def randint(min, max):
    """
    Return a random integer in the range [min, max]
    """
    return int(random.random() * (max - min + 1) + min)


class Algo:
    """
    Generic algorithm for generating the gate sequences
    """

    CHANNEL_A = 1
    CHANNEL_B = 2

    def __init__(self, channel, weekday, cycle, continuity):
        """
        Child constructors must call this first

        Child constructors must initialize self.sequence by appending {0, 1} values to it

        @param channel  1 for channel A, 2 for channel B
        @param weekday  The current weekday 1-7 (M-Su)
        @param cycle  The current moon phase
        @param continuity  ???
        """

        self.channel = channel

        if channel == self.CHANNEL_A:
            self.gate_out = cv1
            self.inv_out = cv2
            self.eos_out = cv3
        else:
            self.gate_out = cv4
            self.inv_out = cv5
            self.eos_out = cv6

        self.weekday = weekday
        self.cycle = cycle
        self.continuity = continuity

        self.sequence = []
        self.index = 0

        self.state_dirty = False

    @staticmethod
    def map(x, in_min, in_max, out_min, out_max):
        # treat the output as inclusive
        out_max = out_max + 1
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def tick(self):
        """
        Advance the sequence
        """
        self.index = (self.index + 1 ) % len(self.sequence)
        self.state_dirty = True

    def set_outputs(self):
        """
        Set the outputs high/low as needed
        """
        if self.sequence[self.index]:
            self.gate_out.on()
            self.inv_out.off()
        else:
            self.gate_out.off()
            self.inv_out.on()

        if self.index == len(self.sequence) - 1:
            self.eos_out.on()

        self.state_dirty = False

    def outputs_off(self):
        self.gate_out.off()
        self.inv_out.off()
        self.eos_out.off()


class AlgoPlain(Algo):
    """
    The Red-mood algorithm
    """

    # swords
    mood_graphics = bytearray(b'\x00\x00\x00\x1f\x00\x00\x00!\x00\x00\x00A\x00\x00\x00\x81\x00\x00\x01\x01\x00\x00\x02\x02\x00\x00\x04\x04\x00\x00\x08\x08\x00\x00\x10\x10\x00\x00  \x00\x00@@\x00\x00\x80\x80\x00\x01\x01\x00\x00\x02\x02\x00\x04\x04\x04\x00\x04\x08\x08\x00\x06\x10\x10\x00\x07  \x00\x03\xc0@\x00\x01\xc0\x80\x00\x00\xe1\x00\x00\x00r\x00\x00\x00\xfc\x00\x00\x01\xdc\x00\x00\x03\x8e\x00\x00\x07\x07\x00\x00~\x03\xc0\x00|\x00\x00\x00|\x00\x00\x00|\x00\x00\x00|\x00\x00\x00\x00\x00\x00\x00')

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity)

        seqmax = 0

        if cycle == MoonPhase.NEW_MOON:
            seqmax = randint(5, 7)
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WANING_CRESCENT:
            seqmax = randint(4, 16)
        elif cycle == MoonPhase.FIRST_QUARTER or cycle == MoonPhase.THIRD_QUARTER:
            seqmax = Algo.map(continuity, 0, 100, 6, 12)
            seqmax = seqmax * self.channel  # channel B is twice as long as A
        elif cycle == MoonPhase.WAXING_GIBBOUS:
            seqmax = 12
        elif cycle == MoonPhase.WANING_GIBBOUS:
            seqmax = 16
        else:
            seqmax = 16

        # From Jonah S:
        # Randomly populate rhythm
        # this may seems weird/cheesy, but as I note in the manual - I decided to focus on
        # one and only one translated elements for the moon cycle, which is the length
        # relationship of A and B - I found through practice that the random population of
        # steps actually produces great results, the key is how many steps you use, and the
        # relationship between the 2 step lengths. The interesting difference is comparing
        # for example a pair of 8 step rhythms, vs a 7 step rhythm, and a 15 step rhythm
        # being played against each other - this is the "meta movement" of the rhythmic
        # flavor, in every algo/mood
        for i in range(seqmax):
            self.sequence.append(randint(0, 1))


class AlgoReich(Algo):
    """
    The Blue-mood algorithm
    """

    # cups
    mood_graphics = bytearray(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xfe?\xff\xff\xfc?\xff\xff\xfc\x1f\xff\xff\xf8\x0f\xff\xff\xf0\x07\xff\xff\xe0\x03\xff\xff\xc0\x01\xff\xff\x80\x00\x7f\xfe\x00\x00\x0f\xf0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x0f\xf0\x00\x00\x7f\xfe\x00\x01\xff\xff\x80\x03\xff\xff\xc0')

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity)

        if cycle == MoonPhase.NEW_MOON:
            seqmax = randint(3, 5)
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WAXING_CRESCENT:
            if channel == Algo.CHANNEL_A:
                seqmax = Algo.map(continuity, 0, 100, 3, 8)
            else:
                a = Algo.map(continuity, 0, 100, 3, 8)
                b = 0
                while b == 0 or b == a or b == a*2 or b*2 == a:
                    b = randint(3, 8)

                seqmax = b
        elif cycle == MoonPhase.FIRST_QUARTER or cycle == MoonPhase.THIRD_QUARTER:
            seqmax = Algo.map(continuity, 0, 100, 5, 9)
            seqmax = seqmax * channel  # B is double A
        elif cycle == MoonPhase.WAXING_GIBBOUS or cycle == MoonPhase.WANING_GIBBOUS:
            seqmax = Algo.map(continuity, 0, 100, 4, 8)
        else:
            seqmax = 8

        seqDensity=50
        for i in range(seqmax):
            if randint(0, 99) < seqDensity:
                self.sequence.append(1)
            else:
                self.sequence.append(0)

        empty = True
        for i in range(len(self.sequence)):
            if self.sequence[i] == 1:
                empty = False
        if empty:
            self.sequence[randint(0, len(self.sequence)-1)] = 1


class AlgoSparse(Algo):
    """
    The Yellow-mood algorithm
    """

    # wands/clubs
    mood_graphics = bytearray(b'\x00\x07\xe0\x00\x00\x0f\xf0\x00\x00\x1f\xf8\x00\x00?\xfc\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x0f\xff\xff\xf0\x1f\xff\xff\xf8?\xff\xff\xfc\x7f\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xfb\xdf\xfe?\xf3\xcf\xfc\x1f\xe3\xc7\xf8\x0f\xc3\xc3\xf0\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x07\xe0\x00\x00\x0f\xf0\x00\x00\x1f\xf8\x00\x00?\xfc\x00\x00\x7f\xfe\x00')

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity)

        if cycle == MoonPhase.NEW_MOON:
            seqmax = randint(10, 19)
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WANING_CRESCENT:
            seqmax = randint(15, 30)
        elif cycle == MoonPhase.FIRST_QUARTER:
            if channel == Algo.CHANNEL_A:
                seqmax = 32
            else:
                seqmax = 64
        elif cycle == MoonPhase.THIRD_QUARTER:
            if channel == Algo.CHANNEL_A:
                seqmax = 24
            else:
                seqmax = 48
        elif cycle == MoonPhase.WAXING_GIBBOUS:
            seqmax = 32
        elif cycle == MoonPhase.WANING_GIBBOUS:
            seqmax = 24
        else:
            seqmax = 64

        densityPercent = 10

        for i in range(seqmax):
            self.sequence.append(0)

        seedStepInd = randint(0, seqmax - 1)
        self.sequence[seedStepInd] = 1

        for i in range(seqmax):
            if randint(0, 99) < densityPercent:
                self.sequence[i] = 1


class AlgoVari(Algo):
    """
    The Green-mood algorithm
    """

    # pentacles
    mood_graphics = bytearray(b'\x00\x07\xe0\x00\x009\x9c\x00\x00\xc1\x83\x00\x01\x01\x80\x80\x02\x02@@\x04\x02@ \x08\x02@\x10\x10\x04 \x08 \x04 \x04 \x04 \x04@\x08\x10\x02\x7f\xff\xff\xfeP\x08\x10\n\x88\x10\x08\x11\x84\x10\x08!\x83\x10\x08\xc1\x80\xa0\x05\x01\x80`\x06\x01\x800\x0c\x01@H\x12\x02@Fb\x02@A\x82\x02 \x81\x81\x04 \x86a\x04\x10\x88\x11\x08\t0\x0c\x90\x05@\x02\xa0\x03\x80\x01\xc0\x01\x00\x00\x80\x00\xc0\x03\x00\x008\x1c\x00\x00\x07\xe0\x00')

    def __init__(self, channel, weekday, cycle, continuity):
        super().__init__(channel, weekday, cycle, continuity)

        if cycle == MoonPhase.NEW_MOON:
            seqmax = randint(3, 19)
            repeats = 3
        elif cycle == MoonPhase.WAXING_CRESCENT or cycle == MoonPhase.WANING_CRESCENT:
            seqmax = randint(8, 12)
            repeats = randint(3, 6)
        elif cycle == MoonPhase.FIRST_QUARTER or cycle == MoonPhase.THIRD_QUARTER:
            seqmax = 8
            if channel == Algo.CHANNEL_A:
                repeats = 4
            else:
                repeats = 8
        elif cycle == MoonPhase.WAXING_GIBBOUS or cycle == MoonPhase.WANING_GIBBOUS:
            seqmax = 16
            repeats = 4
        else:
            seqmax = 12
            repeats = 3

        seq_a = []
        seq_b = []
        for i in range(seqmax):
            r = randint(0, 1)
            seq_a.append(r)
            seq_b.append(r)

        for i in range(seqmax-1, -1, -1):
            j = randint(0, i)

            tmp = seq_b[i]
            seq_b[i] = seq_b[j]
            seq_b[j] = i

        # the whole sequence is r * [seq_a] + r * [seq_b]
        for r in range(repeats):
            for n in seq_a:
                self.sequence.append(n)
        for r in range(repeats):
            for n in seq_b:
                self.sequence.append(n)


class AlgoBlocks(Algo):
    """
    One of the unimplemented algorithms in the original firmware
    """

    # hearts
    mood_graphics = bytearray(b'\x07\xe0\x07\xe0\x1f\xf8\x1f\xf8?\xfc?\xfc\x7f\xfe\x7f\xfe\x7f\xfe\x7f\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xfe?\xff\xff\xfc\x1f\xff\xff\xf8\x1f\xff\xff\xf8\x0f\xff\xff\xf0\x07\xff\xff\xe0\x07\xff\xff\xe0\x03\xff\xff\xc0\x01\xff\xff\x80\x01\xff\xff\x80\x00\xff\xff\x00\x00\x7f\xfe\x00\x00\x7f\xfe\x00\x00?\xfc\x00\x00\x1f\xf8\x00\x00\x1f\xf8\x00\x00\x0f\xf0\x00\x00\x07\xe0\x00\x00\x07\xe0\x00\x00\x03\xc0\x00\x00\x01\x80\x00')


class AlgoCulture(Algo):
    """
    One of the unimplemented algorithms in the original firmware
    """

    # spades
    mood_graphics = bytearray(b'\x00\x01\x80\x00\x00\x03\xc0\x00\x00\x07\xe0\x00\x00\x0f\xf0\x00\x00\x1f\xf8\x00\x00?\xfc\x00\x00\x7f\xfe\x00\x00\xff\xff\x00\x01\xff\xff\x80\x03\xff\xff\xc0\x07\xff\xff\xe0\x0f\xff\xff\xf0\x1f\xff\xff\xf8?\xff\xff\xfc\x7f\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xfe\x7f\xff\xff\xfe?\xfd\xbf\xfc\x1f\xf9\x9f\xf8\x07\xe1\x87\xe0\x00\x01\x80\x00\x00\x01\x80\x00\x00\x01\x80\x00\x00\x07\xe0\x00\x00\x1f\xf8\x00\x00?\xfc\x00')


class AlgoOver(Algo):
    """
    One of the unimplemented algorithms in the original firmware
    """

    # diamonds
    mood_graphics = bytearray(b'\x00\x01\x80\x00\x00\x01\x80\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x07\xe0\x00\x00\x07\xe0\x00\x00\x0f\xf0\x00\x00\x0f\xf0\x00\x00\x1f\xf8\x00\x00\x1f\xf8\x00\x00?\xfc\x00\x00?\xfc\x00\x00\x7f\xfe\x00\x00\xff\xff\x00\x03\xff\xff\xc0\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x03\xff\xff\xc0\x00\xff\xff\x00\x00\x7f\xfe\x00\x00?\xfc\x00\x00?\xfc\x00\x00\x1f\xf8\x00\x00\x1f\xf8\x00\x00\x0f\xf0\x00\x00\x0f\xf0\x00\x00\x07\xe0\x00\x00\x07\xe0\x00\x00\x03\xc0\x00\x00\x03\xc0\x00\x00\x01\x80\x00\x00\x01\x80\x00')


class AlgoWonk(Algo):
    """
    One of the unimplemented algorithms in the original firmware
    """

    # shields
    mood_graphics = bytearray(b'\xff\xff\xff\xff\x9f\xff\xff\xff\x8f\xff\xe0?\x87\xff\xf0\x7f\x83\xff\xb8\xef\xc1\xff\x98\xcf\xe0\xff\x80\x0f\xf0\x7f\x80\x0f\xf8?\x80\x0f\xfc\x1f\x98\xcf\xfe\x0f\xb8\xef\xff\x07\xf0\x7f\xff\x83\xe0?\xff\xc1\xff\xff\xff\xe0\xff\xff\xff\xf0\x7f\xff\xff\xf8?\xff\x7f\xfc\x1f\xfe?\xfe\x0f\xfc\x1f\xff\x07\xf8\x0f\xff\x83\xf0\x07\xff\xc1\xe0\x03\xff\xe0\xc0\x01\xff\xf0\x80\x00\xff\xf9\x00\x00\x7f\xfe\x00\x00?\xfc\x00\x00\x1f\xf8\x00\x00\x0f\xf0\x00\x00\x07\xe0\x00\x00\x03\xc0\x00\x00\x01\x80\x00')


class MoonPhase:
    """
    Calculates the current moon phase
    """

    NEW_MOON = 0
    WAXING_CRESCENT = 1
    FIRST_QUARTER = 2
    WAXING_GIBBOUS = 3
    FULL_MOON = 4
    WANING_GIBBOUS = 5
    THIRD_QUARTER = 6
    WANING_CRESCENT = 7

    moon_phase_images = [
        bytearray(b'\x00\x07\xc0\x00\x000\x0c\x00\x00\x80\x01\x00\x03\x00\x00\xc0\x04\x00\x00 \x08\x00\x00\x10\x00\x00\x00\x00\x10\x00\x00\x08 \x00\x00\x04\x00\x00\x00\x00@\x00\x00\x02@\x00\x00\x02\x00\x00\x00\x00\x80\x00\x00\x01\x80\x00\x00\x01\x80\x00\x00\x01\x80\x00\x00\x01\x80\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x02@\x00\x00\x02\x00\x00\x00\x00 \x00\x00\x04\x10\x00\x00\x08\x10\x00\x00\x08\x08\x00\x00\x10\x04\x00\x00 \x01\x00\x00\x80\x00\x80\x01\x00\x000\x0c\x00\x00\x07\xc0\x00'),
        bytearray(b'\x00\x0b\xe0\x00\x000\xfe\x00\x00\x80\x1f\x00\x01\x00\x0f\xc0\x04\x00\x03\xe0\x00\x00\x01\xf0\x00\x00\x00\xf8\x10\x00\x00\xf8 \x00\x00|\x00\x00\x00>@\x00\x00>@\x00\x00>\x00\x00\x00\x1e\x00\x00\x00\x1f\x80\x00\x00\x1f\x00\x00\x00\x1f\x80\x00\x00\x1f\x00\x00\x00\x1f\x00\x00\x00\x1f\x00\x00\x00\x1e@\x00\x00>@\x00\x00>\x00\x00\x00< \x00\x00|\x10\x00\x00\xf8\x00\x00\x00\xf8\x08\x00\x01\xf0\x00\x00\x03\xe0\x01\x00\x0f\xc0\x00\x80\x1f\x00\x000\xfc\x00\x00\x0b\xe0\x00'),
        bytearray(b'\x00\x02\xe0\x00\x000\xfe\x00\x00\x80\xff\x00\x01\x00\xff\xc0\x04\x00\xff\xe0\x00\x00\xff\xf0\x00\x00\xff\xf8\x10\x00\xff\xf8 \x00\xff\xfc\x00\x00\xff\xfe@\x00\xff\xfe@\x00\xff\xfe\x00\x00\xff\xfe\x00\x00\xff\xff\x80\x00\xff\xff\x00\x00\xff\xff\x80\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xff\x00\x00\xff\xfe@\x00\xff\xfe@\x00\xff\xfe\x00\x00\xff\xfc \x00\xff\xfc\x10\x00\xff\xf8\x00\x00\xff\xf8\x08\x00\xff\xf0\x00\x00\xff\xe0\x01\x00\xff\xc0\x00\x80\xff\x00\x000\xfc\x00\x00\x02\xe0\x00'),
        bytearray(b'\x00\x02\x90\x00\x000\xfc\x00\x00\x83\xff\x00\x01\x07\xff\xc0\x04\x0f\xff\xe0\x00\x1f\xff\xf0\x00?\xff\xf8\x10\x7f\xff\xf8 \x7f\xff\xfc\x00\xff\xff\xfe@\xff\xff\xfe@\xff\xff\xfe\x01\xff\xff\xfe\x01\xff\xff\xff\x81\xff\xff\xff\x01\xff\xff\xff\x81\xff\xff\xff\x01\xff\xff\xff\x01\xff\xff\xff\x01\xff\xff\xfe@\xff\xff\xfe@\xff\xff\xfe\x00\xff\xff\xfc \x7f\xff\xfc\x10\x7f\xff\xf8\x00?\xff\xf8\x08\x1f\xff\xf0\x00\x0f\xff\xe0\x01\x07\xff\xc0\x00\x83\xff\x00\x000\xfc\x00\x00\x02\x90\x00'),
        bytearray(b'\x00\x07\xc0\x00\x00?\xfc\x00\x00\xff\xff\x00\x03\xff\xff\xc0\x07\xff\xff\xe0\x0f\xff\xff\xf0\x0f\xff\xff\xf0\x1f\xff\xff\xf8?\xff\xff\xfc?\xff\xff\xfc\x7f\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xfe\x7f\xff\xff\xfe?\xff\xff\xfc?\xff\xff\xfc\x1f\xff\xff\xf8\x1f\xff\xff\xf8\x0f\xff\xff\xf0\x07\xff\xff\xe0\x01\xff\xff\x80\x00\xff\xff\x00\x00?\xfc\x00\x00\x07\xc0\x00'),
        bytearray(b'\x00\t\x80\x00\x00\x7f\x0c\x00\x00\xff\xc1\x00\x03\xff\xe0\x80\x07\xff\xf0 \x0f\xff\xf8\x00\x1f\xff\xfc\x00\x1f\xff\xfe\x08?\xff\xfe\x04\x7f\xff\xff\x00\x7f\xff\xff\x02\x7f\xff\xff\x02\xff\xff\xff\x80\x7f\xff\xff\x80\xff\xff\xff\x81\xff\xff\xff\x81\xff\xff\xff\x80\xff\xff\xff\x81\xff\xff\xff\x80\x7f\xff\xff\x80\x7f\xff\xff\x02\x7f\xff\xff\x02?\xff\xff\x00?\xff\xfe\x04\x1f\xff\xfe\x08\x1f\xff\xfc\x00\x0f\xff\xf8\x00\x07\xff\xf0\x00\x03\xff\xe0\x80\x00\xff\xc1\x00\x00\x7f\x0c\x00\x00\t\x80\x00'),
        bytearray(b'\x00\x0b\x80\x00\x00\x7f\x0c\x00\x00\xff\x01\x00\x03\xff\x00\x80\x07\xff\x00 \x0f\xff\x00\x00\x1f\xff\x00\x00\x1f\xff\x00\x08?\xff\x00\x04\x7f\xff\x00\x00\x7f\xff\x00\x02\x7f\xff\x00\x02\xff\xff\x00\x00\x7f\xff\x00\x00\xff\xff\x00\x01\xff\xff\x00\x01\xff\xff\x00\x00\xff\xff\x00\x01\xff\xff\x00\x00\x7f\xff\x00\x00\x7f\xff\x00\x02\x7f\xff\x00\x02?\xff\x00\x00?\xff\x00\x04\x1f\xff\x00\x08\x1f\xff\x00\x00\x0f\xff\x00\x00\x07\xff\x00\x00\x03\xff\x00\x80\x00\xff\x01\x00\x00\x7f\x0c\x00\x00\x0b\x80\x00'),
        bytearray(b'\x00\x0b\xe0\x00\x00\x7f\x0c\x00\x00\xf8\x01\x00\x03\xf0\x00\x80\x07\xc0\x00 \x0f\x80\x00\x00\x1f\x00\x00\x00\x1f\x00\x00\x08>\x00\x00\x04|\x00\x00\x00|\x00\x00\x02|\x00\x00\x02\xf8\x00\x00\x00x\x00\x00\x00\xf8\x00\x00\x01\xf8\x00\x00\x01\xf8\x00\x00\x00\xf8\x00\x00\x01\xf8\x00\x00\x00x\x00\x00\x00|\x00\x00\x02|\x00\x00\x02<\x00\x00\x00>\x00\x00\x04\x1f\x00\x00\x08\x1f\x00\x00\x00\x0f\x80\x00\x00\x07\xc0\x00\x00\x03\xf0\x00\x80\x00\xf8\x01\x00\x00\x7f\x0c\x00\x00\x0b\xe0\x00'),
    ]

    @staticmethod
    def calculate_days_since_new_moon(date):
        """
        Calculate the number of days since a known full moon

        @see https://www.subsystems.us/uploads/9/8/9/4/98948044/moonphase.pdf

        @param date  The current UTC DateTime
        """
        if date.year < 2000:
            raise ValueError(f"Date out of range; check your RTC")

        y = date.year
        m = date.month
        d = date.day

        if m == Month.JANUARY or m == Month.FEBRUARY:
            y = y - 1
            m = m + 12

        a = math.floor(y/100)
        b = math.floor(a/4)
        c = 2 - a + b
        e = math.floor(365.25 * (y + 4716))
        f = math.floor(30.6001 * (m + 1))
        jd = c + d + e + f - 1524.5

        days_since_new_moon = jd - 2451549.5

        return days_since_new_moon

    @staticmethod
    def calculate_phase(date):
        """
        Calculate the current moon phase

        @param date  The current UTC DateTime
        """
        days_since_new_moon = MoonPhase.calculate_days_since_new_moon(date)

        yesterday_new_moons = (days_since_new_moon - 1) / 29.53
        today_new_moons = days_since_new_moon / 29.53
        tomorrow_new_moons = (days_since_new_moon + 1) / 29.53

        # we always want 1 day assigned to new, first quarter, full, and third quarter
        # so use yesterday, today, and tomorrow as a 3-day window
        # if tomorrow is on one side of the curve and yesterday was the other, treat today
        # as the "special" phase

        yesterday_fraction = yesterday_new_moons % 1
        today_fraction = today_new_moons % 1
        tomorrow_fraction = tomorrow_new_moons % 1

        if yesterday_fraction > 0.75 and tomorrow_fraction < 0.25:
            return MoonPhase.NEW_MOON
        elif yesterday_fraction < 0.25 and tomorrow_fraction > 0.25:
            return MoonPhase.FIRST_QUARTER
        elif yesterday_fraction < 0.5 and tomorrow_fraction > 0.5:
            return MoonPhase.FULL_MOON
        elif yesterday_fraction < 0.75 and tomorrow_fraction > 0.75:
            return MoonPhase.THIRD_QUARTER
        elif today_fraction == 0.0:
            return MoonPhase.NEW_MOON
        elif today_fraction < 0.25:
            return MoonPhase.WAXING_CRESCENT
        elif today_fraction == 0.25:
            return MoonPhase.FIRST_QUARTER
        elif today_fraction < 0.5:
            return MoonPhase.WAXING_GIBBOUS
        elif today_fraction == 0.5:
            return MoonPhase.FULL_MOON
        elif today_fraction < 0.75:
            return MoonPhase.WANING_GIBBOUS
        elif today_fraction == 0.75:
            return MoonPhase.THIRD_QUARTER
        else:
            return MoonPhase.WANING_CRESCENT


class Mood:
    """
    The algorithm's "mood"

    Mood is one of 4 colours, which rotates every moon cycle
    """

    MOOD_RED = 0
    MOOD_BLUE = 1
    MOOD_YELLOW = 2
    MOOD_GREEN = 3

    N_MOODS = 4

    @staticmethod
    def calculate_mood(date):
        """
        Calculate the current mood

        @param date  The current UTC DateTime
        """
        days_since_new_moon = MoonPhase.calculate_days_since_new_moon(date)
        cycles = math.floor(days_since_new_moon / 29.53)

        return cycles % Mood.N_MOODS

    @staticmethod
    def mood_algorithm(date):
        """
        Get the algorithm for the current mood

        @param date  The current UTC DateTime
        """
        mood = Mood.calculate_mood(date)
        if mood == Mood.MOOD_RED:
            return AlgoPlain
        elif mood == Mood.MOOD_BLUE:
            return AlgoReich
        elif mood == Mood.MOOD_YELLOW:
            return AlgoSparse
        else:
            return AlgoVari


class IntervalTimer:
    """
    Uses ticks_ms and ticks_diff to fire a callback at fixed-ish intervals
    """

    MIN_INTERVAL = 10
    MAX_INTERVAL = 500

    def __init__(self, speed_knob, rise_cb=lambda: None, fall_cb=lambda: None):
        self.interval_ms = 0
        self.last_tick_at = time.ticks_ms()

        self.speed_knob = speed_knob

        self.rise_callback = rise_cb
        self.fall_callback = fall_cb

        self.next_rise = True

        self.update_interval()

    def update_interval(self):
        DEADZONE = 0.1
        p = self.speed_knob.percent()
        if p <= DEADZONE:
            # disable the timer for the first 10% of travel so we have an easy-off
            # for external clocking
            self.interval_ms = 0
        else:
            p = 1.0 - rescale(p, DEADZONE, 1, 0, 1)
            self.interval_ms = round(rescale(p, 0, 1, self.MIN_INTERVAL, self.MAX_INTERVAL))

    def tick(self):
        # kick out immediately if the timer is off
        if self.interval_ms <= 0:
            return

        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_tick_at) >= self.interval_ms:
            self.last_tick_at = now

            if self.next_rise:
                self.rise_callback()
                self.next_rise = False
            else:
                self.fall_callback()
                self.next_rise = True


class PetRock(EuroPiScript):

    def __init__(self):
        super().__init__()

        self.seed_offset = 1
        self.generate_sequences()

        self.din2 = AnalogReaderDigitalWrapper(
            ain,
            cb_rising = self.on_channel_b_trigger,
            cb_falling = self.on_channel_b_fall
        )
        b2.handler(self.on_channel_b_trigger)
        b2.handler_falling(self.on_channel_b_fall)
        self.timer_b = IntervalTimer(
            k2,
            rise_cb=self.on_channel_b_trigger,
            fall_cb=self.on_channel_b_fall
        )

        din.handler(self.on_channel_a_trigger)
        din.handler_falling(self.on_channel_a_fall)
        b1.handler(self.on_channel_a_trigger)
        b1.handler_falling(self.on_channel_a_fall)
        self.timer_a = IntervalTimer(
            k1,
            rise_cb=self.on_channel_a_trigger,
            fall_cb=self.on_channel_a_fall
        )

    def generate_sequences(self):
        continuity = randint(0, 99)

        now = clock.utcnow()
        if now.weekday is None:
            now.weekday = 0

        cycle = MoonPhase.calculate_phase(now)

        today_seed = now.day + now.month + now.year + self.seed_offset
        random.seed(today_seed)

        self.sequence_a = Mood.mood_algorithm(now)(Algo.CHANNEL_A, now.weekday, cycle, continuity)
        self.sequence_b = Mood.mood_algorithm(now)(Algo.CHANNEL_B, now.weekday, cycle, continuity)

        self.last_generation_at = clock.localnow()

    def on_channel_a_trigger(self):
        self.sequence_a.tick()

    def on_channel_a_fall(self):
        self.sequence_a.outputs_off()

    def on_channel_b_trigger(self):
        self.sequence_b.tick()

    def on_channel_b_fall(self):
        self.sequence_b.outputs_off()

    def draw(self, local_time):
        oled.fill(0)

        if local_time.weekday:
            oled.text(Weekday.NAME[local_time.weekday][0:3].upper(), OLED_WIDTH - CHAR_WIDTH * 3, 0, 1)

        oled.text(f"{local_time.hour:02}:{local_time.minute:02}", OLED_WIDTH - CHAR_WIDTH * 5, OLED_HEIGHT - CHAR_HEIGHT, 1)

        moon_phase = MoonPhase.calculate_phase(clock.utcnow())
        moon_img = FrameBuffer(MoonPhase.moon_phase_images[moon_phase], 32, 32, MONO_HLSB)
        oled.blit(moon_img, 0, 0)

        mood_img = FrameBuffer(self.sequence_a.mood_graphics, 32, 32, MONO_HLSB)
        oled.blit(mood_img, 34, 0)

        oled.show()

    def main(self):
        self.draw(clock.localnow())
        last_draw_at = clock.localnow()

        while True:
            self.din2.update()

            self.timer_a.update_interval()
            self.timer_b.update_interval()

            self.timer_a.tick()
            self.timer_b.tick()

            local_time = clock.localnow()

            ui_dirty = local_time.minute != last_draw_at.minute

            # if the day has rolled over, generate new sequences and mark them as dirty
            # so we'll continue playing
            if local_time.day != self.last_generation_at.day:
                self.generate_sequences()
                self.sequence_a.state_dirty = True
                self.sequence_b.state_dirty = True

                ui_dirty = True

            if self.sequence_a.state_dirty:
                self.sequence_a.set_outputs()

            if self.sequence_b.state_dirty:
                self.sequence_b.set_outputs()

            if ui_dirty:
                self.draw(local_time)
