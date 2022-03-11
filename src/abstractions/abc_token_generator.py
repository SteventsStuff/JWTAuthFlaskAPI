import typing as t
from abc import ABC, abstractmethod


class ABCTokenGenerator(ABC):

    @abstractmethod
    def create_token(self, claims: t.Dict[str, t.Any]) -> str:
        raise NotImplementedError
