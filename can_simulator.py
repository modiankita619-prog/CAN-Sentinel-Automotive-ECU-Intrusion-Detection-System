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
def generate_normal_frame(can_id, dlc):
    """Build the display string for a NORMAL frame.
    can_id/dlc are passed in (not re-randomized here) so the printed
    frame always matches what gets sent to the detector."""
    data = [random.randint(0, 255) for _ in range(dlc)]
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] ID: 0x{can_id:X} | ECU: {ECU_IDS[can_id]} | DLC: {dlc} | Data: {data} | Status: NORMAL"

# Intrusion / Anomaly frame (for IDS testing)
def generate_anomaly_frame(can_id, dlc):
    """Build the display string for an ANOMALY frame.
    Same fix as above: uses the can_id/dlc already chosen by the caller."""
    data = [random.randint(0, 255) for _ in range(8)]
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] ID: 0x{can_id:X} | ECU: UNKNOWN | DLC: {dlc} | Data: {data} | Status: ANOMALY DETECTED"

def run_simulator(num_frames=20):
    print("=== CAN-Sentinel - CAN Bus Traffic Simulator Started ===")
    print(f"Simulating {num_frames} CAN frames...\n")

    for i in range(num_frames):
        # 80% normal, 20% anomaly to test IDS
        if random.random() < 0.8:
            can_id = random.choice(list(ECU_IDS.keys()))
            dlc = 8
            frame = generate_normal_frame(can_id, dlc)
        else:
            can_id = random.choice([0x000, 0x7FF, 0x123])  # Spoofed/unknown IDs
            dlc = random.randint(0, 8)
            frame = generate_anomaly_frame(can_id, dlc)

        # Same can_id/dlc used in the frame above is now used for detection too
        alert = detect_intrusion(can_id, dlc)

        print(f"{i+1}. {frame}")
        print(f"    IDS Result: {alert}")
        time.sleep(0.5)

    print("\n=== Simulation Complete - Log saved for IDS Analysis ===")

if __name__ == "__main__":
    run_simulator()
