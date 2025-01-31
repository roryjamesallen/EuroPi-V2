from europi import *
from europi_script import EuroPiScript

from experimental.knobs import *

morse_alphabet = {
    None: "",
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
}

valid_letters = [
    None,
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
]

class Morse(EuroPiScript):
    dot_high_out = cv1
    dot_high_latched_out = cv2
    dot_low_out = cv4
    dot_low_latched_out = cv5
    end_of_letter_out = cv3
    end_of_word_out = cv6

    def __init__(self):
        super().__init__()

        default_letters = [None] * 16
        saved_cfg = self.load_state_json()
        self.letters = saved_cfg.get("letters", default_letters)

        # the letter the user is hovering over
        # may be -1 to indicate no letter
        # otherwise must be in range [0, 16)
        self.hover_letter = -1

        # create a lockable bank of knobs so we can edit letters
        # without accidentally changing them
        builder = KnobBank.builder(k2).with_unlocked_knob("-1")
        for i in range(len(self.letters)):
            percent = valid_letters.index(self.letters[i]) / len(valid_letters)
            builder = builder.with_locked_knob(str(i), initial_percentage_value=percent)
        self.k2_bank = builder.build()

        self.gate_recvd = False
        self.sequence_counter = 0

        @b1.handler
        def on_b1_press():
            n = self.hover_letter - 1
            if n < -1:
                # wrap around
                n = len(self.letters) - 1
            self.hover_letter = n
            self.k2_bank.set_current(str(self.hover_letter))

        @b2.handler
        def on_b2_press():
            n = self.hover_letter + 1
            if n >= len(self.letters):
                # wrap around
                n = -1
            self.hover_letter = n
            self.k2_bank.set_current(str(self.hover_letter))

        @din.handler
        def on_din_rise():
            self.gate_recvd = True

        @din.handler_falling
        def on_din_fall():
            # turn off the unlatched CVs
            self.dot_low_out.off()
            self.dot_high_out.off()
            self.end_of_letter_out.off()
            self.end_of_word_out.off()

    def save_state(self):
        w = ""
        for l in self.letters:
            if l is not None:
                w = w + l

        cfg = {
            "word": w
        }
        self.save_state_json(cfg)

    def expand_sequence(self):
        """
        Expand the more representation to a boolean sequence

        We treat "." as True and "-" as False
        """
        seq = []
        for ch in self.letters:
            if ch is not None:
                for bit in morse_alphabet[ch]:
                    if bit == ".":
                        seq.append(True)
                    else:
                        seq.append(False)
        return seq

    def get_letter_ends(self):
        seq = []
        n = 0
        for ch in self.letters:
            if ch is not None:
                n += len(morse_alphabet[ch])
                seq.append(n)
        return seq

    def draw(self):
        oled.centre_text(f"{self.hover_letter}\n{self.k2_bank.current.percent():0.2f}")

    def main(self):
        while True:
            self.draw()

            sequence = self.expand_sequence()
            end_of_letters = self.get_letter_ends()
            if len(sequence) == 0:
                turn_off_all_cvs()
                continue

            # kick out if there's no gate to process
            if not self.gate_recvd:
                continue

            self.gate_recvd = False

            # if we've modified the sequence, check for overflow
            if self.sequence_counter >= len(sequence):
                self.sequence_counter = 0

            # play the sequence
            if sequence[self.sequence_counter]:
                self.dot_high_out.on()
                self.dot_high_latched_out.on()
                self.dot_low_out.off()
                self.dot_low_latched_out.off()
            else:
                self.dot_high_out.off()
                self.dot_high_latched_out.off()
                self.dot_low_out.on()
                self.dot_low_latched_out.on()

            # increment
            self.sequence_counter += 1

            # check for end of letter
            if self.sequence_counter in end_of_letters:
                self.end_of_letter_out.on()

            # check for end of word
            if self.sequence_counter == len(sequence):
                self.end_of_word_out.on()






if __name__ == "__main__":
    Morse().main()
