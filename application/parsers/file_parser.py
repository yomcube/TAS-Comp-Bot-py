"""
File Parser
==============================

Module path:
    src/application/parsers/file_parser.py

Summary:
    Delegates parsing to exactly one ParserStrategy, which can
    be swapped at runtime based on competition settings.
"""

from .parser_strategy import ParserStrategy
from domain.entities import SubmissionFile

class FileParser:
    """
    Uses a single ParserStrategy to parse submission files.
    """

    def __init__(self, strategy: ParserStrategy):
        """
        Args:
            strategy (ParserStrategy): the only strategy to use.
        """
        self._strategy = strategy

    def set_strategy(self, strategy: ParserStrategy) -> None:
        """
        Replace the current parsing strategy.

        Args:
            strategy (ParserStrategy): new strategy to use.
        """
        self._strategy = strategy

    def parse(self, file_bytes: bytes, uploaded_at_epoch: int) -> SubmissionFile:
        """
        Attempt to parse using the configured strategy.

        Args:
            file_bytes (bytes): raw bytes of the uploaded file.
            uploaded_at_epoch (int): UNIX timestamp of upload.

        Returns:
            SubmissionFile: parsed domain object.

        Raises:
            ValueError: if the configured strategy does not support these bytes.
        """
        if not self._strategy.supports(file_bytes):
            raise ValueError(
                f"{self._strategy.__class__.__name__} does not support this file format"
            )
        return self._strategy.parse(file_bytes, uploaded_at_epoch)
