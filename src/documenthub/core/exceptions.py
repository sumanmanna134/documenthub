class DocumentHubError(Exception):
     """Base exception for all DocumentHub errors."""

class UnSupportedFormatError(DocumentHubError):
    """Raised when no handler exists for a file format."""

class DocumentReadError(DocumentHubError):
    """Raised when a document cannot be loaded."""

class DocumentWriteError(DocumentHubError):
    """Raised when a document cannot be written."""

class MetadataError(DocumentHubError):
    """Raised when metadata cannot be read or written."""


class DatasetGenerationError(DocumentHubError):
    """Raised when synthetic dataset generation fails."""
