from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import Namespace


class Command(ABC):
    @abstractmethod
    def execute(self, args: Namespace) -> int:
        raise NotImplementedError
