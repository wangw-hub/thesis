from pathlib import Path

from ..atomic_write import FAULT_POINTS
from ..exceptions import InjectedStorageFault


class FaultInjector:
    """Single-shot test-only fault hook."""

    def __init__(self, point: str):
        if point not in FAULT_POINTS:
            raise ValueError("unknown fault point")
        self.point = point
        self.triggered = False

    def __call__(self, point: str, temporary: Path, final: Path) -> None:
        if point == self.point and not self.triggered:
            self.triggered = True
            raise InjectedStorageFault(point)
