"""
realtime_detector.py - CAN-Sentinel Week 3: Live Integration

Listens on a Unix Domain Socket for CAN frames forwarded live by
can_sniffer.c (real SocketCAN traffic from vcan0), and runs each one
through the rule-based detector the instant it arrives - true real-time
inference, no polling, no file writes in between.

Run this FIRST (it creates the socket and waits), then start can_sniffer
in another terminal:
    python3 realtime_detector.py
    ./can_sniffer vcan0 /tmp/can_sentinel.sock      (in another terminal)
"""
import socket
import os
import time
from can_detector import detect_intrusion

SOCK_PATH = "/tmp/can_sentinel.sock"


def parse_line(line):
    """'100,8,7,208,0,0,0,0,0,0' -> (can_id:int, dlc:int, data:list[int])"""
    parts = line.strip().split(",")
    can_id = int(parts[0], 16)
    dlc = int(parts[1])
    data = [int(x) for x in parts[2:2 + dlc]] if len(parts) > 2 else []
    return can_id, dlc, data


def main():
    if os.path.exists(SOCK_PATH):
        os.remove(SOCK_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCK_PATH)
    server.listen(1)
    print(f"[DETECTOR] listening on {SOCK_PATH} - waiting for can_sniffer to connect...")

    conn, _ = server.accept()
    print("[DETECTOR] sniffer connected - starting real-time inference\n")

    buf = b""
    count = 0
    alerts = 0
    t_start = time.time()

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
                can_id, dlc, data = parse_line(line.decode())
                result = detect_intrusion(can_id, dlc, data)
                t_done = time.time()
                count += 1
                if "NORMAL" not in result:
                    alerts += 1
                    print(f"  0x{can_id:X} | DLC {dlc} | {result} "
                          f"| inference: {(t_done - t_recv) * 1000:.3f} ms")
    except KeyboardInterrupt:
        pass
    finally:
        elapsed = time.time() - t_start
        print(f"\n[DETECTOR] stopped. {count} frames processed in {elapsed:.1f}s "
              f"({alerts} flagged) - avg {count / elapsed if elapsed else 0:.0f} frames/sec")
        conn.close()
        server.close()
        os.remove(SOCK_PATH)


if __name__ == "__main__":
    main()
