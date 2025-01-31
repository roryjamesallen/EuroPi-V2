# Contributions

Please see the [contributing guide](/contributing.md) for details on how to contribute a script to this
directory, specifically [the section on contrib scripts](/contributing.md#contrib-scripts).

# List of packaged scripts

### Arpeggiator \[ [documentation](/software/contrib/arp.md) | [script](/software/contrib/arp.py) \]

A quantized scale/arpeggio generator

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: quantizer, scale, arpeggio</i>

### Bernoulli Gates \[ [documentation](/software/contrib/bernoulli_gates.md) | [script](/software/contrib/bernoulli_gates.py) \]

A probability script based on Mutable Instruments Branches

Two channels of probability-based routing, where the digital input will be routed to one of two outputs based on a weighted random chance, controlled by a knob per channel, and the analogue input for channel 1

<i>Author: [Bridgee](https://github.com/Bridgee)</i>
<br><i>Labels: Random</i>

### Bezier Curves \[ [documentation](/software/contrib/bezier.md) | [script](/software/contrib/bezier.py) \]

Smooth random voltages based on bezier curves. Inspired by the ADDAC507 Random Bezier Waves module.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: Random</i>

### Clock Modifier \[ [documentation](/software/contrib/clock_mod.md) | [script](/software/contrib/clock_mod.md) \]

A clock multiplier or divider. Each channel has an independently-controllable modifier, multiplying or dividing an external clock signal on `din`.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: clock, clock multiplier, clock divider, gates</i>

### Consequencer \[ [documentation](/software/contrib/consequencer.md) | [script](/software/contrib/consequencer.md) \]

A gate and CV sequencer inspired by Mutable Instruments Grids and the Music Thing Modular Turing Machine

Users can morph between patterns and CV sequences during operation, with 3 gate and 3 CV outputs based on the current pattern, programmed randomness, and CV input, running from an external clock

<i>Author: [gamecat69](https://github.com/gamecat69)</i>
<br><i>Labels: sequencer, gates, triggers, drums, randomness</i>

### Conway \[ [documentation](/software/contrib/conway.md) | [script](/software/contrib/conway.md) \]

A semi-random LFO that uses [John Conway's Game Of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) to produce CV and gate signals.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: lfo, gates, randomness</i>

### CVecorder \[ [documentation](/software/contrib/cvecorder.md) | [script](/software/contrib/cvecorder.py) \]

6 channels of control voltage recording

Record 6 banks of 6 channels of control voltage, and then play them back at a consistent rate set by an external clock.
Recording of CV can be primed so that you can record a movement without missing a beat

<i>Author: [anselln](https://github.com/anselln)</i>
<br><i>Labels: sequencer, CV, performance</i>

### Daily Random \[ [documentation](/software/contrib/daily_random.md) | [script](/software/contrib/daily_random.md) \]

A pseudo-random gate and CV sequencer that uses a realtime clock to generate patterns.

Requires installing and configuring a realtime clock module, connected to EuroPi's external I2C interface for best results.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: sequencer, gate, cv, random, realtime clock</i>

### DCSN-2 \[ [documentation](/software/contrib/dscn2.md) | [script](/software/contrib/dcsn2.md) \]

A loopable random gate sequencer based on a binary tree.  Inspired by the Robaux DCSN3

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: sequencer, gates, triggers, randomness</i>

### Egressus Melodium \[ [documentation](/software/contrib/egressus_melodiam.md) | [script](/software/contrib/egressus_melodiam.py) \]
Clockable and free-running LFO and random CV pattern generator

<i>Author: [gamecat69](https://github.com/gamecat69)</i>
<br><i>Labels: clocked lfo, sequencer, CV, randomness</i>

### Envelope Generator \[ [documentation](/software/contrib/envelope_generator.md) | [script](/software/contrib/envelope_generator.py) \]

An attack release envelope with optional sustain and looping functionality.
Envelopes are triggered or gated by the digital input, and the envelope is output, along with a copy of the digital input and an inverted copy of the envelope.

<i>Author: [roryjamesallen](https://github.com/roryjamesallen)</i>
<br><i>Labels: Envelope Generator</i>

### Euclid \[ [documentation](/software/contrib/euclid.md) | [script](/software/contrib/euclid.py) \]

Euclidean rhythm generator. Each channel can generate an independent euclidean rhythm.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: sequencer, gates, triggers, euclidean</i>

### Gates and Triggers \[ [documentation](/software/contrib/gates_and_triggers.md) | [script](/software/contrib/gates_and_triggers.py) \]

Convert incoming triggers to gates or gates to triggers.  Buttons allow manually creating gates/triggers, knobs control
the duration of the output signals.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: gates, triggers</i>

### Gate Phaser \[ [documentation](/software/contrib/gate_phaser.md) | [script](/software/contrib/gate_phaser.py) \]

A script which attempts to answer the question "What would Steve Reich do if he had a EuroPi?"

<i>Author: [gamecat69](https://github.com/gamecat69)</i>
<br><i>Labels: sequencer, gates</i>

### Hamlet \[ [documentation](/software/contrib/hamlet.md) | [script](/software/contrib/hamlet.py) \]

A variation of the Consequencer script specifically geared towards driving voices

2pairs of gate and CV outputs are available to drive two voices, as well as 2 drum gate outputs.
As with the consequencer, the patterns can be smoothly morphed between while performing

<i>Author: [seanbechhofer](https://github.com/seanbechhofer)</i>
<br><i>Labels: sequencer, gates, triggers, drums, randomness</i>

### Harmonic LFOs \[ [documentation](/software/contrib/harmonic_lfos.md) | [script](/software/contrib/harmonic_lfos.py) \]

6 tempo-related LFOs with adjustable wave shape

Users can run up to 6 LFOs with one internal master clock, with wave shapes of either sine, saw, square, semi-random, or off.
The division of the master clock that each LFO runs at, as well as each of their wave shapes, can be adjusted during operation

<i>Author: [roryjamesallen](https://github.com/roryjamesallen)</i>
<br><i>Labels: LFO</i>

### Itty Bitty \[ [documentation](/software/contrib/itty_bitty.md) | [script](/software/contrib/itty_bitty.py) \]

Dual-channel 8-bit trigger+gate+cv sequencer based on the binary representation of an 8-bit number.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: sequencer, gate, trigger, cv</i>

### Kompari \[ [documentation](/software/contrib/kompari.md) | [script](/software/contrib/kompari.py) \]

Compares `AIN` to `K1` and `K2`, outputting 5V digital signals on `CV1`-`CV5`, and an analogue output signal based on
comparing all 3 sources.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: logic, gates, binary operators</i>

### Logic \[ [documentation](/software/contrib/logic.md) | [script](/software/contrib/logic.py) \]

Treats both inputs as digital on/off signals and outputs the results of binary AND, OR, XOR, NAND, NOR, and XNOR operations on outputs 1-6.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: logic, gates, binary operators</i>

### Lutra \[ [documentation](/software/contrib/lutra.md) | [script](/software/contrib/lutra.py) \]

Six syncable LFOs with variable wave shapes. The clock speed of each LFO is slightly different, with an adjustable base speed and CV-controllable spread.

Inspired by [Expert Sleepers' Otterley](https://expert-sleepers.co.uk/otterley.html) module.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: lfo</i>

### Morse \[ [documentation](/software/contrib/morse.md) | [script](/software/contrib/morse.md) \]

A gate sequencer that uses Morse code to generate the on/off pattern.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: gates, sequencer</i>

### Noddy Holder \[ [documentation](/software/contrib/noddy_holder.md) | [script](/software/contrib/noddy_holder.py) \]

Two channels of sample/track and hold based on a single trigger and CV source

Users have a copy of the original trigger signal, a sample and hold and a track and hold of the analogue input, and the all above but with the gate inverted, available from the CV outputs

<i>Author: [seanbechhofer](https://github.com/seanbechhofer)</i>
<br><i>Labels: gates, sample&hold, track&hold</i>

### Pam's "EuroPi" Workout \[ [documentation](/software/contrib/pams.md) | [script](/software/contrib/pams.py) \]

A re-imaging of [ALM/Busy Circuit's Pamela's "NEW" Workout](https://busycircuits.com/alm017/). Turns the EuroPi into a clocked modulation
source with multiple wave shapes, optional quantization, euclidean rhythm outputs and external start/stop trigger input.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: clock, euclidean, gate, lfo, quantizer, random, trigger</i>

### Particle Physics \[ [documentation](/software/contrib/particle_physics.md) | [script](/software/contrib/particle_physics.py) \]

An irregular LFO based on a basic 1-dimensional physics simulation. Outputs triggers when a particle bounces under the effects of gravity. Outputs control signals
based on the particle's position and velocity.

While not technically random, the effects of changing the particle's initial conditions, gravity, and elasticity coefficient can create unpreditable rhythms.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: gate, lfo, sequencer, random, trigger</i>

### Pet Rock \[ [documentation](/software/contrib/pet_rock.md) | [script](/software/contrib/pet_rock.py) \]

A pseudo-random gate generator that uses the realtime clock to track the phase of the moon as a seed. Based on [Pet Rock by Jonah Senzel](https://petrock.site)

Requires installing and configuring a realtime clock module, connected to EuroPi's external I2C interface for best results.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: sequencer, gate, random, realtime clock</i>

### Poly Square \[ [documentation](/software/contrib/poly_square.md) | [script](/software/contrib/poly_square.py) \]

Six independent oscillators which output on CVs 1-6.

The base pitch is set by the analog input, which is interpreted as a V/oct input with 0V = C. Knob 1 allows for detuning of the 6 voices, and as the knob is turned clockwise, the spread between them increases. Button 2 toggles the maximum detune between a half step and a major 9th. Knob 2 sets the polyphony mode.

<i>Author: [t-schreibs](https://github.com/t-schreibs)</i>
<br><i>Labels: oscillator, poly</i>

### Polyrhythmic Sequencer \[ [script](/software/contrib/polyrhythmic_sequencer.py) \]

A sequencer that advances notes according to a polyrhythmic clock, inspired by the operation of the Moog Subharmonicon sequencer

Users can run two simultaneous polyrhythmic sequences clocked by the same external clock.
Quantised outputs are available, with the note for each step, and the polyrhythm it runs at, being easily changed to write the sequence

<i>Author: [awonak](https://github.com/awonak)</i>
<br><i>Labels: polyrhythms, sequencer, triggers</i>

### Probapoly \[ [documentation](/software/contrib/probapoly.md) | [script](/software/contrib/probapoly.py) \]

Creates interesting polyrhythmic gate patterns while also allowing probabilities to be set on gates.

Given values for and upper and lower rhythmic ratios, Probapoly will create a looping pattern as short as possible with no repetition of the pattern within the loop.

<i>Author: [gamecat69](https://github.com/gamecat69)</i>
<br><i>Labels: sequencer, performance, gates, polyrhythm, probability</i>

### Quantizer \[ [documentation](/software/contrib/quantizer.md) | [script](/software/contrib/quantizer.py) \]

Quantizes input analog signals to a customizable scale.  Additional signals output the same note shifted up or down to create harmonies across multiple oscillators.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: quantizer</i>

### Radio Scanner \[ [documentation](/software/contrib/radio_scanner.md) | [script](/software/contrib/radio_scanner.py) \]

A tool for exploring sounds and control voltage combinations by navigating a 2D plane

The two knobs allow users to scan in 2 separate axis, with the value of each knob available as a CV output.
There is also a CV output for the difference between the two knob positions, and then the lower row of CV outputs is the inverse of each jack above.
The outputs can also be rotated as inspired by the 4MS Rotating Clock Divider

<i>Author: [roryjamesallen](https://github.com/roryjamesallen)</i>
<br><i>Labels: n/a</i>

### Sequential Switch \[ [documentation](/software/contrib/sequential_switch.md) | [script](/software/contrib/sequential_switch.py) \]

A 2-6 output sequential switch.  The analogue input is mirrored to one of the outputs, with the specific output changed every time a trigger is received.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: random, sequential switch</i>

### Sigma \[ [documentation](/software/contrib/sigma.md) | [script](/software/contrib/sigma.py) \]

Random CV, optionally quantized, voltages based on controllable normal distributions. Inspired by Magnetic Freak's Gaussian module.

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: random, quantizer</i>

### Slopes \[ [documentation](/software/contrib/slopes.md) | [script](/software/contrib/slopes.py) \]

CV analyzer that produces gates & CV outputs based on the slope of the incoming signal

<i>Author: [chrisib](https://github.com/chrisib)</i>
<br><i>Labels: gates, CV</i>

### Smooth Random Voltages \[ [script](/software/contrib/smooth_random_voltages.py) \]

Random CV with adjustable slew rate, inspired by: https://youtu.be/tupkx3q7Dyw.

3 random or analog input s&h voltages with changable slew smoothness. New voltages assigned upon each digital input trigger. Top row outputs move
towards target voltage according to slew rate set by knob 1. Bottom row outputs immediately change to new target voltage.

<i>Author: [awonak](https://github.com/awonak)</i>
<br><i>Labels: random, s&h</i>

### Strange Attractor \[ [documentation](/software/contrib/strange_attractor.md) | [script](/software/contrib/strange_attractor.py) \]

A source of chaotic modulation using systems of differential equations such as the Lorenz System

Users have the x, y, and z values of the output of each attractor model available as CV outputs, as well as 3 gate signals related to the relationships between these values

<i>Author: [seanbechhofer](https://github.com/seanbechhofer)</i>
<br><i>Labels: gates, triggers, randomness</i>

### Traffic \[ [documentation](/software/contrib/traffic.md) | [script](/software/contrib/traffic.py) \]

A re-imagining of [Jasmine and Olive Tree's Traffic](https://jasmineandolivetrees.com/products/traffic) module. Triggers are sent to both inputs
generating CV signals based on which trigger fired most recently and a pair of gains per channel.

<i>Author: [chrisib](http://github.com/chrisib)</i>
<br><i>Labels: sequencer, gate, triggers</i>

### Turing Machine \[ [documentation](/software/contrib/turing_machine.md) | [script](/software/contrib/turing_machine.py) \]

A script meant to recreate the [Music Thing Modular Turning Machine Random Sequencer](https://musicthing.co.uk/pages/turing.html)
as faithfully as possible on the EuroPi hardware.

<i>Author: [mjaskula](https://github.com/mjaskula)</i>
<br><i>Labels: sequencer, random, triggers</i>

### Volts \[ [documentation](/software/contrib/volts.md) | [script](/software/contrib/volts.py) \]

Generates static voltages on CV1-6. Useful for when you need a reliable, fixed voltage source as an input. Some useful applications include:
- transposing a sequencer
- shifting a bipolar LFO or VCO to be unipolar
- sending a fixed voltage to a VCA to amplify a signal to a fixed level
- calibrating other modules

<i>Author: [chrisib](http://github.com/chrisib)</i>
<br><i>Labels: cv, voltages, non-interactive</i>

---

<details>
<summary><h2>Proof of Concept Scripts</h2></summary>

### Coin Toss \[ [documentation](/software/contrib/coin_toss.md) | [script](/software/contrib/coin_toss.py) \]

A probability utility with an output based on a percentage choice between 1 or 0

Using the threshold knob and analogue input, users can determine whether a 1 or a 0 is preferred by the weighted random choice each time the digital input is triggered, or an internal clock depending on the mode

<i>Author: [awonak](https://github.com/awonak)</i>
<br><i>Labels: Clock, Random, CV Generation</i>

### Hello World \[ [script](/software/contrib/hello_world.py) \]

An example script for the menu system

This script can be copied and altered as a starting point for your own scripts that are to be menu compatible, and make use of the save state functionality

<i>Author: [mjaskula](https://github.com/mjaskula)</i>
<br><i>Labels: example</i>

### Scope \[ [script](/software/contrib/scope.py) \]

An oscilloscope script to monitor the analogue and digital inputs

The current values of the analogue and digital inputs are displayed in an oscilloscope style on the OLED display, and copies of both signals, as well as an inverted gate signal, are available from the CV outputs

<i>Author: [mjaskula](https://github.com/mjaskula)</i>
<br><i>Labels: utility</i>

</details>
