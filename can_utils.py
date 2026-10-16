# can_utils.py - Utility functions for CAN-Sentinel Project
# Author: Ankita - CAN-Sentinel Automotive ECU IDS

import pandas as pd

def load_can_data(file_path):
    """Load CAN bus data from CSV file"""
    try:
        data = pd.read_csv(file_path)
        print(f"Loaded {len(data)} CAN messages")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def filter_can_ids(data, can_id):
    """Filter messages by specific CAN ID"""
    if data is None:
        return None
    filtered = data[data['CAN_ID'] == can_id]
    return filtered

def check_anomaly(can_id, dlc, data_bytes):
    """Basic anomaly check for ECU messages"""
    # DLC should be 0-8 for standard CAN
    if dlc < 0 or dlc > 8:
        return True, "Invalid DLC"
    
    # Check for known malicious CAN IDs (example)
    suspicious_ids = ['0x000', '0x7FF']
    if can_id in suspicious_ids:
        return True, f"Suspicious CAN ID: {can_id}"
        
    return False, "Normal"

if __name__ == "__main__":
    print("CAN-Sentinel Utils Loaded Successfully")
