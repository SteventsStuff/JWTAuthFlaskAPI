import typing as t
from abc import ABC, abstractmethod


class ABCMapper(ABC):

    @abstractmethod
    def create_payload(self) -> t.Dict[str, t.Any]:
        raise NotImplementedError
