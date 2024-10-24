import multiprocessing
import os
import signal
import time

import pytest

from eurydice.common.utils import signals


def _do_the_job(
    shared_running: multiprocessing.Value,
    ready_condition: multiprocessing.Condition,
) -> None:
    keep_running = signals.BooleanCondition()

    with ready_condition:
        ready_condition.notify()

    while keep_running:
        time.sleep(0.1)

    shared_running.value = int(bool(keep_running))


@pytest.mark.parametrize(
    ("sig", "clean_exit"),
    [(signal.SIGINT, True), (signal.SIGTERM, True), (signal.SIGKILL, False)],
)
def test_boolean_condition_success(sig: signal.Signals, clean_exit: bool):
    ready_condition = multiprocessing.Condition()
    shared_running = multiprocessing.Value("i", -1)
    process = multiprocessing.Process(
        target=_do_the_job, args=(shared_running, ready_condition)
    )

    process.start()
    with ready_condition:
        ready_condition.wait(timeout=5.0)

    os.kill(process.pid, sig)

    process.join()

    assert not process.is_alive()
    if clean_exit:
        assert process.exitcode == 0
        assert shared_running.value == 0
    else:
        assert process.exitcode == -sig
        assert shared_running.value == -1
