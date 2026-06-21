from abc import ABC, abstractmethod
from app.core.types import ParseResult

class LanguageParser(ABC):
    @abstractmethod
    def parse(self, file_path: str, source_code: str) -> ParseResult:
        raise NotImplementedError

    @property
    @abstractmethod
    def language_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        raise NotImplementedError