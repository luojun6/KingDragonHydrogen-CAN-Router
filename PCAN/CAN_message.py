#!/usr/bin/pthon

import decimal
import can


try:
    from global_config import *
except ModuleNotFoundError:
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from global_config import *

class CanMessage:
    def __init__(self, dbc, can_id, init_can_data=None, logger=get_logger("CAN_message")):
        self.logger = logger
        self.__dbc = dbc
        self.__can_id = can_id
        self.__msg_dbc = self.__dbc.get_message_by_frame_id(self.__can_id)
        self.__signal_names = list(
            map(lambda signal: signal.name, self.__msg_dbc.signals))
        self.__msg_name = self.__msg_dbc.name
        self.__period = self.__msg_dbc.cycle_time
        self.__can_data = init_can_data
        self.__extended = self.__msg_dbc.is_extended_frame
        self.__construct_default_msg()

    def modify_signals(self, can_data=None, **signals):
        if can_data is None:
            for signal in signals.keys():
                self.modify_signal(signal_name=signal,
                                   signal_value=signals[signal])
        else:
            for signal in can_data.keys():
                self.modify_signal(signal_name=signal,
                                   signal_value=can_data[signal])
        return self.__can_msg

    def modify_signal(self, signal_name, signal_value):
        try:
            signal = self.__get_signal_by_name(signal_name)
            min_value = signal.minimum
            max_value = signal.maximum
            if min_value and max_value:
                if (signal_value < min_value) or (signal_value > max_value):
                    self.logger.error(f"[{self.__class__}] Out of range input signal value: "
                                      f"{signal_value} from {min_value} to {max_value}!")
                    return -1
            self.__can_data[signal_name] = signal_value
            self.__encode_msg()
            return self.__can_msg
        except IndexError as e:
            self.logger.error(
                f"[{self.__class__}] This message doesn't contain this signal: {signal_name}!", e)
        except TypeError as e:
            self.logger.error(
                f"[{self.__class__}] Invalid input signal value: {signal_value}!", e)

    def __construct_default_msg(self):
        if self.__can_data is None or type(self.__can_data) != dict:
            self.__can_data = dict()
        self.__fill_can_data()
        self.__encode_msg()

    def __fill_can_data(self):
        if len(self.__can_data) < len(self.__signal_names):
            for signal_name in self.__signal_names:
                try:
                    if self.__can_data[signal_name]:
                        pass
                except KeyError:
                    signal = self.__get_signal_by_name(signal_name)
                    if signal.minimum:
                        self.__can_data[signal_name] = signal.minimum
                    else:
                        self.__can_data[signal_name] = 0

    def __get_signal_by_name(self, signal_name):
        signal = list(filter(lambda can_signal: can_signal.name ==
                      signal_name, self.__msg_dbc.signals))[0]
        return signal

    def __encode_msg(self):
        try:
            dbc_data = self.__msg_dbc.encode(self.__can_data)
        except decimal.InvalidOperation:
            dbc_data = self.__msg_dbc.encode(
                self.__can_data, scaling=False, strict=False)
        except decimal.DivisionByZero:
            dbc_data = self.__msg_dbc.encode(
                self.__can_data, scaling=False, strict=False)
        except OverflowError:
            dbc_data = self.__msg_dbc.encode(
                self.__can_data, scaling=False, strict=False)
        self.__can_msg = can.Message(arbitration_id=self.__can_id, data=dbc_data,
                                     is_extended_id=self.__extended)

    @property
    def can_msg(self):
        return self.__can_msg

    @property
    def dbc(self):
        return self.__dbc

    @property
    def msg_name(self):
        return self.__msg_name

    @property
    def period(self):
        return self.__period

    @period.setter
    def period(self, p):
        self.__period = p

    @property
    def can_data(self):
        return self.__can_data

    @property
    def can_id(self):
        return self.__can_id


if __name__ == '__main__':
    import cantools
    import os

    dbc_path = os.path.join(ROOT_DIR, r'resource/fcu.dbc')
    dbc = cantools.database.load_file(dbc_path)

    msg = CanMessage(dbc=dbc, can_id=0x1891d6d7)
    print(f"msg.can_msg: {msg.can_msg}")
    print(f"msg.can_data: {msg.can_data}")

    msg.modify_signal(signal_name='MainValveStatus', signal_value=1)
    print(f"msg.can_data: {msg.can_data}")
    print(dbc.get_message_by_name('HydrogenManagementSystemStatus').encode(msg.can_data))

    can_data = {
        "HydrogenFuelSOC": 74,
        "TubePressure": 10
    }
    msg.modify_signals(can_data=can_data)
    print(f"msg.can_msg: {msg.can_msg}")
    print(f"msg.can_data: {msg.can_data}")

    msg.modify_signals(HMSModeState=2)
    print(f"msg.can_msg: {msg.can_msg}")
    print(f"msg.can_data: {msg.can_data}")
