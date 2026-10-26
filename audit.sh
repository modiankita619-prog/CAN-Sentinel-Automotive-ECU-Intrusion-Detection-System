#!/bin/bash
# CAN-Sentinel Mid-Review "Simulation Audit"
# Proves vcan0 transmits & receives frames with no packet loss.
# Needs: can-utils (sudo apt install can-utils), vcan0 up, ./ecu_sim compiled
# Run:  ./audit.sh [seconds]

DURATION=${1:-10}
RX_LOG=/tmp/rx_audit.log
TX_LOG=/tmp/tx_audit.log

rm -f $RX_LOG $TX_LOG
candump -L vcan0 > $RX_LOG &
CANDUMP_PID=$!
sleep 0.5

timeout -s INT $DURATION ./ecu_sim vcan0 > $TX_LOG
sleep 0.5
kill $CANDUMP_PID 2>/dev/null

SENT=$(grep "TOTAL SENT" $TX_LOG | awk '{print $3}')
RECEIVED=$(wc -l < $RX_LOG)

echo "=============================="
echo " CAN-Sentinel Simulation Audit"
echo "=============================="
echo " Duration         : ${DURATION}s"
echo " Frames sent      : $SENT"
echo " Frames received  : $RECEIVED"
if [ "$SENT" = "$RECEIVED" ]; then
    echo " RESULT           : PASS - 0% packet loss"
else
    echo " RESULT           : MISMATCH - check output"
fi
echo
echo "Sample of raw hex frames:"
head -n 5 $RX_LOG
