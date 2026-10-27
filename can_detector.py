from datetime import datetime

# Example rules for simulated CAN traffic
KNOWN_ECU_IDS = {0x100, 0x200, 0x300, 0x400}
SUSPICIOUS_IDS = {0x000, 0x7FF}

# Physically plausible value ranges per ECU (for spoofing/value-based detection)
# RPM (0x100): a real engine idles ~700, redlines ~7000-8000
RPM_MIN, RPM_MAX = 0, 8000
# Speed (0x200): km/h, a realistic road car won't exceed ~200
SPEED_MIN, SPEED_MAX = 0, 200

def detect_intrusion(can_id, dlc, data=None):
    timestamp = datetime.now().strftime("%H:%M:%S")

    if can_id in SUSPICIOUS_IDS:
        return f"[{timestamp}] ALERT: Suspicious CAN ID 0x{can_id:X}"

    if can_id not in KNOWN_ECU_IDS:
        return f"[{timestamp}] WARNING: Unknown CAN ID 0x{can_id:X}"

    if not 0 <= dlc <= 8:
        return f"[{timestamp}] ALERT: Invalid CAN data length"

    # Spoofing / value-plausibility check (only runs if payload data is given)
    if data is not None:
        if can_id == 0x100 and len(data) >= 2:  # Engine RPM, 2 bytes big-endian
            rpm = (data[0] << 8) | data[1]
            if not (RPM_MIN <= rpm <= RPM_MAX):
                return f"[{timestamp}] ALERT: Spoofed RPM value ({rpm}) on ID 0x100"
        elif can_id == 0x200 and len(data) >= 1:  # Speed, 1 byte
            speed = data[0]
            if not (SPEED_MIN <= speed <= SPEED_MAX):
                return f"[{timestamp}] ALERT: Spoofed Speed value ({speed}) on ID 0x200"

    return f"[{timestamp}] NORMAL: Recognized ECU message"


if __name__ == "__main__":
    print("CAN-Sentinel Intrusion Detector")
    can_id = int(input("Enter CAN ID (example: 0x100): "), 16)
    dlc = int(input("Enter data length (0-8): "))
    print(detect_intrusion(can_id, dlc))
