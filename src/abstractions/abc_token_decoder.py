from abc import ABC, abstractmethod


class ABCTokenDecoder(ABC):
    @abstractmethod
    def decode_token(self, token: str) -> str:
        pass
