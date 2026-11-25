from documenthub.core.exceptions import UnSupportedFormatError
from documenthub.core.protocols import DocumentFormattedHandler


class FormatRegistry:
    def __init__(self):
        self._handlers:dict[str, DocumentFormattedHandler] = {}

    @staticmethod
    def normalized_extension(extension:str)->str:
        normalized = extension.strip().lower()
        if not normalized:
            raise ValueError("File extension cannot be empty")
        return normalized if normalized.startswith(".") else f".{normalized}"
    def register(self, handler:DocumentFormattedHandler, *, replace:bool=False)->None:
        normalized_extn = tuple(self.normalized_extension(handler) for handler in handler.extension)
        if not normalized_extn:
            raise ValueError("A handler must declare at lease one extension")
        duplicates =[extension for extension in normalized_extn if extension in self._handlers and not replace]

        if duplicates:
            raise ValueError("Handler already registered for: "+ ", ".join(duplicates))

        for extension in normalized_extn:
            self._set_extension_in_handlers(extension, handler)

    def _set_extension_in_handlers(self, extension:str, handler:DocumentFormattedHandler):
        self._handlers[extension] = handler

    def get(self, extension:str)->DocumentFormattedHandler:
        """Return the handler for an extension such as '.txt' or 'txt'."""
        normalized = self.normalized_extension(extension)
        try:
            return self._handlers[normalized]
        except KeyError as exc:
            raise UnSupportedFormatError(f"Unsupported document format: {normalized}") from exc

    @property
    def supported_extension(self)->tuple[str,...]:
        return tuple(sorted(self._handlers))
