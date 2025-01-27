# Binary Counter

Binary Counter is a simple gate sequencer that uses binary numbers to turn gates on & off.

Starting from zero, every time a gate is received on `din`, the value of the counter is
incremented by `k`, and CV1-6 are set on/off according to the binary representation of the
counter.

## I/O Mapping

| I/O           | Usage
|---------------|-------------------------------------------------------------------|
| `din`         | Input gate signal                                                 |
| `ain`         | CV input to control `k`                                           |
| `b1`          | Manual gate signal                                                |
| `b2`          | Reset `n` to zero                                                 |
| `k1`          | Control for `k`                                                   |
| `k2`          | Attenuator for `ain`                                              |
| `cv1`         | Least significant bit output                                      |
| `cv2`         | 2s-bit output                                                     |
| `cv3`         | 4s-bit output                                                     |
| `cv4`         | 8s-bit output                                                     |
| `cv5`         | 16s-bit output                                                    |
| `cv6`         | Most significant bit output                                       |
