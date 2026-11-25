from pathlib import Path
from typing import Protocol

from langchain_core.documents import Document


class DocumentFormattedHandler(Protocol):
    """Interfaces shared by document format handlers."""

    @property
    def extension(self)->tuple[str,...]:
        ...
    def read(self, path:Path)->Document:
        """Read a file and return a Document"""
        ...
    def write(self, path:Path, content:str)->Path:
        """Write text content to a file., and return its path"""
        ...
