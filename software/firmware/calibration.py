# How many CV outputs are there?
# On EuroPi this 6, but future versions (e.g. EuroPi X may have more)
NUM_CVS = 6


# Import the calibration values
# These are generated by tools/calibrate.py, but do not exist by default
try:
    from calibration_values import INPUT_CALIBRATION_VALUES, OUTPUT_CALIBRATION_VALUES
except ImportError:
    # Note: run calibrate.py to get a more precise calibration.
    # Default calibration values are close-enough to reasonable performance, but aren't great
    INPUT_CALIBRATION_VALUES = [384, 44634]
    OUTPUT_CALIBRATION_VALUES = [
        0,
        6300,
        12575,
        19150,
        25375,
        31625,
        38150,
        44225,
        50525,
        56950,
        63475,
    ]
# Legacy calibration using only CV1; apply the same calibration values to each output
if type(OUTPUT_CALIBRATION_VALUES[0]) is int:
    cv1_values = OUTPUT_CALIBRATION_VALUES
    OUTPUT_CALIBRATION_VALUES = []
    for i in range(NUM_CVS):
        OUTPUT_CALIBRATION_VALUES.append(cv1_values)
