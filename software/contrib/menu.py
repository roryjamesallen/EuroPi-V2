"""See menu.md for details."""
# Reset the module state and display bootsplash screen.
from europi import bootsplash


bootsplash()


from bootloader import BootloaderMenu
from collections import OrderedDict

## Scripts that are included in the menu
#
#  Keys are the names displayed in the menu, values are the fully-qualified names
#  of the classes to launch.  The classes MUST be EuriPiScript subclasses
#
#  The OLED can display up to 16 characters horizontally, so make sure the names fit
#  that width requirement
#
# fmt: off
EUROPI_SCRIPTS = OrderedDict([
#   ["0123456789abcdef",  "contrib.spam.Eggs"],
    ["Arpeggiator",       "contrib.arp.Arpeggiator"],
    ["Bernoulli Gates",   "contrib.bernoulli_gates.BernoulliGates"],
    ["Bezier Curves",     "contrib.bezier.Bezier"],
    ["Binary Counter",    "contrib.binary_counter.BinaryCounter"],
    ["Bit Garden",        "contrib.bit_garden.BitGarden"],
    ["Clock Modifier",    "contrib.clock_mod.ClockModifier"],
    ["Coin Toss",         "contrib.coin_toss.CoinToss"],
    ["Consequencer",      "contrib.consequencer.Consequencer"],
    ["Conway",            "contrib.conway.Conway"],
    ["CVecorder",         "contrib.cvecorder.CVecorder"],
    ["Daily Random",      "contrib.daily_random.DailyRandom"],
    ["DCSN-2",            "contrib.dscn2.Dcsn2"],
    ["EgressusMelodiam",  "contrib.egressus_melodiam.EgressusMelodiam"],
    ["EnvelopeGen",       "contrib.envelope_generator.EnvelopeGenerator"],
    ["Euclid",            "contrib.euclid.EuclideanRhythms"],
    ["Gates & Triggers",  "contrib.gates_and_triggers.GatesAndTriggers"],
    ["Gate Phaser",       "contrib.gate_phaser.GatePhaser"],
    ["Hamlet",            "contrib.hamlet.Hamlet"],
    ["HarmonicLFOs",      "contrib.harmonic_lfos.HarmonicLFOs"],
    ["HelloWorld",        "contrib.hello_world.HelloWorld"],
    ["Itty Bitty",        "contrib.itty_bitty.IttyBitty"],
    ["KnobPlayground",    "contrib.knob_playground.KnobPlayground"],
    ["Kompari",           "contrib.kompari.Kompari"],
    ["Logic",             "contrib.logic.Logic"],
    ["Lutra",             "contrib.lutra.Lutra"],
    ["MasterClock",       "contrib.master_clock.MasterClock"],
    ["NoddyHolder",       "contrib.noddy_holder.NoddyHolder"],
    ["Pam's Workout",     "contrib.pams.PamsWorkout2"],
    ["Particle Phys.",    "contrib.particle_physics.ParticlePhysics"],
    ["Pet Rock",          "contrib.pet_rock.PetRock"],
    ["Piconacci",         "contrib.piconacci.Piconacci"],
    ["PolyrhythmSeq",     "contrib.polyrhythmic_sequencer.PolyrhythmSeq"],
    ["PolySquare",        "contrib.poly_square.PolySquare"],
    ["Probapoly",         "contrib.probapoly.Probapoly"],
    ["Quantizer",         "contrib.quantizer.QuantizerScript"],
    ["RadioScanner",      "contrib.radio_scanner.RadioScanner"],
    ["Scope",             "contrib.scope.Scope"],
    ["Seq. Switch",       "contrib.sequential_switch.SequentialSwitch"],
    ["Sigma",             "contrib.sigma.Sigma"],
    ["Slopes",            "contrib.slopes.Slopes"],
    ["Smooth Rnd Volts",  "contrib.smooth_random_voltages.SmoothRandomVoltages"],
    ["StrangeAttractor",  "contrib.strange_attractor.StrangeAttractor"],
    ["Traffic",           "contrib.traffic.Traffic"],
    ["Turing Machine",    "contrib.turing_machine.EuroPiTuringMachine"],
    ["Volts",             "contrib.volts.OffsetVoltages"],

    # System tools, in alphabetical order with a _ prefix

    ["_About",            "tools.about.About"],
    ["_BootloaderMode",   "bootloader_mode.BootloaderMode"],
    ["_Calibrate",        "tools.calibrate.Calibrate"],
    ["_Config Editor",    "tools.conf_edit.ConfigurationEditor"],
    ["_Diagnostic",       "tools.diagnostic.Diagnostic"],
    ["_Exp Cfg Editor",   "tools.experimental_conf_edit.ExperimentalConfigurationEditor"],
])
# fmt: on

if __name__ == "__main__":
    BootloaderMenu(EUROPI_SCRIPTS).main()
