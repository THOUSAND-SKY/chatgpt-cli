from abc import ABC, abstractmethod


class AbstractCache(ABC):
    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def write(self, history):
        pass

    @abstractmethod
    def load(self):
        pass
