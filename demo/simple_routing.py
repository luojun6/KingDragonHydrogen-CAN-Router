#!/usr/bin/pthon

try:
    from PCAN.CAN_inseries_router import CanInSeriesRouter
    from PCAN.CAN_transceiver import CanTransceiver, CanTransceiverConfig
    from PCAN.CAN_message import CanMessage
    from global_config import *
except ModuleNotFoundError:
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    from PCAN.CAN_inseries_router import CanInSeriesRouter
    from PCAN.CAN_transceiver import CanTransceiver, CanTransceiverConfig
    from PCAN.CAN_message import CanMessage
    from global_config import *
    
import cantools
import can

dbc_path = os.path.join(ROOT_DIR, r'resource/fcu.dbc')
dbc = cantools.database.load_file(dbc_path)

def get_can_message(dbc, can_frame_id):
    return CanMessage(dbc=dbc, can_id=can_frame_id)

def lower_soc_as_70_percent(msg):
    if isinstance(msg, can.Message): 
        can_data = dbc.decode_message(msg.arbitration_id, msg.data)
        soc = can_data["HydrogenFuelSOC"]
        print(f"[DEBUG] HydrogenFuelSOC before modification: {soc}")
        new_soc = soc * 0.7
        can_data["HydrogenFuelSOC"] = new_soc
        print(f"[DEBUG] HydrogenFuelSOC post modification: {new_soc}")
        
        return can.Message(arbitration_id=msg.arbitration_id, data=dbc.encode_message(msg.arbitration_id, can_data))
    else:
        raise TypeError(f"Inpyt msg is not an instance of {can.Message}")
    
def main():
    
    import time
    
    PERIOD = 0.1
    
    can_sender_config = CanTransceiverConfig(
            channel='vcan1', 
            interface=CanTransceiverConfig.SOCKET_CAN,
            bitrate=CanTransceiverConfig.BAUD_RATE_250K,
            filtered_msg_ids=None,
            record_last_msgs=None,
            logger=get_logger("CAN_in_series_sender"),
            logging_rec_msg=True)
    
    can_receiver_config = CanTransceiverConfig(
            channel='vcan0', 
            interface=CanTransceiverConfig.SOCKET_CAN,
            bitrate=CanTransceiverConfig.BAUD_RATE_250K,
            filtered_msg_ids=None,
            record_last_msgs=True,
            logger=get_logger("CAN_in_series_reciever"),
            logging_rec_msg=True)
    
    
    router = CanInSeriesRouter(can_sender_config=can_sender_config, can_receiver_config=can_receiver_config)
    
    msg = get_can_message(dbc, 0x1891d6d7)
    router.can_receiver.add_periodic_tx_msg(msg=msg.can_msg, period=PERIOD)
    router.start()
    time.sleep(1)
    
    msg.modify_signal(signal_name='MainValveStatus', signal_value=1)
    router.can_receiver.modify_tx_msg(msg.can_msg)
    time.sleep(1)
    
    router.logger.debug("[DEBUG] Loading routing_function: lower_soc_as_70_percent")
    router.set_routing_function(lower_soc_as_70_percent)
    msg.modify_signal(signal_name="HydrogenFuelSOC", signal_value=100)
    router.can_receiver.modify_tx_msg(msg.can_msg)
    time.sleep(0.4)
    msg.modify_signal(signal_name="HydrogenFuelSOC", signal_value=70)
    router.can_receiver.modify_tx_msg(msg.can_msg)
    time.sleep(0.4)
    msg.modify_signal(signal_name="HydrogenFuelSOC", signal_value=40)
    router.can_receiver.modify_tx_msg(msg.can_msg)
    time.sleep(1)
    
    router.stop()
    
if __name__ == '__main__':
    main()
    
    
    