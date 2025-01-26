from collections import OrderedDict
from europi import Knob, MAX_UINT16

from experimental.math_extras import median


DEFAULT_THRESHOLD = 0.05


class LockableKnob(Knob):
    """A Knob whose state can be locked on the current value. Once locked, reading the knob's
    position will always return the locked value. When unlocking the knob, the value still doesn't
    change until the position of the knob moves to within ``threshold`` percent of the value. This
    prevents large jumps in a stetting when the knob is unlocked.

    This class is useful for cases where you want to have a single physical knob control several
    parameters (see also the :class:`KnobBank` class). Or where the value of a parameter needs to be
    disassociated from the position of the knob, as in after loading saved state.

    This class accepts two different parameters to specify it's initial value,
    `initial_uint16_value` and `initial_percentage_value`. Only one initial value may be specified.
    If both are specified, `initial_percentage_value` is ignored. The percentage value is more
    useful if you would like to hardcode a starting value for a knob in the code in a readable way.
    The uint16 value uses the knob's internal representation and is more appropriate for use when
    loading a saved knob position. If your script would like to read the internal representation of
    current position of a `LockableKnob`, first lock the knob, then read it's value.::

        lockable_knob.lock()
        internal_rep = lockable_knob.value

    :param knob: The knob to wrap.
    :param initial_uint16_value: The UINT16 (0-`europi.MAXINT16`) value to lock the knob at. If a value is provided the new knob is locked, otherwise it is unlocked.
    :param initial_percentage_value: The percentage (as a decimal 0-1) value to lock the knob at. If a value is provided the new knob is locked, otherwise it is unlocked.
    :param threshold: a decimal between 0 and 1 representing how close the knob must be to the locked value in order to unlock. The percentage is in terms of the knobs full range. Defaults to 5% (0.05)
    """

    STATE_UNLOCKED = 0
    STATE_UNLOCK_REQUESTED = 1
    STATE_LOCKED = 2

    def __init__(
        self,
        knob: Knob,
        initial_percentage_value=None,
        initial_uint16_value=None,
        threshold_percentage=DEFAULT_THRESHOLD,
    ):
        super().__init__(knob.pin_id)
        self.pin = knob.pin  # Share the ADC

        if initial_uint16_value != None:
            self.value = initial_uint16_value
            self.state = LockableKnob.STATE_LOCKED
        elif initial_percentage_value != None:
            self.value = (1 - initial_percentage_value) * MAX_UINT16
            self.state = LockableKnob.STATE_LOCKED
        else:
            self.value = MAX_UINT16  # Min value
            self.state = LockableKnob.STATE_UNLOCKED

        self.threshold = int(threshold_percentage * MAX_UINT16)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.pin}, {self.value}, {self.state})"

    def _sample_adc(self, samples=None):
        if self.state == LockableKnob.STATE_LOCKED:
            return self.value

        elif self.state == LockableKnob.STATE_UNLOCKED:
            return super()._sample_adc(samples)

        else:  # STATE_UNLOCK_REQUESTED:
            current_value = super()._sample_adc(samples)
            if abs(self.value - current_value) < self.threshold:
                self.state = LockableKnob.STATE_UNLOCKED
                return current_value
            else:
                return self.value

    def lock(self, samples=None):
        """Locks this knob at its current state. Makes a call to the underlying knob's
        ``_sample_adc()`` method with the given number of samples."""
        self.value = self._sample_adc(samples=samples)
        self.state = LockableKnob.STATE_LOCKED

    def change_lock_value(self, percent=0.0):
        """Change the current value to reflect a desired percentage

        @param percent  The 0-1 value we want to re-lock the knob at
        """
        self.value = int(MAX_UINT16 * (1.0-percent))

    def request_unlock(self):
        """Requests that the knob be unlocked. The knob will unlock the next time a reading of it's
        position is taken that is withing the threshold percentage of the locked value. That is,
        when the knob is moved close to the locked value. If :meth:`~LockableKnob.lock()` is called
        before the knob unlocks, the unlock is aborted.
        """
        if self.state == LockableKnob.STATE_LOCKED:
            self.state = LockableKnob.STATE_UNLOCK_REQUESTED


class DisabledKnob(LockableKnob):
    """A :class:`LockableKnob` that cannot be unlocked and whose value is unimportant. Useful when
    building multifunction knobs.

    :param knob: The knob to wrap."""

    def __init__(self, knob: Knob):
        super().__init__(knob, initial_uint16_value=MAX_UINT16)

    def request_unlock(self):
        """LockedKnob can never be unlocked"""
        return


class KnobBank:
    """A ``KnobBank`` is a group of named 'virtual' :class"``LockableKnobs`` that share the same
    physical knob. Only one of these knobs is active (unlocked) at a time. This allows for a single
    knob to be used to control many parameters.

    It is recommended that ``KnobBanks`` be created using the :class:``Builder``, as in::

       k1_bank = (
           KnobBank.builder(k1)
           .with_disabled_knob()
           .with_unlocked_knob("x", threshold=0.02)
           .with_locked_knob("y", initial_percentage_value=1)
           .build()
       )

    Knobs can be referenced using their names::

       k1_bank.x.percent()
       k1_bank.y.read_position()

    .. note::
       ``KnobBank`` is not thread safe. It is possible to end up with two unlocked knobs if you call
       :meth:`~KnobBank.next()` and take readings from a knob in two different threads. This can
       easily happen if your script calls ``next()`` in a button handler, while constantly reading
       the knob state in a main loop. The workaround is to set a flag in the button handler and call
       ``next()`` in the main loop.

       For example::

          class KnobBankExample(EuroPiScript):
              def __init__(self):
                  super().__init__()
                  self.next_k1 = False

                  self.kb1 = (
                      KnobBank.builder(k1)
                      .with_locked_knob("p1", initial_percentage_value=1, threshold_percentage=0.02)
                      .with_locked_knob("p2", initial_percentage_value=1)
                      .with_locked_knob("p3", initial_percentage_value=1)
                      .build()
                  )

                  @b1.handler
                  def next_knob1():
                      self.next_k1 = True

              def main(self):

                  while True:
                      if self.next_k1:
                          self.kb1.next()
                          self.next_k1 = False

                      # main loop body
    """

    def __init__(self, physical_knob: Knob, virtual_knobs, initial_selection) -> None:
        self.index = 0
        self.knobs = []
        self.names = []

        for name, knob in virtual_knobs.items():
            setattr(self, name, knob)  # make knob available by its name
            self.knobs.append(knob)
            self.names.append(name)
        self.knobs[initial_selection].request_unlock()
        self.index = initial_selection

    @property
    def current(self) -> LockableKnob:
        """The currently active knob."""
        return self.knobs[self.index]

    @property
    def current_name(self) -> str:
        return self.names[self.index]

    def next(self):  # potential race condition: next() and _sample_adc() can both change state
        """Select the next knob by locking the current knob, and requesting an unlock on the next in
        the bank."""
        self.current.lock()
        self.index = (self.index + 1) % len(self.knobs)
        self.current.request_unlock()

    def set_current(self, name):
        """Set the currently-unlocked knob to the one whose name matches the argument

        @param name  The name of the knob to set as the current one
        """
        try:
            index = self.names.index(name)
            self.current.lock()
            self.index = index
            self.current.request_unlock()
        except ValueError:
            # if the name isn't found, just silently trap the exception
            pass

    def __getitem__(self, name):
        """Get the LockableKnob in this bank with the given name

        @param name  The name of the knob to return, or None if the name isn't found
        """
        try:
            index = self.names.index(name)
            return self.knobs[index]
        except ValueError:
            return None

    class Builder:
        """A convenient interface for creating a :class:`KnobBank` with consistent initial state."""

        def __init__(self, knob: Knob) -> None:
            self.knob = knob
            self.knobs_by_name = OrderedDict()
            self.initial_index = None

        def with_disabled_knob(self) -> "Builder":
            """Add a :class:`DisabledKnob` to the bank. This disables the knob so that no parameters can
            be changed."""
            self.knobs_by_name[DisabledKnob.__name__] = DisabledKnob(self.knob)
            return self

        def with_locked_knob(
            self,
            name: str,
            initial_percentage_value=None,
            initial_uint16_value=None,
            threshold_percentage=None,
            threshold_from_choice_count=None,
        ) -> "Builder":
            """Add a :class:`LockableKnob` to the bank whose initial state is locked.

            `threshold_from_choice_count` is a convenience parameter to be used in the case where
            this knob will be used to select from a relatively few number of choices, via the
            :meth:`~europi.Knob.choice()` method. Pass the number of choices to this parameter and
            an appropriate threshold value will be calculated.

            :param name: the name of this virtual knob
            :param threshold_percentage: the threshold percentage for this knob as described by :class:`LockableKnob`
            :param threshold_from_choice_count: Provides the number of choices this knob will be used with in order to generate an appropriate threshold.
            """
            if initial_uint16_value is None and initial_percentage_value is None:
                raise ValueError(
                    "initial_percentage_value and initial_uint16_value cannot both be None"
                )

            return self._with_knob(
                name,
                initial_percentage_value=initial_percentage_value,
                initial_uint16_value=initial_uint16_value,
                threshold_percentage=threshold_percentage,
                threshold_from_choice_count=threshold_from_choice_count,
            )

        def with_unlocked_knob(
            self,
            name: str,
            threshold_percentage=None,
            threshold_from_choice_count=None,
        ) -> "Builder":
            """Add a :class:`LockableKnob` to the bank whose initial state is unlocked. This knob
            will be active. Only one unlocked knob may be added to the bank.

            `threshold_from_choice_count` is a convenience parameter to be used in the case where
            this knob will be used to select from a relatively few number of choices, via the
            :meth:`~europi.Knob.choice()` method. Pass the number of choices to this parameter and
            an appropriate threshold value will be calculated.

            :param name: the name of this virtual knob
            :param threshold_percentage: the threshold percentage for this knob as described by :class:`LockableKnob`
            :param threshold_from_choice_count: Provides the number of choices this knob will be used with in order to generate an appropriate threshold.

            """
            if self.initial_index != None:
                raise ValueError(f"Second unlocked knob specified: {name}")

            self._with_knob(name, None, None, threshold_percentage, threshold_from_choice_count)

            self.initial_index = len(self.knobs_by_name) - 1

            return self

        def _with_knob(
            self,
            name: str,
            initial_percentage_value,
            initial_uint16_value,
            threshold_percentage,
            threshold_from_choice_count=None,
        ):
            if name == None:
                raise ValueError("Knob name cannot be None")

            if threshold_percentage != None and threshold_from_choice_count != None:
                raise ValueError(
                    "Specify only one of either threshold_percentage or threshold_from_choice_count not both"
                )

            if threshold_from_choice_count != None:
                threshold_percentage = 1 / threshold_from_choice_count

            elif threshold_percentage == None:
                threshold_percentage = DEFAULT_THRESHOLD

            self.knobs_by_name[name] = LockableKnob(
                self.knob,
                initial_percentage_value=initial_percentage_value,
                initial_uint16_value=initial_uint16_value,
                threshold_percentage=threshold_percentage,
            )

            return self

        def build(self) -> "KnobBank":
            """Create the :class:`KnobBank` with the specified knobs."""
            if len(self.knobs_by_name) < 0:
                raise ValueError(f"Must specify at least one knob in the bank.")
            if self.initial_index == None:
                self.initial_index = 0
            return KnobBank(
                physical_knob=self.knob,
                virtual_knobs=self.knobs_by_name,
                initial_selection=self.initial_index,
            )

    @staticmethod
    def builder(knob: Knob) -> Builder:
        return KnobBank.Builder(knob)


class BufferedKnob(Knob):
    """A wrapper for a Knob instance whose value remains fixed until .update(...) is called

    This allows multiple uses of .percent(), .choice(...), etc... without forcing a re-read of
    the ADC value
    """

    def __init__(self, knob):
        """Create a buffered wrapper for the given analogue input

        The parameter @knob can be any Knob instance, including:
        - europi.k1
        - europi.k2

        Until the .update() method is called, this class will return a value of 0.

        @param knob The analogue input to wrap e.g.:
                    ```python
                    from europi import *
                    from experimental.knobs import *
                    k1_buffered = BufferedKnob(k1)
                    ```
        """
        super().__init__(knob.pin_id)
        self.value = 0

    def _sample_adc(self, samples=None):
        """Overrides the internal function that samples the ADC

        Instead of sampling we simply return the most recent sample value

        @param samples  Ignored, but needed by the _sample_adc API used by AnalogueReader
        """
        return self.value

    def update(self, samples=None):
        """Re-read the ADC and update the buffered value

        @param samples  Specifies the number of samples to average to de-noise the ADC reading
                        See europi.AnalogueReader for details on ADC sampling
        """
        self.value = super()._sample_adc(samples)


class MedianAnalogInput:
    """A wrapper for an analogue input (e.g. knob, ain) that provides additional smoothing & debouncing

    This class uses a window of the n latest samples from the underlying input and uses the median of
    those samples. Larger window sizes will produce a more stable output, but at the cost of slowing
    down reaction time to changes.
    """

    def __init__(self, analog_in, samples=100, window_size=5):
        """Create the wrapper

        @param analog_in    The input we're wrapping (e.g. k1, k2, ain)
        @param samples      The number of samples to use when reading from analog_in
        @param window_size  The number of samples used for calculating the median
        """
        self.analog_in = analog_in
        self.n_samples = samples
        self.window_size = window_size

        self.samples = []

    def percent(self):
        """Read the hardware percentage and apply our additional smoothing

        Smoothing is done using a simple 5-window median filter
        """
        self.samples.append(self.analog_in.percent(self.n_samples))

        if len(self.samples) > self.window_size:
            self.samples.pop(0)

        return median(self.samples)
