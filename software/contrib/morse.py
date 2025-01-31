from europi import *
from europi_script import EuroPiScript

BLANK_LETTER = "."

morse_alphabet = {
    BLANK_LETTER: "",
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
    BLANK_LETTER,
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

        default_letters = [BLANK_LETTER] * 16
        saved_cfg = self.load_state_json()
        self.letters = saved_cfg.get("letters", default_letters)

        # the index of the letter the user is hovering over
        self.hover_letter = 0

        self.ui_dirty = True
        self.gate_recvd = False
        self.sequence_counter = 0

        @b1.handler
        def on_b1_press():
            # advance the letter 1 place down
            idx = valid_letters.index(self.letters[self.hover_letter])
            idx = (idx - 1) % len(valid_letters)
            self.letters[self.hover_letter] = valid_letters[idx]
            self.ui_dirty = True

        @b2.handler
        def on_b2_press():
            # advance the letter 1 place up
            idx = valid_letters.index(self.letters[self.hover_letter])
            idx = (idx + 1) % len(valid_letters)
            self.letters[self.hover_letter] = valid_letters[idx]
            self.ui_dirty = True

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
        cfg = {
            "letters": self.letters
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
        top = OLED_HEIGHT // 2 - CHAR_HEIGHT // 2
        left = OLED_WIDTH // 2 - (CHAR_WIDTH * len(self.letters)) // 2

        oled.fill(0)

        w = ''
        for ch in self.letters:
            if ch is None:
                w = w + "."
            else:
                w = w + ch

        oled.text(
            w,
            left,
            top,
            1
        )

        oled.line(
            left + self.hover_letter * CHAR_WIDTH,
            top + CHAR_HEIGHT + 1,
            left + (self.hover_letter + 1) * CHAR_WIDTH,
            top + CHAR_HEIGHT + 1,
            1
        )

        oled.show()

    def main(self):
        while True:
            letter = int(k2.percent() * len(self.letters))
            if letter == len(self.letters):
                # .percent() can return 1, so avoid out-of-bounds issues
                letter -= 1
            if letter != self.hover_letter:
                self.hover_letter = letter
                self.ui_dirty = True

            if self.ui_dirty:
                self.ui_dirty = False
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
