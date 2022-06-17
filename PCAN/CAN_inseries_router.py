#!/usr/bin/pthon

try:
    from PCAN.CAN_transceiver import CanTransceiver, CanTransceiverConfig
    from global_config import *
except ModuleNotFoundError:
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from PCAN.CAN_transceiver import CanTransceiver
    from global_config import *
    

import can
    
class CanInSeriesRouter:
    def __init__(self, can_sender_config, can_receiver_config, logger=get_logger("In_series_CAN_router")) -> None:
        if isinstance(can_sender_config, CanTransceiverConfig) and isinstance(can_receiver_config, CanTransceiverConfig):
            self.__can_sender = CanTransceiver(can_sender_config)
            self.__can_receiver = CanTransceiver(can_receiver_config)
        else:
            raise CanException("Invalid constructor CanTransceiver!")
        self.logger = logger
        self.__routing_function = None
        
    def set_routing_function(self, func):
        self.__routing_function = func
        
    def __can_receiver_on_message_callback(self, can_msg):
        if self.__routing_function:
            
            new_can_msg = self.__routing_function(can_msg)
            if isinstance(new_can_msg, can.Message):
                self.__can_sender.send_evt_msg(new_can_msg)
                return
        self.__can_sender.send_evt_msg(can_msg)
        
    def start(self):
        self.__can_sender.start()
        self.__can_receiver.set_on_can_msg_callback(self.__can_receiver_on_message_callback)
        self.__can_receiver.start()
        
    def stop(self):
        self.__can_receiver.stop()
        self.__can_sender.stop()
        
    @property
    def can_sender(self):
        return self.__can_sender
    
    @property
    def can_receiver(self):
        return self.__can_receiver
