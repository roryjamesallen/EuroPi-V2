from europi import *
from europi_script import EuroPiScript


class BinaryCounter(EuroPiScript):
    MAX_N = (1 << NUM_CVS) - 1

    def __init__(self):
        super().__init__()

        self.n = 0
        self.k = int(
            (
                k1.percent() + k2.percent() * ain.percent()
            ) * self.MAX_N
        )

        self.gate_recvd = False

        din.handler(self.on_gate_rise)
        din.handler_falling(self.on_gate_fall)
        b1.handler(self.on_gate_rise)
        b1.handler_falling(self.on_gate_fall)

        b2.handler(self.reset)

    def on_gate_rise(self):
        self.gate_recvd = True

    def on_gate_fall(self):
        turn_off_all_cvs()

    def reset(self):
        self.n = 0

    def set_outputs(self):
        for i in range(NUM_CVS):
            if (self.n >> i) & 0x01:
                cvs[i].on()
            else:
                cvs[i].off()

    def main(self):
        while True:
            self.k = int(
                (
                    k1.percent() + k2.percent() * ain.percent()
                ) * self.MAX_N
            )

            if self.gate_recvd:
                self.set_outputs()
                self.n = (self.n + self.k) & self.MAX_N
                self.gate_recvd = False

            oled.centre_text(f"""k = {self.k}
{self.n:06b}""")


if __name__ == "__main__":
    BinaryCounter().main()
