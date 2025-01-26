"""
Contains objects used for interactive settings menus

Menu interaction is done using a knob and a button (K2 and B2 by default):
- rotate the knob to select the menu item
- short-press to enter edit mode
- rotate knob to select an option
- short-press button to apply the new option
- long-press button to change between the 2 menu levels (if
  possible)

For examples of how to create and use the SettingsMenu, please refer to
- contrib/settings_menu_example.py

Additional, more complex, examples can be found in:
- contrib/euclid.py
- contrib/pams.py (this is a very complex example)
- contrib/sequential_switch.py
- tools/conf_edit.py
"""

import europi

from configuration import *
from experimental.knobs import KnobBank, LockableKnob
from framebuf import FrameBuffer, MONO_HLSB
from machine import Timer
import os
import time


# fmt: off
AIN_GRAPHICS = bytearray(b"\x00\x00|\x00|\x00d\x00d\x00g\x80a\x80\xe1\xb0\xe1\xb0\x01\xf0\x00\x00\x00\x00")
KNOB_GRAPHICS = bytearray(b"\x06\x00\x19\x80 @@ @ \x80\x10\x82\x10A @\xa0 @\x19\x80\x06\x00")

AIN_LABEL = "AIN"
KNOB_LABEL = "Knob"

AUTOSELECT_AIN = "autoselect_ain"
AUTOSELECT_KNOB = "autoselect_knob"

DANGER_GRAPHICS = bytearray(b'\x00\x00\x04\x00\n\x00\n\x00\x11\x00\x15\x00$\x80$\x80@@D@\x80 \xff\xe0')
# fmt: off


class MenuItem:
    """
    Generic class for anything we can display in the menu
    """

    def __init__(
        self, children: list[object] = None, parent: object = None, is_visible: bool = True
    ):
        """
        Create a new abstract menu item

        @param parent  A MenuItem representing this item's parent, if this item is the bottom-level of a
                       multi-level menu
        @param children  A list of MenuItems representing this item's children, if this is the top-level of a
                         multi-level menu
        @param is_visible  Is this menu item visible by default?
        """
        self.menu = None
        self.parent = parent
        self.children = children
        self.is_visible = is_visible

        # Used to indicate that if this is the active menu item, the UI should re-render it
        self.ui_dirty = False

        if parent and children:
            raise Exception("Cannot specify parent and children in the same menu item")

    def short_press(self):
        """Handler for when the user short-presses the button"""
        pass

    def draw(self, oled=europi.oled):
        """
        Draw the item to the screen

        @param oled   A Display-compatible object we draw to
        """
        self.ui_dirty = False

    def add_child(self, item):
        """
        Add a new child item to this item
        """
        if self.children is None:
            self.children = []
        self.children.append(item)
        item.parent = self
        item.menu = self.menu

    @property
    def is_editable(self):
        return False

    @is_editable.setter
    def is_editable(self, can_edit):
        pass

    @property
    def is_visible(self):
        return self._is_visible

    @is_visible.setter
    def is_visible(self, is_visible):
        self._is_visible = is_visible


class ChoiceMenuItem(MenuItem):
    """A generic menu item for displaying a choice of options to the user"""

    SELECT_OPTION_Y = 16

    def __init__(
        self,
        parent: MenuItem = None,
        children: list[MenuItem] = None,
        title: str = None,
        prefix: str = None,
        graphics: dict = None,
        labels: dict = None,
        is_visible: bool = True,
    ):
        """
        Create a new choice menu item

        @param parent  If the menu has multiple levels, what is this item's parent control?
        @param children  If this menu has multiple levels, whar are this item's child controls?
        @param title  The title to display at the top of the display when this control is active
        @param prefix  A prefix to display before the title when this control is active
        @param graphics  A dict of values mapped to FrameBuffer or bytearray objects, representing 12x12 MONO_HLSB
                         graphics to display along with the keyed values
        @param labels  A dict of values mapped to strings, representing human-readible versions of the ConfigPoint
                       options
        @param is_visible  Is this menu item visible by default?
        """
        super().__init__(
            children=children,
            parent=parent,
            is_visible=is_visible
        )

        self.title = title
        self.prefix = prefix
        self.graphics = graphics
        self.labels = labels

        self._is_editable = False

    def short_press(self):
        """Toggle is_editable on a short press"""
        self.is_editable = not self.is_editable

    def draw(self, oled=europi.oled):
        """
        Draw the current item to the display object

        You MUST call the display's .show() function after calling this in order to send the buffer to the display
        hardware

        @param oled  A Display instance (or compatible class) to render the item
        """
        super().draw(oled)

        if self.is_editable:
            display_value = self.menu.knob.choice(self.choices)
        else:
            display_value = self.default_choice

        text_left = 0
        prefix_left = 1
        prefix_right = len(self.prefix) * europi.CHAR_WIDTH
        title_left = len(self.prefix) * europi.CHAR_WIDTH + 4

        # If we're in a top-level menu the submenu is non-empty. In that case, the prefix in inverted text
        # Otherwise, the title in inverted text to indicate we're in the sub-menu
        if self.children and len(self.children) > 0:
            oled.fill_rect(prefix_left - 1, 0, prefix_right + 1, europi.CHAR_HEIGHT + 2, 1)
            oled.text(self.prefix, prefix_left, 1, 0)
            oled.text(self.title, title_left, 1, 1)
        else:
            oled.fill_rect(
                title_left - 1,
                0,
                len(self.title) * europi.CHAR_WIDTH + 2,
                europi.CHAR_HEIGHT + 2,
                1,
            )
            oled.text(self.prefix, prefix_left, 1, 1)
            oled.text(self.title, title_left, 1, 0)

        if self.graphics:
            gfx = self.graphics.get(display_value, None)
            if gfx:
                text_left = 14  # graphics are 12x12, so add 2 pixel padding
                if type(gfx) is bytearray:
                    gfx = FrameBuffer(gfx, 12, 12, MONO_HLSB)
                oled.blit(gfx, 0, self.SELECT_OPTION_Y)

        if self.labels:
            display_text = self.labels.get(display_value, str(display_value))
        else:
            display_text = str(display_value)

        if self.is_editable:
            # draw the value in inverted text
            text_width = len(display_text) * europi.CHAR_WIDTH

            oled.fill_rect(
                text_left,
                self.SELECT_OPTION_Y,
                text_left + text_width + 3,
                europi.CHAR_HEIGHT + 4,
                1,
            )
            oled.text(display_text, text_left + 1, self.SELECT_OPTION_Y + 2, 0)
        else:
            # draw the selection in normal text
            oled.text(display_text, text_left + 1, self.SELECT_OPTION_Y + 2, 1)

    @property
    def choices(self):
        raise NotImplemented("choices(self) must be implemented by the sub-class!")

    @property
    def default_choice(self):
        raise NotImplemented("default_choice(self) must be implemented by the sub-class!")

    @property
    def is_editable(self):
        return self._is_editable

    @is_editable.setter
    def is_editable(self, can_edit):
        self._is_editable = can_edit


class SettingMenuItem(ChoiceMenuItem):
    """
    A single menu item that presents a setting the user can manipulate

    The menu item is a wrapper around a ConfigPoint, and uses
    that object's values as the available selections.
    """

    def __init__(
        self,
        config_point: ConfigPoint = None,
        parent: MenuItem = None,
        children: list[MenuItem] = None,
        title: str = None,
        prefix: str = None,
        graphics: dict = None,
        labels: dict = None,
        callback=lambda new_value, old_value, config_point, arg: None,
        callback_arg=None,
        float_resolution=2,
        value_map: dict = None,
        is_visible: bool = True,
        autoselect_knob: bool = False,
        autoselect_cv: bool = False,
    ):
        """
        Create a new menu item around a ConfigPoint

        If the item has a callback function defined, it will be invoked once during initialization

        @param config_point  The configration option this menu item controls
        @param parent  If the menu has multiple levels, what is this item's parent control?
        @param children  If this menu has multiple levels, whar are this item's child controls?
        @param title  The title to display at the top of the display when this control is active
        @param prefix  A prefix to display before the title when this control is active
        @param graphics  A dict of values mapped to FrameBuffer or bytearray objects, representing 12x12 MONO_HLSB
                         graphics to display along with the keyed values
        @param labels  A dict of values mapped to strings, representing human-readible versions of the ConfigPoint
                       options
        @param callback  A function to invoke when this item's value changes. Must accept
                         (new_value, old_value, config_point, arg=None) as parameters
        @param callback_arg  An optional additional argument to pass to the callback function
        @param float_resolution  The resolution of floating-point config points (ignored if config_point is not
                                 a FloatConfigPoint)
        @param value_map  An optional dict to map the underlying simple ConfigPoint values to more complex objects
                          e.g. map the string "CMaj" to a Quantizer object
        @param is_visible  Is this menu item visible by default?
        @param autoselect_knob  If True, this item gets "Knob" as an additional choice, allowing ad-hoc selection
                                via the knob
        @param autoselect_cv  If True, this item gets "AIN" as an additional choice, allowing ad-hoc selection
                              via the CV input
        """
        if title is None:
            title = config_point.name
        if prefix is None:
            prefix = ""

        super().__init__(
            parent=parent,
            children=children,
            title=title,
            prefix=prefix,
            graphics=graphics,
            labels=labels,
            is_visible=is_visible,
        )

        self.autoselect_cv = autoselect_cv
        self.autoselect_knob = autoselect_knob
        self.value_map = value_map

        # the configuration setting that we're controlling via this menu item
        # convert everything to a choice configuration; this way we can add the knob/ain options too
        if type(config_point) is FloatConfigPoint:
            self.float_resolution = float_resolution
        self.src_config = config_point
        choices = self.get_option_list()
        self.config_point = ChoiceConfigPoint(
            config_point.name,
            choices=choices,
            default=config_point.default,
            danger=config_point.danger,
        )

        self.NUM_AUTOINPUT_CHOICES = 0
        if self.autoselect_cv or self.autoselect_knob:
            if self.autoselect_cv:
                self.NUM_AUTOINPUT_CHOICES += 1
            if self.autoselect_knob:
                self.NUM_AUTOINPUT_CHOICES += 1

            if not self.graphics:
                self.graphics = {}
            self.graphics[AUTOSELECT_AIN] = AIN_GRAPHICS
            self.graphics[AUTOSELECT_KNOB] = KNOB_GRAPHICS

            if not self.labels:
                self.labels = {}
            self.labels[AUTOSELECT_AIN] = AIN_LABEL
            self.labels[AUTOSELECT_KNOB] = KNOB_LABEL

        self.callback_fn = callback
        self.callback_arg = callback_arg

        # assign the initial value without firing any callbacks
        self._value = self.config_point.default
        self._value_choice = self.config_point.default

    @property
    def choices(self):
        return self.config_point.choices

    @property
    def default_choice(self):
        return self.value_choice

    def reset_to_default(self):
        """
        Reset this item to its default value
        """
        self.choose(self.src_config.default)

    def modify_choices(self, choices=None, new_default=None):
        """
        Regenerate this item's available choices

        This is needed if we externally modify e.g. the maximum/minimum values of the underlying
        config point as a result of one option needing to be within a range determined by another.

        @param choices  The list of new options we want to allow the user to choose from, excluding any autoselections
        @param new_default  A value to assign to this setting if its existing value is out-of-range
        """
        if choices is None:
            choices = self.get_option_list()
        else:
            # add the autoselect items, if needed
            if self.autoselect_knob:
                choices.append(AUTOSELECT_KNOB)
            if self.autoselect_knob:
                choices.append(AUTOSELECT_AIN)

        self.config_point.choices = choices
        still_valid = self.config_point.validate(self.value)
        if not still_valid.is_valid:
            self.choose(new_default)

    def short_press(self):
        """
        Handle a short button press

        This enters edit mode, or applies the selection and
        exits edit mode
        """
        if self.is_editable:
            new_choice = self.menu.knob.choice(self.config_point.choices)
            if new_choice != self.value_choice:
                # apply the currently-selected choice if we're in edit mode
                self.choose(new_choice)
                self.ui_dirty = True
                self.menu.settings_dirty = True

        super().short_press()

    def get_option_list(self):
        """
        Get the list of options the user can choose from

        @return  A list of choices
        """
        t = type(self.src_config)
        if t is FloatConfigPoint:
            FLOAT_RESOLUTION = 1.0 / (10**self.float_resolution)
            items = []
            x = self.src_config.minimum
            while x <= self.src_config.maximum:
                items.append(round(x, self.float_resolution))
                x += FLOAT_RESOLUTION
            items.append(round(self.src_config.maximum, self.float_resolution))
        elif t is IntegerConfigPoint:
            items = list(range(self.src_config.minimum, self.src_config.maximum + 1))
        elif t is BooleanConfigPoint:
            items = [False, True]
        elif t is ChoiceConfigPoint:
            items = list(self.src_config.choices)  # make a copy of the items so we can append the autoselect items!
        else:
            raise Exception(f"Unsupported ConfigPoint type: {type(self.src_config)}")

        # Add the autoselect inputs, if needed
        if self.autoselect_knob:
            items.append(AUTOSELECT_KNOB)
        if self.autoselect_knob:
            items.append(AUTOSELECT_AIN)

        return items

    def autoselect(self, percent: float):
        """
        Called by the parent menu when the Knob/CV timer fires, automatically updating the value of this item

        @param percent  A value 0-1 indicating the level of the knob/cv source
        """
        last_choice = len(self.config_point.choices) - self.NUM_AUTOINPUT_CHOICES
        index = int(
            percent * last_choice
        )
        if index >= last_choice:
            index = last_choice - 1

        item = self.config_point.choices[index]
        if item != self._value:
            self.ui_dirty = True
            old_value = self._value
            self._value = item
            self.callback_fn(item, old_value, self.config_point, self.callback_arg)

    def choose(self, choice):
        """
        Set the raw value of this item's ConfigPoint

        @param choice  The value to assign to the ConfigPoint.

        @exception  ValueError if the given choice is not valid for this setting
        """
        # kick out early if we aren't actually choosing anything
        if choice == self.value_choice:
            return

        validation = self.config_point.validate(choice)
        if not validation.is_valid:
            raise ValueError(f"{choice} is not a valid value for {self.config_point.name}")

        old_value = self._value_choice
        self._value_choice = choice

        if old_value == AUTOSELECT_AIN:
            self.menu.unregister_autoselect_cv(self)
        elif old_value == AUTOSELECT_KNOB:
            self.menu.unregister_autoselect_knob(self)

        if self._value_choice == AUTOSELECT_AIN:
            self.menu.register_autoselect_cv(self)
        elif self._value_choice == AUTOSELECT_KNOB:
            self.menu.register_autoselect_knob(self)
        else:
            self._value = choice
            self.callback_fn(choice, old_value, self.config_point, self.callback_arg)

    def draw(self, oled=europi.oled):
        super().draw(oled)

        # show the real value in parentheses
        if self.value_choice == AUTOSELECT_AIN or self.value_choice == AUTOSELECT_KNOB:
            oled.text(f"({self.value})", europi.OLED_WIDTH//2, self.SELECT_OPTION_Y, 1)


        # add a ! to the lower-right corner to indicate a potentially
        # volatile, edit-at-your-own-risk item
        if self.config_point.danger:
            fb = FrameBuffer(DANGER_GRAPHICS, 12, 12, MONO_HLSB)
            oled.blit(fb, europi.OLED_WIDTH - 12, europi.OLED_HEIGHT - 12)

    @property
    def value_choice(self):
        """The value the user has chosen from the menu"""
        return self._value_choice

    @property
    def value(self):
        """
        Get the raw value of this item's ConfigPoint

        You should use .mapped_value if you have assigned a value_map to the constructor
        """
        return self._value

    @property
    def mapped_value(self):
        """
        Get the value of this item mapped by the value_map

        If value_map was not set by the constructor, this property returns the same
        thing as .value
        """
        if self.value_map:
            return self.value_map[self._value]
        return self._value


class ActionMenuItem(ChoiceMenuItem):
    """
    A menu item that just invokes a callback function when selected.

    This class is similar to the SettingMenuItem, but doesn't wrap a ConfigPoint; it just has
    options and fires the callback when you choose one
    """

    def __init__(
        self,
        actions: list[object],
        callback = lambda x: None,
        callback_arg: object = None,
        parent: MenuItem = None,
        children: list[MenuItem] = None,
        title: str = None,
        prefix: str = None,
        graphics: dict = None,
        labels: dict = None,
        is_visible: bool = True,
    ):
        """
        Create a new menu item around a ConfigPoint

        If the item has a callback function defined, it will be invoked once during initialization

        @param actions  The list of choices the user can pick from. e.g. ["Cancel", "Ok"]
        @param callback  The function to call when the user invokes the action. The selected item from choices
                         is passed as the first parameter
        @param callback_arg  The second parameter passed to the callback
        @param parent  If the menu has multiple levels, what is this item's parent control?
        @param children  If this menu has multiple levels, whar are this item's child controls?
        @param title  The title to display at the top of the display when this control is active
        @param prefix  A prefix to display before the title when this control is active
        @param graphics  A dict of values mapped to FrameBuffer or bytearray objects, representing 12x12 MONO_HLSB
                         graphics to display along with the keyed values
        @param labels  A dict of values mapped to strings, representing human-readible versions of the ConfigPoint
                       options
        @param is_visible  Is this menu item visible by default?
        """
        super().__init__(
            parent=parent,
            children=children,
            title=title,
            prefix=prefix,
            graphics=graphics,
            labels=labels,
            is_visible=is_visible,
        )

        self.actions = actions
        self.callback = callback
        self.callback_arg = callback_arg
        self.title = title
        self.prefix = prefix

        self._is_editable = False

    @property
    def choices(self):
        return self.actions

    @property
    def default_choice(self):
        return self.choices[0]

    def short_press(self):
        if self.is_editable:
            # fire the callback if we're exiting edit-mode
            choice = self.menu.knob.choice(self.choices)
            self.callback(choice, self.callback_arg)

        super().short_press()



class SettingsMenu:
    """
    A menu-based GUI for any EuroPi script.

    This class is assumed to be the main interaction method for the program.
    """

    # Treat a long press as anything more than 500ms
    LONG_PRESS_MS = 500

    def __init__(
        self,
        menu_items: list = None,
        navigation_button: europi.Button = europi.b2,
        navigation_knob: europi.Knob = europi.k2,
        short_press_cb=lambda: None,
        long_press_cb=lambda: None,
        autoselect_knob: europi.Knob = europi.k1,
        autoselect_cv: europi.AnalogueInput = europi.ain,
    ):
        """
        Create a new menu from the given specification

        Long/short press callbacks are invoked inside the handler for the falling edge of the button. It is recommended
        to avoid any lengthy operations inside these callbacks, as they may prevent other interrupts from being
        handled properly.

        @param menu_items  A list of MenuItem objects representing the top-level of the menu
        @param navigation_button  The button the user presses to interact with the menu
        @param navigation_knob  The knob the user turns to scroll through the menu. This may be an
                                experimental.knobs.KnobBank with 3 menu levels called "main_menu",
                                "submenu" and "choice", or a raw knob like europi.k2
        @param short_press_cb  An optional callback function to invoke when the user interacts with a short-press of
                               the button
        @param long_press_cb  An optional callback function to invoke when the user interacts with a long-press of
                              the button
        @param autoselect_knob  A knob that the user can turn to select items without needing to menu-dive
        @param autoselect_cv  An analogue input the user can use to select items with CV
        """
        self._knob = navigation_knob
        self.button = navigation_button

        self._ui_dirty = True

        self.short_press_cb = short_press_cb
        self.long_press_cb = long_press_cb

        self.button.handler(self.on_button_press)
        self.button.handler_falling(self.on_button_release)

        self.items = []
        if menu_items:
            for item in menu_items:
                self.items.append(item)

        self.active_items = self.items
        self.active_item = self.knob.choice(self.items)

        self.button_down_at = time.ticks_ms()

        # Indicates to the application that we need to save the settings to disk
        self.settings_dirty = False

        # Iterate through the menu and get all of the config points
        self.config_points_by_name = {}
        self.menu_items_by_name = {}
        for item in self.items:
            item.menu = self

            if type(item) is SettingMenuItem:
                self.config_points_by_name[item.config_point.name] = item.config_point
                self.menu_items_by_name[item.config_point.name] = item

            if item.children:
                for c in item.children:
                    c.menu = self

                    if type(c) is SettingMenuItem:
                        self.config_points_by_name[c.config_point.name] = c.config_point
                        self.menu_items_by_name[c.config_point.name] = c

        # set up a timer for menu items that choose automatically based on the alternate knob or ain
        self.autoselect_cv = autoselect_cv
        self.autoselect_knob = autoselect_knob
        self.autoselect_timer = Timer()
        self.autoselect_cv_items = []
        self.autoselect_knob_items = []

    @property
    def knob(self):
        if type(self._knob) is KnobBank:
            return self._knob.current
        else:
            return self._knob

    def get_config_points(self):
        """
        Get the config points for the menu so we can load/save them as needed
        """
        return list(self.config_points_by_name.values())

    def load_defaults(self, settings_file):
        """
        Load the initial settings from the file

        @param settings_file  The path to a JSON file where the user's settings are saved
        """
        failed_key_counts = {}

        # because we may have a situation where, via callbacks, some settings' options are dynamically
        # modified, we need to load iteratively
        json_data = load_json_file(settings_file)
        keys = list(json_data.keys())
        max_tries = len(keys)
        while len(keys) > 0:
            k = keys[0]
            keys.pop(0)
            if k in self.menu_items_by_name:
                try:
                    self.menu_items_by_name[k].choose(json_data[k])
                except ValueError as err:
                    if k not in failed_key_counts:
                        failed_key_counts[k] = 1
                    else:
                        failed_key_counts[k] += 1
                    # Bump this key to the back and try again; a prior key might fix the problem
                    if failed_key_counts[k] < max_tries:
                        keys.append(k)
                    else:
                        raise

    def save(self, settings_file):
        """
        Save the current settings to the specified file
        """
        data = {}
        for item in self.menu_items_by_name.values():
            data[item.config_point.name] = item.value_choice
        try:
            # ensure the /config directory exists
            # save_to_file won't create it for us!
            os.mkdir("config")
        except OSError:
            pass
        ConfigFile.save_to_file(settings_file, data)
        self.settings_dirty = False

    def on_button_press(self):
        """Handler for the rising edge of the button signal"""
        self.button_down_at = time.ticks_ms()
        self._ui_dirty = True

    def on_button_release(self):
        """Handler for the falling edge of the button signal"""
        self._ui_dirty = True
        if time.ticks_diff(time.ticks_ms(), self.button_down_at) >= self.LONG_PRESS_MS:
            self.long_press()
        else:
            self.short_press()

    def short_press(self):
        """
        Handle a short button press

        This enters edit mode, or applies the selection and
        exits edit mode
        """
        self.active_item.short_press()

        # Cycle the knob bank, if necessary
        if type(self._knob) is KnobBank:
            if self.active_item.is_editable:
                self._knob.set_current("choice")
                if issubclass(type(self.active_item), SettingMenuItem):
                    # lock the knob to our current value
                    self._knob.current.change_lock_value(
                        self.active_item.choices.index(self.active_item.value_choice) /
                            len(self.active_item.choices)
                    )
            elif self.active_item.children and len(self.active_item.children) > 0:
                self._knob.set_current("main_menu")
            else:
                self._knob.set_current("submenu")

        self.short_press_cb()

    def long_press(self):
        """
        Handle a long button press

        This changes between the two menu levels (if possible)
        """
        # exit editable mode when we change menu levels
        self.active_item.is_editable = False

        # we're in the top-level menu; go to the submenu if it exists
        if self.active_items == self.items:
            if self.active_item.children:
                self.active_items = self.active_item.children
                if type(self.knob) is KnobBank:
                    self.knob.set_current("submenu")
        else:
            self.active_items = self.items
            if type(self.knob) is KnobBank:
                self.knob.set_current("main_menu")

        self.long_press_cb()

    def draw(self, oled=europi.oled):
        """
        Draw the menu to the given display

        You should call the display's .fill(0) function before calling this in order to clear the screen. Otherwise
        the menu item will be drawn on top of whatever is on the screen right now. (In some cases this may be the
        desired result, but when in doubt, call oled.fill(0) first).

        You MUST call the display's .show() function after calling this in order to send the buffer to the display
        hardware

        @param oled  The display object to draw to
        """
        if not self.active_item.is_editable:
            self.active_item = self.knob.choice(self.visible_items)
        self.active_item.draw(oled)
        self._ui_dirty = False

    def register_autoselect_cv(self, menu_item: SettingMenuItem):
        """
        Connects a menu item to this menu's CV input

        @param menu_item  The item that wants to subscribe to the CV input
        """
        if len(self.autoselect_cv_items) == 0 and len(self.autoselect_knob_items) == 0:
            self.autoselect_timer.init(freq=10, mode=Timer.PERIODIC, callback=self.do_autoselect)
        self.autoselect_cv_items.append(menu_item)

    def register_autoselect_knob(self, menu_item: SettingMenuItem):
        """
        Connects a menu item to this menu's knob input

        @param menu_item  The item that wants to subscribe to the knob input
        """
        if len(self.autoselect_cv_items) == 0 and len(self.autoselect_knob_items) == 0:
            self.autoselect_timer.init(freq=10, mode=Timer.PERIODIC, callback=self.do_autoselect)
        self.autoselect_knob_items.append(menu_item)

    def unregister_autoselect_cv(self, menu_item: SettingMenuItem):
        """
        Disconnects a menu item to this menu's CV input

        @param menu_item  The item that wants to unsubscribe from the CV input
        """
        self.autoselect_cv_items.remove(menu_item)
        if len(self.autoselect_cv_items) == 0 and len(self.autoselect_knob_items) == 0:
            self.autoselect_timer.deinit()

    def unregister_autoselect_knob(self, menu_item: SettingMenuItem):
        """
        Disconnects a menu item to this menu's knob input

        @param menu_item  The item that wants to unsubscribe from the knob input
        """
        self.autoselect_knob_items.remove(menu_item)
        if len(self.autoselect_cv_items) == 0 and len(self.autoselect_knob_items) == 0:
            self.autoselect_timer.deinit()

    def do_autoselect(self, timer):
        """
        Callback function for the autoselection timer

        Reads from ain and/or the autoselect knob and applies that choice to all subscribed menu items
        """
        if len(self.autoselect_cv_items) > 0:
            ain_percent = self.autoselect_cv.percent()
            for item in self.autoselect_cv_items:
                item.autoselect(ain_percent)

        if len(self.autoselect_knob_items) > 0:
            knob_percent = self.autoselect_knob.percent()
            for item in self.autoselect_knob_items:
                item.autoselect(knob_percent)

    @property
    def ui_dirty(self):
        """
        Is the UI currently dirty and needs re-drawing?

        This will be true if the user has pressed the button or rotated the knob sufficiently
        to change the active item
        """
        return self._ui_dirty or self.active_item.ui_dirty or self.active_item != self.knob.choice(self.visible_items)

    @property
    def visible_items(self):
        """
        Get the set of visible menu items for the current state of the menu

        Menu items can be shown/hidden by setting their is_visible property. Normally this should be done in
        a value-change callback of a menu item to show/hide dependent other items.
        """
        items = []
        for item in self.active_items:
            if item.is_visible:
                items.append(item)
        return items
