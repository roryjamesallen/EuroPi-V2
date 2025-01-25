"""
A global configuration-editor menu

Used to edit the global EuroPiConfig settings -- use at your own peril!
"""

from europi import *
from europi_config import EuroPiConfig
from europi_script import EuroPiScript

from configuration import ConfigFile
from experimental.settings_menu import *
from framebuf import FrameBuffer, MONO_HLSB


class SectionHeader(MenuItem):
    def __init__(self, title, children):
        super().__init__(children=children)
        self.title = title

    def draw(self, oled):
        oled.centre_text(f"{self.title}\n\nHold B2 to edit")


class ConfigurationEditor(EuroPiScript):
    def __init__(self):
        super().__init__()

        # fmt: off
        boolean_labels = {
            True: "Yes",
            False: "No"
        }

        voltage_items = []
        system_items = []
        display_items = []
        i2c_items = []

        config_points = EuroPiConfig.config_points()
        for cfg in config_points:
            if type(cfg) is BooleanConfigPoint:
                labels = boolean_labels
            else:
                labels = None

            # Special case; this name can't be easily modified & still fit, so just replace it
            if cfg.name == "MENU_AFTER_POWER_ON":
                title = "boot to menu"
                prefix = "Sys"
                items = system_items
            elif "EXTERNAL_I2C" in cfg.name:
                title = cfg.name.replace("EXTERNAL_I2C", "").replace("_", ' ').lower().strip()
                prefix = "I2C"
                items = i2c_items
            elif "DISPLAY" in cfg.name:
                title = cfg.name.replace("DISPLAY", "").replace("_", ' ').lower().strip()
                prefix = "OLED"
                items = display_items
            elif "VOLTAGE" in cfg.name:
                title = cfg.name.replace("VOLTAGE", "").replace("_", ' ').lower().replace("input", "in").replace("output", "out").strip()
                prefix = "Voltage"
                items = voltage_items
            else:
                title = cfg.name.replace("_", ' ').lower().strip()
                prefix = "Sys"
                items = system_items

            items.append(
                SettingMenuItem(
                    config_point=cfg,
                    labels=labels,
                    float_resolution=1,
                    prefix=prefix,
                    title=title,
                )
            )

        self.menu = SettingsMenu(
            menu_items=[
                # Voltage properties
                SectionHeader(
                    title="Voltage",
                    children=voltage_items
                ),

                # System properties
                SectionHeader(
                    title="System",
                    children=system_items
                ),

                # Display properties
                SectionHeader(
                    title="Display/OLED",
                    children=display_items
                ),

                # External I2C properties
                SectionHeader(
                    title="I2C",
                    children=i2c_items
                ),
            ]
        )
        self.menu.load_defaults(ConfigFile.config_filename(EuroPiConfig))
        # fmt: on

    def main(self):
        # fmt: off
        disk_icon = bytearray(b'\xff\xf0\x9f\xe8\x9f$\x9f"\x9f!\x9f\xe1\x80\x01\xbf\xfd\xa0\x05\xaf\xf5\xa0\x05\xaf\xf5\xa0\x05\xbf\xfd\x80\x01\xff\xff')
        # fmt: on

        icon_height = OLED_HEIGHT // 2 - 8
        text_height = OLED_HEIGHT // 2 - CHAR_HEIGHT // 2

        while True:
            if self.menu.ui_dirty:
                oled.fill(0)
                self.menu.draw()
                oled.show()

            if self.menu.settings_dirty:
                # visually indicate we're saving
                oled.fill(0)
                oled.blit(FrameBuffer(disk_icon, 16, 16, MONO_HLSB), 0, icon_height)
                oled.text("Saving...", 18, text_height, 1)
                oled.show()

                self.menu.save(ConfigFile.config_filename(EuroPiConfig))
                time.sleep(0.5)

                oled.fill(0)
                self.menu.draw()
                oled.show()


if __name__ == "__main__":
    ConfigurationEditor().main()
