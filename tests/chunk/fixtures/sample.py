"""Module doc."""
import os
from typing import Any
from dataclasses import dataclass

@dataclass
class DataclassConfig:
    """Dataclass doc."""
    value: int = 0

class PublicClass(Base):
    """Class doc."""

    def public_method(self):
        """Method doc."""
        pass

    def _private_method(self):
        pass

    @property
    def value(self):
        return 1

def public_function():
    """Function doc."""
    pass

def _private_function():
    pass
