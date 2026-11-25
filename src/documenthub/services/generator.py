import random
import re
from pathlib import Path

from documenthub.core.exceptions import DocumentWriteError
from documenthub.core.metadata import MetadataStore
from documenthub.core.models import GeneratedDataset
from documenthub.core.protocols import DocumentFormattedHandler
from documenthub.core.registry import FormatRegistry
from documenthub.services import get_available_topics
from documenthub.services.template import SyntheticRecord, create_record


class SynthenticDataSetGenerator:
    """Create reproducible fictional datasets for RAG development"""
    def __init__(self, registry:FormatRegistry) -> None:
        self.registry = registry
    def generate(self, *, root:Path, count: int, formats: list[str]| None=None,
        topic: str | list[str]="all", seed:int=42, dataset_id:str="synthetic-rag-dataset", overwrite:bool=False)->GeneratedDataset:
            if count<0:
                raise ValueError("count must be zero or greater")
            if not re.fullmatch(r"[A-Za-z0-9_-]+", dataset_id):
                raise ValueError("dataset_id many contain only letters, numbers, '_', and '-'")
            requested_formats = [self.registry.normalized_extension(item)
                for item in (formats if formats is not None else ["txt"] )]
            if not requested_formats:
                raise ValueError("At least one format required")

            self._check_formats_duplicate(requested_formats)

            for extension in requested_formats:
                self.registry.get(extension)

            ## if topic="all" then list of get_available_topics
            # if topic="topic1" then ["topic1"]
            # if topic=["topic1", "topic2"] then ["topic1", "topic2"]
            selected_topics = self._get_topic(topic)
            if not selected_topics:
                raise ValueError("atleast one topic must be selected")

            self._check_if_topic_is_unknown(selected_topics)
            dataset_directory = root.expanduser().resolve() / "synthetic"/dataset_id
            dataset_directory.mkdir(exist_ok=True, parents=True)
            metadata_store =MetadataStore(dataset_directory)
            rng = random.Random(seed)
            files: list[Path]= []

            self._check_candidate_exists_if_overwrite_false(
                count=count, dataset_directory=dataset_directory, meta_data_store=metadata_store,overwrite=overwrite)

            ## generate each doc
            for index in range(1, count+1):
                choice_topic = rng.choice(selected_topics)
                record = create_record(dataset_id=dataset_id, index=index, topic=choice_topic)
                output_path = dataset_directory/f"{index:05d}.txt"
                sidecard_path = metadata_store.path_for(output_path)

                if self._check_confict(output_path,sidecard_path, overwrite=overwrite):
                    raise FileExistsError(
                            f"Generated output already exists: {output_path}. "
                            "Use overwrite=True or choose a new dataset_id."
                    )

                handler = self.registry.get(output_path.suffix)
                self._write(handler=handler, metadata_store=metadata_store, output_path=output_path, record=record,files=files, dataset_id=dataset_id, index=index, seed=seed)
            return GeneratedDataset(
                    dataset_id= dataset_id,
                    directory=dataset_directory,
                    files=tuple(files)
            )

    def _write(self, *,handler:DocumentFormattedHandler, metadata_store: MetadataStore, output_path:Path,record:SyntheticRecord, files:list[Path], dataset_id:str,index:int,seed:int):
        try:
            handler.write(output_path, record.body)
            metadata_store.write(
                output_path,
                {
                            "document_id": f"{dataset_id}-{index:05d}",
                            "dataset_id": dataset_id,
                            "is_synthetic": True,
                            "topic": record.topic,
                            "seed": seed,
                            "retrieval_test": {
                                "question": record.question,
                                "expected_answer": record.expected_answer,
                            },
                        },

            )
        except Exception as exc:
            output_path.unlink(missing_ok=True)
            raise DocumentWriteError(
                    f"Could not generate synthetic document {index}: {exc}"
                ) from exc
        files.append(output_path)






























    def _check_if_topic_is_unknown(self, selected_topics:list[str])->None:
        unknown = set(selected_topics) - set(get_available_topics())
        if unknown:
            raise ValueError(
                    f"Unknown topics: {sorted(unknown)}. "
                    f"Available: {get_available_topics()}"
                )
    def _get_topic(self,topic:str | list[str]="all" )->list[str]:
        return (
            list(get_available_topics())
            if topic=="all"
            else [topic] if isinstance(topic, str) else list(topic)
        )
    def _check_formats_duplicate(self, requested_formats:list[str]):
        if(len(set(requested_formats))!=len(requested_formats)):
            raise ValueError("Duplicates format not allowed")

    def _check_candidate_exists_if_overwrite_false(self,*, dataset_directory:Path,meta_data_store:MetadataStore, overwrite:bool=False, count:int):
        if not overwrite:
            conflicts=[]
            for index in range(1, count+1):
                candidate = dataset_directory/f"{index:05d}.txt"
                if candidate.exists() or meta_data_store.path_for(candidate).exists():
                    conflicts.append(candidate)
            if conflicts:
                raise FileExistsError(
                    "dataset output already exists. choose another dataset_id "
                    "or pass overwrite=True. First conflict: "
                    f"{conflicts[0]}"
                )
    def _check_confict(self, candidate_path:Path, sidecard_path:Path, *, overwrite:bool=False):
        return not overwrite and (candidate_path.exists() or sidecard_path.exists())
