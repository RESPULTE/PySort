import collections


from collections import deque
from typing import Iterable, Any


def exhaust(__i: Iterable) -> None:
    deque(__i, 0)


class OperationLoggingList(list):
    def __init__(self) -> None:
        super().__init__()
        self.num_array_reads = 0
        self.num_array_write = 0

    def reset(self) -> None:
        self.num_array_reads = 0
        self.num_array_write = 0

    def __getitem__(self, __i: int) -> Any:
        self.num_array_reads += 1
        return super().__getitem__(__i)

    def __setitem__(self, __i: int, __val: Any) -> None:
        self.num_array_write += 1
        super().__setitem__(__i, __val)
