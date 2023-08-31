from .parser import LinterParser
from .shfmt import ShfmtParser
from .flakeeight import Flake8Parser
from .shellcheck import ShellCheckParser
from .black import BlackParser

__all__ = [
    "LinterParser",
    "ShfmtParser",
    "Flake8Parser",
    "ShellCheckParser",
    "BlackParser",
]
