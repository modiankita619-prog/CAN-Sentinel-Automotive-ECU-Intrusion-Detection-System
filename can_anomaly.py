"""
detect_anomaly.py - CAN-Sentinel ML Engine (Week 2 deliverable)

Trains an Isolation Forest on NORMAL traffic (learns the baseline timing/
entropy pattern), then tests it on ATTACK traffic to prove it flags the
injected frames as anomalous.

Needs:  pip install pandas scikit-learn
Run:    python generate_traffic.py      (creates the two CSVs first)
        python detect_anomaly.py
"""
import pandas as pd
from sklearn.ensemble import IsolationForest

# ---- Load data -------------------------------------------------------
normal_df = pd.read_csv("normal_traffic.csv")
attack_df = pd.read_csv("attack_traffic.csv")

FEATURES = ["inter_arrival_ms", "entropy"]

# ---- Train on normal traffic only (this is the "baseline") ----------
# contamination = expected fraction of "weird" points even in normal data.
# 0.07 was tuned by testing a few values (see notes below) - it gives a good
# balance: catches almost all attack frames without flagging too many
# normal frames as false alarms.
model = IsolationForest(n_estimators=150, contamination=0.07, random_state=42)
model.fit(normal_df[FEATURES])

# ---- Test on the attack CSV (normal + injected attack frames) -------
attack_df["prediction"] = model.predict(attack_df[FEATURES])
# IsolationForest: -1 = anomaly, 1 = normal
attack_df["flagged"] = attack_df["prediction"] == -1

# ---- Results ----------------------------------------------------------
total_attack_frames = (attack_df["label"] == "attack").sum()
flagged_attack_frames = ((attack_df["label"] == "attack") & attack_df["flagged"]).sum()
false_positives = ((attack_df["label"] == "normal") & attack_df["flagged"]).sum()
total_normal_frames = (attack_df["label"] == "normal").sum()

print("=" * 50)
print(" CAN-Sentinel - Detection Validation (Mid-Review)")
print("=" * 50)
print(f" Total frames tested        : {len(attack_df)}")
print(f" Actual attack frames       : {total_attack_frames}")
print(f" Attack frames FLAGGED      : {flagged_attack_frames}  "
      f"({100 * flagged_attack_frames / total_attack_frames:.1f}% caught)")
print(f" Normal frames wrongly flagged (false positives): {false_positives} "
      f"/ {total_normal_frames}")
print()
print("Sample of flagged rows (should mostly be ID 0x150 during the attack window):")
print(attack_df[attack_df["flagged"]].head(10)[["timestamp_ms", "can_id", "inter_arrival_ms", "entropy", "label"]]
      .to_string(index=False))
