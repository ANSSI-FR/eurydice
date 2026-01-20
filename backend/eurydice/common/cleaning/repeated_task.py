import abc
import datetime
import time

from django.db import connections
from django.utils import timezone

from eurydice.common.utils import signals

ONE_SECOND_TIMEDELTA = datetime.timedelta(seconds=1)


class RepeatedTask(abc.ABC):
    """An abstract task that runs indefinitely until signal interruption (SIGINT).
    Inherit this class and implement the `_run` and `_ready` methods with your own
    implementation.
    """

    def __init__(
        self,
        run_every: datetime.timedelta,
        check_if_should_run_every: datetime.timedelta = ONE_SECOND_TIMEDELTA,
    ):
        """
        Args:
            run_every: minimal timedelta between each run. Any call to `_run` beyond
                the first call is guaranteed to happen `run_every` after the previous
                call.
            check_if_should_run_every: delay between checks that trigger a run if the
                `run_every` timedelta has passed. Defaults to 1 second.
        """
        self._last_run_at: datetime.datetime | None = None
        self._run_every = run_every
        self._check_if_should_run_every = check_if_should_run_every.total_seconds()

    @abc.abstractmethod
    def _ready(self) -> None:
        """Called when RepeatedTask is ready, just before first loop. This method is meant
        to be overridden, for example to log that the task is ready to loop.
        Raises NotImplementedError by default. Override this in your own class.
        """
        raise NotImplementedError

    def _should_run(self) -> bool:
        """Determine whether the cleaning task should be run based on the last run of the
        task and the check_if_should_run_every parameter.
        """
        if self._last_run_at is None:
            return True

        return timezone.now() >= self._last_run_at + self._run_every

    @abc.abstractmethod
    def _run(self) -> None:
        """The function to be called each loop, when `_should_run` returns True.
        Raises NotImplementedError by default. Override this in your own class.
        """
        raise NotImplementedError

    def _loop(self) -> None:
        """Loop indefinitely until interrupted, and call `_run` at a given frequency."""
        keep_running = signals.BooleanCondition()

        self._ready()

        while keep_running:
            if self._should_run():
                self._run()
                self._last_run_at = timezone.now()

            time.sleep(self._check_if_should_run_every)

    def start(self) -> None:  # pragma: no cover
        """Entrypoint for the RepeatedTask."""
        try:
            self._loop()
        finally:
            connections.close_all()
