"""
CAN-Sentinel: Automotive ECU Intrusion Detection System
Module: CAN Traffic Simulator - Day 4
Project Code: ITS/CS/1076 | Group 1
Domain: Cyber Security
"""

import random
import time
from datetime import datetime
from can_detector import detect_intrusion

# Standard ECU IDs for simulation
ECU_IDS = {
    0x100: "Engine ECU",
    0x200: "Brake ECU",
    0x300: "Transmission ECU",
    0x400: "Steering ECU"
}

# Normal CAN payload range
def generate_normal_frame(can_id, dlc, data):
    """Build the display string for a NORMAL frame.
    can_id/dlc/data are passed in (not re-randomized here) so the printed
    frame always matches what gets sent to the detector."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] ID: 0x{can_id:X} | ECU: {ECU_IDS[can_id]} | DLC: {dlc} | Data: {data} | Status: NORMAL"

# Intrusion / Anomaly frame (for IDS testing)
def generate_anomaly_frame(can_id, dlc, data):
    """Build the display string for an ANOMALY frame.
    Same fix as above: uses the can_id/dlc/data already chosen by the caller."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] ID: 0x{can_id:X} | ECU: UNKNOWN | DLC: {dlc} | Data: {data} | Status: ANOMALY DETECTED"

def make_rpm_bytes(rpm):
    """Pack an RPM value into 2 bytes, big-endian (matches ecu_sim.c's format)."""
    rpm = max(0, min(65535, rpm))
    return [(rpm >> 8) & 0xFF, rpm & 0xFF] + [0] * 6

def run_simulator(num_frames=20):
    print("=== CAN-Sentinel - CAN Bus Traffic Simulator Started ===")
    print(f"Simulating {num_frames} CAN frames...\n")

    for i in range(num_frames):
        # 80% normal, 20% anomaly to test IDS
        roll = random.random()
        if roll < 0.8:
            can_id = random.choice(list(ECU_IDS.keys()))
            dlc = 8
            if can_id == 0x100:
                data = make_rpm_bytes(random.randint(700, 6500))   # realistic RPM
            elif can_id == 0x200:
                data = [random.randint(0, 180)] + [0] * 7          # realistic speed
            else:
                data = [random.randint(0, 255) for _ in range(dlc)]
            frame = generate_normal_frame(can_id, dlc, data)
        elif roll < 0.9:
            # Spoofed value attack: valid ID, but an impossible RPM/Speed value
            can_id = random.choice([0x100, 0x200])
            dlc = 8
            if can_id == 0x100:
                data = make_rpm_bytes(random.randint(20000, 60000))  # impossible RPM
            else:
                data = [random.randint(220, 255)] + [0] * 7          # impossible speed
            frame = generate_anomaly_frame(can_id, dlc, data)
        else:
            can_id = random.choice([0x000, 0x7FF, 0x123])  # Spoofed/unknown IDs
            dlc = random.randint(0, 8)
            data = [random.randint(0, 255) for _ in range(8)]
            frame = generate_anomaly_frame(can_id, dlc, data)

        # Same can_id/dlc/data used in the frame above is now used for detection too
        alert = detect_intrusion(can_id, dlc, data)

        print(f"{i+1}. {frame}")
        print(f"    IDS Result: {alert}")
        time.sleep(0.1)

    print("\n=== Simulation Complete - Log saved for IDS Analysis ===")

if __name__ == "__main__":
    run_simulator()
