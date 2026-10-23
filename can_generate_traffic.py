"""
generate_traffic.py - CAN-Sentinel: simulate CAN bus traffic as CSV data
(no Linux / SocketCAN required - pure Python, runs on Windows)

This mimics what ecu_sim.c + attacker.c would produce if you logged their
real output on Linux. Same CAN IDs, same timing pattern, same attack
behaviour - just generated directly as numbers instead of real sockets.

Produces two files:
    normal_traffic.csv  - ~5000 rows of clean baseline traffic
    attack_traffic.csv  - normal traffic + a brake-flooding attack window

Run:  python generate_traffic.py
"""
import csv
import math
import random

random.seed(42)

# Same 5 ECUs as ecu_sim.c: (CAN ID, period in ms)
ECUS = [
    (0x100, 10),   # RPM
    (0x150, 20),   # Brake status
    (0x200, 20),   # Speed
    (0x300, 50),   # Steering
    (0x400, 100),  # Engine temp
]


def random_payload(n_bytes=8, low_entropy=True):
    """Low-entropy = realistic sensor-ish bytes. High-entropy = random/spoofed."""
    if low_entropy:
        base = random.randint(0, 255)
        return [max(0, min(255, base + random.randint(-3, 3))) for _ in range(n_bytes)]
    else:
        return [random.randint(0, 255) for _ in range(n_bytes)]


def entropy(byte_list):
    """Shannon entropy of the payload bytes (0 = all same, higher = more random)."""
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


def simulate_normal(duration_ms=60000):
    """Simulate normal traffic like ecu_sim.c: fixed IDs at fixed periods."""
    rows = []
    last_seen = {id_: 0 for id_, _ in ECUS}
    for id_, period in ECUS:
        t = 0
        while t < duration_ms:
            payload = random_payload(low_entropy=True)
            inter_arrival = t - last_seen[id_]
            rows.append({
                "timestamp_ms": t,
                "can_id": hex(id_),
                "inter_arrival_ms": inter_arrival,
                "entropy": round(entropy(payload), 3),
                "label": "normal",
            })
            last_seen[id_] = t
            t += period
    rows.sort(key=lambda r: r["timestamp_ms"])
    return rows


def simulate_attack(duration_ms=60000, attack_start_ms=30000, attack_end_ms=40000,
                     attack_interval_ms=1):
    """Normal traffic, but with attacker.c-style flooding of ID 0x150 injected
    between attack_start_ms and attack_end_ms (random high-entropy payload,
    much higher frequency than the real brake ECU)."""
    rows = simulate_normal(duration_ms)
    last_seen_attack = attack_start_ms
    t = attack_start_ms
    while t < attack_end_ms:
        payload = random_payload(low_entropy=False)
        inter_arrival = t - last_seen_attack
        rows.append({
            "timestamp_ms": t,
            "can_id": hex(0x150),
            "inter_arrival_ms": inter_arrival,
            "entropy": round(entropy(payload), 3),
            "label": "attack",
        })
        last_seen_attack = t
        t += attack_interval_ms
    rows.sort(key=lambda r: r["timestamp_ms"])
    return rows


def save_csv(rows, path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp_ms", "can_id", "inter_arrival_ms", "entropy", "label"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {path}")


if __name__ == "__main__":
    normal_rows = simulate_normal(duration_ms=60000)
    save_csv(normal_rows, "normal_traffic.csv")

    attack_rows = simulate_attack(duration_ms=60000, attack_start_ms=30000, attack_end_ms=40000)
    save_csv(attack_rows, "attack_traffic.csv")

    n_attack_frames = sum(1 for r in attack_rows if r["label"] == "attack")
    print(f"\nAttack window: 30000ms-40000ms, {n_attack_frames} spoofed 0x150 frames injected")
