"""
realtime_ml_detector.py - CAN-Sentinel Week 3: Live Integration (ML version)

This is the PROPER version of Live Integration, matching the project spec
exactly: "Connect the live C-based sniffer directly to the Python ML model
using Unix Domain Sockets for sub-millisecond, real-time inference."

Unlike realtime_detector.py (which uses the simple rule-based detector),
this script feeds each live frame's computed features - inter-arrival time
and payload entropy - into the ACTUAL trained Isolation Forest model
(the same one trained in detect_anomaly.py / can_anomaly.py), live,
frame by frame, with no batching and no CSV in between.

Needs:  pip install pandas scikit-learn joblib
        A trained model file: can_sentinel_model.pkl (see train_model.py)

Run this FIRST, then start can_sniffer in another terminal:
    python3 realtime_ml_detector.py
    ./can_sniffer vcan0 /tmp/can_sentinel.sock      (in another terminal)
"""
import socket
import os
import time
import math
import joblib
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

FEATURES = ["inter_arrival_ms", "entropy"]

SOCK_PATH = "/tmp/can_sentinel.sock"
MODEL_PATH = "can_sentinel_model.pkl"

# Tracks the last time each CAN ID was seen, to compute inter-arrival time live
last_seen = {}


def entropy(byte_list):
    """Shannon entropy of the payload bytes - same formula as training time."""
    if not byte_list:
        return 0.0
    counts = {}
    for b in byte_list:
        counts[b] = counts.get(b, 0) + 1
    n = len(byte_list)
    ent = 0.0
    for c in counts.values():
        p = c / n
        ent -= p * math.log2(p)
    return ent


def parse_line(line):
    """'100,8,7,208,0,0,0,0,0,0' -> (can_id:int, dlc:int, data:list[int])"""
    parts = line.strip().split(",")
    can_id = int(parts[0], 16)
    dlc = int(parts[1])
    data = [int(x) for x in parts[2:2 + dlc]] if len(parts) > 2 else []
    return can_id, dlc, data


def main():
    model = joblib.load(MODEL_PATH)
    print(f"[ML-DETECTOR] loaded model from {MODEL_PATH}")

    if os.path.exists(SOCK_PATH):
        os.remove(SOCK_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCK_PATH)
    server.listen(1)
    print(f"[ML-DETECTOR] listening on {SOCK_PATH} - waiting for can_sniffer to connect...")

    conn, _ = server.accept()
    print("[ML-DETECTOR] sniffer connected - starting LIVE ML inference\n")

    buf = b""
    count = 0
    flagged = 0
    t_program_start = time.time()
    start_ms = None

    try:
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                if not line:
                    continue

                t_recv = time.time()
                if start_ms is None:
                    start_ms = t_recv
                now_ms = (t_recv - start_ms) * 1000

                can_id, dlc, data = parse_line(line.decode())

                # --- live feature extraction (mirrors training-time features) ---
                prev = last_seen.get(can_id, now_ms)
                inter_arrival = now_ms - prev
                last_seen[can_id] = now_ms
                ent = entropy(data)

                X = pd.DataFrame([[inter_arrival, ent]], columns=FEATURES)
                score = model.decision_function(X)[0]
                is_anomaly = model.predict(X)[0] == -1

                t_done = time.time()
                count += 1

                if is_anomaly:
                    flagged += 1
                    print(f"  0x{can_id:X} | inter_arrival={inter_arrival:.2f}ms | "
                          f"entropy={ent:.2f} | score={score:.3f} | ML ALERT "
                          f"| inference: {(t_done - t_recv) * 1000:.3f} ms")
    except KeyboardInterrupt:
        pass
    finally:
        elapsed = time.time() - t_program_start
        print(f"\n[ML-DETECTOR] stopped. {count} frames processed in {elapsed:.1f}s "
              f"({flagged} flagged, {100*flagged/count if count else 0:.1f}%) "
              f"- avg {count / elapsed if elapsed else 0:.0f} frames/sec")
        conn.close()
        server.close()
        if os.path.exists(SOCK_PATH):
            os.remove(SOCK_PATH)


if __name__ == "__main__":
    main()
