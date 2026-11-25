from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from documenthub.core.models import GeneratedDataset
from documenthub.core.registry import FormatRegistry
from documenthub.handlers import build_default_registry
from documenthub.services.generator import SynthenticDataSetGenerator
from documenthub.services.loader import DocumentLoader


class DocumentHub:
    def __init__(self,root:str|Path="/documenthub", *, registry:FormatRegistry|None=None) -> None:
        self.root = Path(root).expanduser().resolve()
        self.registry = registry or build_default_registry()


    @property
    def supported_formats(self)-> tuple[str,...]:
        return self.registry.supported_extension

    def get_directory(self)->Path:
        return self.root

    def get_synthetic_directory(self)->Path:
        """Return the directory containing synthetic datasets."""
        return self.root / "synthetic"

    def get_dataset_directory(self, dataset_id: str)->Path:
        dataset_directory = self.get_synthetic_directory() / dataset_id

        if not dataset_directory.is_dir():
                raise FileNotFoundError(
                    f"Dataset '{dataset_id}' does not exist."
                )

        return dataset_directory

    def get_metadata_directory(self, dataset_id:str|None=None)->Path:
        """
                Return the metadata directory.

                If dataset_id is provided, return that dataset's metadata directory.
                Otherwise, return the root-level metadata directory.
                """
        base_directory = (
            self.get_dataset_directory(dataset_id=dataset_id)
            if dataset_id is not None
            else self.get_directory()
        )
        return base_directory/".documenthub"/"metadata"

    def get_registry(self) -> FormatRegistry:
            """Return the active format registry."""
            return self.registry




    def generate_sample_docs(self, *, count:int, formats: list[str]|None =None, topic:str|list[str]="all",
        seed:int=42, dataset_id:str="synthetic-rag-dataset", overwrite:bool=False)->GeneratedDataset:
            generator = SynthenticDataSetGenerator(self.registry)
            return generator.generate(
                root=self.root,
                count=count,
                formats=formats,
                topic=topic,
                seed=seed,
                dataset_id=dataset_id,
                overwrite=overwrite
            )
    def load(self, path: str | Path| None=None, *, recursive:bool=True,metadata:dict[str,Any]|None=None, strict:bool=True)->list[Document]:
        source = Path(path) if path is not None else self.root
        loader = DocumentLoader(self.registry)
        return loader.load(
            root=source,
            recursive=recursive,
            metadata=metadata,
            strict=strict
        )
