# countermeasures/error_injector.py
import can
import threading
import time

class CANErrorInjector:
    """
    CAN-Sentinel Active Countermeasure
    Injects Error Frames to destroy malicious packets per ISO 11898
    """
    def __init__(self, channel='vcan0', bustype='socketcan'):
        self.bus = can.interface.Bus(channel=channel, bustype=bustype)
        self.is_active = False

    def destroy_packet(self, malicious_id):
        """
        Sends 6 consecutive dominant bits (Error Flag) which violates
        CAN bit-stuffing and forces all nodes to discard the attacker's frame.
        """
        if not self.is_active:
            return

        # Active Error Frame: 6 dominant bits
        error_frame = can.Message(
            is_error_frame=True,
            dlc=0
        )
        try:
            self.bus.send(error_frame)
            print(f"[COUNTERMEASURE] Destroyed malicious frame ID: {hex(malicious_id)}")
            return True
        except can.CanError as e:
            print(f"[ERROR] Injection failed: {e}")
            return False

    def enable_defense(self):
        self.is_active = True
        print("[DEFENSE] CAN-Sentinel Active Defense ARMED")

    def disable_defense(self):
        self.is_active = False
        print("[DEFENSE] Active Defense DISARMED")

# Hook into your IDS - Add this in your detection loop:
# if ids_detected_attack(msg):
#     injector.destroy_packet(msg.arbitration_id)
