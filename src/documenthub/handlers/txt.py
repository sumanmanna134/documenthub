from pathlib import Path

from langchain_core.documents import Document

from documenthub.core.exceptions import DocumentReadError


class TxtHandler:
    @property
    def extension(self)->tuple[str, ...]:
        return (".txt",)

    def read(self, path:Path)->Document:
        # read the doc
        if not path.exists() or not path.is_file():
            raise DocumentReadError(f"TXT file does not exist: {path}")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise DocumentReadError(f"Could not read TXT file: {path}") from exc
        return Document(page_content=text, metadata={"format":"txt"})

    def write(self, path:Path, content: str)->Path:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
            return path
        except OSError as exc:
            raise DocumentReadError(f"Could not write TXT file: {path}") from exc
