"""One home for how long a thread-stress test is allowed to run.

Why this exists
---------------
The cache suite has a family of race-detector tests built the same way: spin some
mutator threads, run a reader thread a fixed number of rounds asserting an invariant
each time, then stop the mutators. To widen the interleaving window they all call
``sys.setswitchinterval(1e-7)``, which makes the GIL thrash on purpose.

A fixed round count is not a duration -- it is a duration *on the machine it was sized
on*. That distinction is not academic: sized on a many-core dev box,
``test_get_entry_never_raises_under_concurrent_eviction`` measured 16s under coverage
and 8 threads. On a 2-core GitHub runner, with coverage tracing every line in every
thread, the same round count blew the 60s ``pytest-timeout`` ceiling on both 3.11 and
3.12 -- and before the timeout was switched to the ``thread`` method it could not even
be interrupted, so the job ran to GitHub's 6-hour default instead of failing.

A wall-clock budget needs no knowledge of the machine. Fast hardware finishes
``max_rounds``; slow hardware stops at the deadline. Both take about ``budget_s``.

What this does and does not buy
-------------------------------
It bounds **runtime**, not race-detection power, and for these tests the two are close
to independent. Measured on the ``get_entry`` case: with the lock removed, the test
passed 3x at 500 rounds and 3x at 120, with and without coverage. A plain ``dict.get()``
is atomic under the GIL, so the guarded race almost never manifests and detection power
is near zero at every budget tried. Fewer rounds therefore costs approximately nothing
-- but the honest reading of that same measurement is that these tests assert a lock
EXISTS considerably more than they prove the lock is NEEDED. Strengthening them (an
injected switch point inside a check-then-get window) is a real change to security
regression tests and is tracked on its own.

Not every stress loop belongs here. ``test_exact_cache.py`` asserts
``counter[0] >= 3_000`` -- a deliberate did-this-actually-run floor. Deadline-bounding
it would mean weakening that guard, so it keeps its fixed count.
"""

from __future__ import annotations

import time
from typing import Iterator

# The budget every converted stress loop shares. 8s leaves ~7x headroom under the 60s
# per-test ceiling in pyproject.toml, which is enough to absorb both coverage tracing
# and a 2-core runner.
STRESS_BUDGET_S: float = 8.0


def bounded_rounds(max_rounds: int, budget_s: float = STRESS_BUDGET_S) -> Iterator[int]:
    """Yield up to ``max_rounds`` round indices, stopping once ``budget_s`` elapses.

    The deadline is measured from the first call, so each worker thread gets its own
    budget starting when it starts. At least one round always runs -- the clock is
    checked after the body, never before it.
    """
    deadline = time.monotonic() + budget_s
    for index in range(max_rounds):
        yield index
        if time.monotonic() >= deadline:
            return
