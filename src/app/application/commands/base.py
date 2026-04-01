from __future__ import annotations

from abc import ABC
from argparse import Namespace


class Command(ABC):
    @staticmethod
    def execute(self, args: Namespace) -> int:
        raise NotImplementedError
