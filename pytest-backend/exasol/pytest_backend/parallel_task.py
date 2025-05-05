from __future__ import annotations

import multiprocessing as mp
from contextlib import (
    AbstractContextManager,
    ContextDecorator,
    contextmanager,
)
from functools import wraps
from typing import Any


class _ParallelGenCtxManager(AbstractContextManager, ContextDecorator):

    def __init__(self, func, args, kwargs):
        self._func_name = func.__name__
        self._ctx_func = contextmanager(func)
        self._args = args
        self._kwargs = kwargs
        self._queue = mp.Queue()
        self._ready = mp.Event()
        self._done = mp.Event()

    def _run(self) -> None:
        try:
            with self._ctx_func(*self._args, **self._kwargs) as output:
                # Now the task has completed. Make the results available for
                # caller and indicate the completion.
                # Return None as the error object followed by the function output.
                self._queue.put(None)
                self._queue.put(output)
                self._ready.set()
                # Wait until the caller is done and proceed with the cleanup.
                self._done.wait()
        except Exception as ex:
            # Pass the exception back to the caller and wait until it's done.
            self._queue.put(ex)
            self._ready.set()
            self._done.wait()

    def __enter__(self) -> _ParallelGenCtxManager:
        self._proc: mp.Process = mp.Process(target=self._run)
        self._proc.start()
        # Leave the process running
        return self

    def __exit__(self, *exc) -> None:
        # At this point the task should be completed or the process killed.
        # Indicate the task that it can now clean up and finish.
        self._done.set()
        self._proc.join()
        self._proc.close()

    def wait(self, timeout: float | None = None) -> None:
        if not self._ready.wait(timeout):
            self._proc.kill()
            raise TimeoutError(
                f"{self._func_name} failed to complete within {timeout} seconds"
            )

        # Check if an exception is returned and if so re-raise it
        error = self._queue.get()
        if error is not None:
            raise RuntimeError(f"{self._func_name} failed") from error

    def get_output(self, timeout: float | None = None) -> Any:
        self.wait(timeout)
        return self._queue.get()


def paralleltask(func):
    """
    @paralleltask decorator.

    The decorator starts a long-running function in a separate process. The function
    must be a generator. The targeted use case is a function that builds some kind of
    environment or a data structure, lets the caller use it, and then destroys it.
    Here is a rough pattern of such a function:

    def prepare_something(some_arguments):
        # do the preparation
        yield some_output
        # clean up

    Normally, this function would be used with the help of the @contextmanager decorator.

    @contextmanager
    def prepare_something(some_arguments):
        ...

    with prepare_something(some_arguments) as some_output:
        ...

    This decorator provides similar functionality but runs the function in a separate
    process. It changes the type of the returned output, wrapping it into an object with
    synchronisation functions. The output can be obtained using the get_output([timeout])
    method. This method blocks until the output is ready or the timeout expires. If the
    function produces no output the wait([timeout]) method can be called instead.

    The decorator can be used with session fixtures that want to start bringing up their
    resources in advance, possibly in parallel with each other. Below is a fixture that
    performs all its tasks at once, when it is called. Here we assume that prepare_something
    function is decorated with the @contextmanager.

    @fixture(score="session")
    def some_fixture():
        with prepare_something(...) as some_output:
            yield some_output

    This fixture can be split into two parts. Let's now assume that prepare_something is
    decorated with the @paralleltask.

    @fixture(score="session", autouse=True)
    def some_fixture_async():
        with prepare_something(...) as prep_task:
            yield prep_task

    @fixture(score="session")
    def some_fixture(some_fixture_async):
        return some_fixture_async.get_output()

    The first fixture will start bringing up the resources required for the second fixture.
    All fixtures of the first type should run before any of the fixtures of the second type,
    which is facilitated by the "autouse" parameter.
    """

    @wraps(func)
    def helper(*args, **kwargs):
        return _ParallelGenCtxManager(func, args, kwargs)

    return helper
