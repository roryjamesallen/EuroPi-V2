# Morse

Morse is a gate sequencer that uses the
[Morse code](https://en.wikipedia.org/wiki/Morse_code) encoding
of a word to generate the high/low pattern.

The user uses the buttons and knobs to enter a word of up to
16 letters. The output is the encoded word.

## Inputs & Outputs

| I/O   | Notes                                     |
|-------|-------------------------------------------|
| `DIN` | Input clock/gate source                   |
| `AIN` | Unused                                    |
| `K1`  | Unused                                    |
| `K2`  | Used to select letters                    |
| `B1`  | Move letter input to the left             |
| `B2`  | Move letter input to the right            |
| `CV1` | Gate output, treating `.` as high         |
| `CV2` | Latched gate output, treating `.` as high |
| `CV3` | End-of-letter gate                        |
| `CV4` | Gate output, treating `.` as low          |
| `CV5` | Latched gate output, treating `.` as low  |
| `CV6` | End-of-word gate                          |

Normal gate outputs go low on the falling edge of the clock signal
on `DIN`. Latched gate outputs stay high across multiple pulses if
adjacent signals would be high.

## Morse Code Reference

| Letter/Number | Morse representation |
|---------------|----------------------|
| A             | `.-`                 |
| B             | `-...`               |
| C             | `-.-.`               |
| D             | `-..`                |
| E             | `.`                  |
| F             | `..-.`               |
| G             | `--.`                |
| H             | `....`               |
| I             | `..`                 |
| J             | `.---`               |
| K             | `-.-`                |
| L             | `.-..`               |
| M             | `--`                 |
| N             | `-.`                 |
| O             | `---`                |
| P             | `.--.`               |
| Q             | `--.-`               |
| R             | `.-.`                |
| S             | `...`                |
| T             | `-`                  |
| U             | `..-`                |
| V             | `...-`               |
| W             | `.--`                |
| X             | `-..-`               |
| Y             | `-.--`               |
| Z             | `--..`               |
| 0             | `-----`              |
| 1             | `.----`              |
| 2             | `..---`              |
| 3             | `...--`              |
| 4             | `....-`              |
| 5             | `.....`              |
| 6             | `-....`              |
| 7             | `--...`              |
| 8             | `---..`              |
| 9             | `----.`              |
