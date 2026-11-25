from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from documenthub.core.exceptions import DocumentReadError
from documenthub.core.metadata import MetadataStore
from documenthub.core.protocols import DocumentFormattedHandler
from documenthub.core.registry import FormatRegistry


class DocumentLoader:
    def __init__(self, registry:FormatRegistry) -> None:
        self.registry=registry
    def load(self, *, root:Path, recursive: bool=True, metadata:dict[str, Any]|None=None, strict:bool=True,)->list[Document]:
        directory = root.expanduser().resolve()
        if not directory.exists():
            raise DocumentReadError(f"Directory does not exist: {directory}")
        if not directory.is_dir():
            raise DocumentReadError(f"Path is not a directory: {directory}")
        # rglob() searches the directory and its nested subdirectories
        # when recursive FALSE, it does not enter nested directories, it will returns immediate contents of the directory
        candidates = directory.rglob("*") if recursive else directory.iterdir()
        supported = set(self.registry.supported_extension)
        paths = sorted(
            (
                path for path in candidates
                if path.is_file()
                and path.suffix.lower() in supported
                and not any(part.startswith(".") for part in path.relative_to(directory).parts[:-1])
            ),
            key=lambda path: path.as_posix().lower()
        )
        ## prepare metadata storage and result collection
        metadata_store = MetadataStore(directory)
        ## in real data, metadata directory may not exist. MetadataStore.read() returns an empty dictionary, when sidecar missing, so the real doc can be still be loaded
        documents:list[Document] = []
        ## load each doc
        for path in paths:
            try:
                handler:DocumentFormattedHandler = self.registry.get(path.suffix)
                document = handler.read(path)
                sidecar_metadata = metadata_store.read(path)
                relative_path = path.relative_to(directory).as_posix()
                document.metadata = {
                    "source": relative_path,
                    **document.metadata,
                    **sidecar_metadata,
                    **(metadata or {}),
                }
                documents.append(document)
            except Exception as exc:
                if strict and isinstance(exc, DocumentReadError):
                    raise DocumentReadError(f"Failed to load '{path}': {exc}") from exc
        return documents
