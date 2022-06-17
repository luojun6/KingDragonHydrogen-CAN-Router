#!/usr/bin/pthon

from abc import ABC, abstractmethod


class Service(ABC):
    command = "command"
    command_name = "command_name"
    response = "response"
    response_name = "response_name"
    status = "status"
    data = "data"
    device_message = "device_message"

    def __init__(self, service_id = None):
        if service_id: 
            self.__service_id = service_id
        else:
            self.__service_id = self.__class__

    @abstractmethod
    def execute(self, **kwargs):
        pass

    @property
    def service_id(self):
        return self.__service_id
