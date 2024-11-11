import configuration
from configuration import ConfigFile, ConfigSpec


# sub-key constants for CPU_FREQS dict (see below)
# fmt: off
OVERCLOCKED_FREQ = "overclocked"
DEFAULT_FREQ = "normal"           # the Europi default is to overclock, so to avoid confusion about the default
                                  # not being "default" just use a different word
# fmt: on

# Default & overclocked CPU frequencies for supported boards
# Key: board type (corresponds to EUROPI_MODEL setting)
# Sub-key: "default" or "overclocked"
# fmt: off
CPU_FREQS = {
    "pico": {
        DEFAULT_FREQ: 125_000_000,     # Pico default frequency is 125MHz
        OVERCLOCKED_FREQ: 250_000_000  # Overclocked frequency is 250MHz
    },
    "pico2": {
        DEFAULT_FREQ: 150_000_000,     # Pico2 default frequency is 150MHz
        OVERCLOCKED_FREQ: 300_000_000  # Overclocked frequency is 300MHz
    },
    "pico h": {
        DEFAULT_FREQ: 125_000_000,     # Pico H default frequency is 125MHz
        OVERCLOCKED_FREQ: 250_000_000  # Overclocked frequency is 250MHz
    },
    "pico w": {
        DEFAULT_FREQ: 125_000_000,     # Pico W default frequency is 125MHz
        OVERCLOCKED_FREQ: 250_000_000  # Overclocked frequency is 250MHz
    }
}
# fmt: on


class EuroPiConfig:
    """This class provides EuroPi's global config points.

    To override the default values, create /config/EuroPiConfig.json on the Raspberry Pi Pico
    and populate it with a JSON object. e.g. if your build has the oled mounted upside-down compared
    to normal, the contents of /config/EuroPiConfig.json should look like this:

    {
        "ROTATE_DISPLAY": true
    }
    """

    @classmethod
    def config_points(cls):
        # fmt: off
        return [
            # EuroPi revision -- this is currently unused, but reserved for future expansion
            configuration.choice(
                name="EUROPI_MODEL",
                choices = ["europi"],
                default="europi"
            ),

            # CPU & board settings
            configuration.choice(
                name="PICO_MODEL",
                choices=["pico", "pico w", "pico2", "pico h"],
                default="pico"
            ),
            configuration.choice(
                name="CPU_FREQ",
                choices=[
                    DEFAULT_FREQ,
                    OVERCLOCKED_FREQ
                ],
                default=OVERCLOCKED_FREQ,
            ),

            # Display settings
            configuration.boolean(
                name="ROTATE_DISPLAY",
                default=False
            ),
            configuration.integer(
                name="DISPLAY_WIDTH",
                minimum=8,
                maximum=1024,
                default=128
            ),
            configuration.integer(
                name="DISPLAY_HEIGHT",
                minimum=8,
                maximum=1024,
                default=32
            ),
            configuration.choice(
                name="DISPLAY_SDA",
                choices=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 26],
                default=0,
            ),
            configuration.choice(
                name="DISPLAY_SCL",
                choices=[1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 27],
                default=1,
            ),
            configuration.integer(
                name="DISPLAY_CHANNEL",
                minimum=0,
                maximum=1,
                default=0
            ),

            # I/O voltage settings
            configuration.floatingPoint(
                name="MAX_OUTPUT_VOLTAGE",
                minimum=1.0,
                maximum=10.0,
                default=10.0
            ),
            configuration.floatingPoint(
                name="MAX_INPUT_VOLTAGE",
                minimum=1.0,
                maximum=12.0,
                default=12.0
            ),
            configuration.floatingPoint(
                name="GATE_VOLTAGE",
                minimum=1.0,
                maximum=10.0,
                default=5.0
            ),

            # Menu settings
            configuration.boolean(
                name="MENU_AFTER_POWER_ON",
                default=False
            ),
        ]
        # fmt: on


def load_europi_config():
    return ConfigFile.load_config(EuroPiConfig, ConfigSpec(EuroPiConfig.config_points()))
