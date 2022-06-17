#!/usr/bin/pthon

from abc import ABC, abstractmethod


class Strategy(ABC):
    
    def __init__(self, executor, value=0) -> None:
        super().__init__()
        self.__executor = executor
        self.__value = value
    
    @property
    def executor(self):
        return self.__executor
    
    @property
    def value(self):
        return self.__value
    
    @abstractmethod
    def execute(self):
        pass
    
class StrategyException(Exception):
    pass 