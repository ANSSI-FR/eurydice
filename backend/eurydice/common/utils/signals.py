import signal
from typing import Iterable


class BooleanCondition:
    """Object wrapping a boolean with an initial value of `initial_value`.
    Upon reception of a signal referenced in `listen_to` the boolean is set to a value
    opposite to its initial value.

    This class allows for the easy recording of emitted signals.

    Args:
        initial_value: the initial boolean value of the object.
        listen_to: the signals the object must listen and react to.

    Example:
        running = BooleanCondition(initial_value=True, listen_to=(signal.SIGINT,))
        while running:
            do_the_job()

    """

    def __init__(
        self, *, initial_value: bool = True, listen_to: Iterable[signal.Signals] = (signal.SIGINT, signal.SIGTERM)
    ) -> None:
        self._initial_value = initial_value
        self._value = initial_value
        self._attach_handler(listen_to)

    def _attach_handler(self, listen_to: Iterable[int]) -> None:
        """Register function to handle signal reception."""
        for sig in listen_to:
            signal.signal(sig, self._handle_signal)

    def _handle_signal(self, *args, **kwargs) -> None:
        """Method called upon signal reception."""
        self._value = not self._initial_value

    def __bool__(self) -> bool:
        return self._value


__all__ = ("BooleanCondition",)
