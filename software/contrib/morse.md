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
| `K2`  | Select the letter to edit                 |
| `B1`  | Cycle the letter one position backwards   |
| `B2`  | Cycle the letter one position forwards    |
| `CV1` | Gate output, treating `.` as high         |
| `CV2` | Latched gate output, treating `.` as high |
| `CV3` | End-of-letter gate                        |
| `CV4` | Gate output, treating `.` as low          |
| `CV5` | Latched gate output, treating `.` as low  |
| `CV6` | End-of-word gate                          |

Normal gate outputs go low on the falling edge of the clock signal
on `DIN`. Latched gate outputs stay high across multiple pulses if
adjacent signals would be high.

## Patching Ideas

Because `Morse` outputs a binary on/off sequence instead of
long/short gates, it doesn't naturally sound like morse code.
But with some clever patching you can create audible morse code!

### Idea 1: Two envelopes

Patch the output from `CV1` into an envelope with a short
decay and the output from `CV4` into an envelope with a long
decay. Connect these two envelopes into your VCA (or if your
VCA only has 1 CV input, use a mixer).

### Idea 2: CV-controlled envelope

If your envelope generator has CV over the decay, you can patch
`CV1` into the envelope's trigger, and `CV5` into the decay CV.
You may need to attenuate the CV control to get the durations right,
but this will let you generate long and short pulses with a
single envelope.

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
