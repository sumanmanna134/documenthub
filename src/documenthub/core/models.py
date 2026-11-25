from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class GeneratedDataset:
    """Description of a synthetic dataset created by DocumentHub"""
    dataset_id: str
    directory: Path
    files: tuple[Path,...]

    @property
    def count(self)->int:
        return len(self.files)
