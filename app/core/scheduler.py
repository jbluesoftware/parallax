import tkinter as tk
from typing import Callable, Optional


class Scheduler:
    def __init__(self, root: tk.Tk, interval_ms: int = 60000):
        self.root = root
        self.interval_ms = interval_ms
        self._job_id: Optional[str] = None
        self._callback: Optional[Callable[[], None]] = None

    def start(self, callback: Callable[[], None]) -> None:
        self._callback = callback
        self._schedule_next()

    def _schedule_next(self) -> None:
        self._job_id = self.root.after(self.interval_ms, self._run)

    def _run(self) -> None:
        if self._callback:
            self._callback()
        self._schedule_next()

    def stop(self) -> None:
        if self._job_id is not None:
            self.root.after_cancel(self._job_id)
            self._job_id = None
