#!/bin/bash
# CAN-Sentinel - create the virtual CAN interface (vcan0)
# Run with:  sudo ./setup_vcan.sh
set -e

modprobe vcan
# Delete old interface if it exists (ignore errors)
ip link delete vcan0 2>/dev/null || true
ip link add dev vcan0 type vcan
ip link set up vcan0

echo "vcan0 is up:"
ip -details link show vcan0 | head -n 3
