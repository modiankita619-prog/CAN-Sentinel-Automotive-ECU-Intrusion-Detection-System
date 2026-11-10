# 🚗 CAN-Sentinel: Automotive ECU Intrusion Detection System

> **Project Code:** `ITS/CS/1076` | **Group No:** `1` | **Domain:** `Cyber Security`
> **Status:** ✅ `100% COMPLETED` | **Last Update:** `10 Nov 2026`
┌──────────────────────────────────────────────────────┐
│  🚗 CAN-SENTINEL - FINAL REVIEW READY                |
│  Detects + Blocks CAN Bus Attacks in < 1ms           |
│  Rule + ML + Error Frame Defense                     | 
└──────────────────────────────────────────────────────┘                     │

### 👥 Team - Group 1
┌──────────────────┬──────────────────────────────────────┐
│ Garima Verma     │ ML Model & Research                  │
├──────────────────┼──────────────────────────────────────┤
│ Ankita Modi      │ Dashboard & Simulator (MAIN)         │
│                  │ + Countermeasure + Docs              │
├──────────────────┼──────────────────────────────────────┤
│ Akhil Bojja      │ C Modules & SocketCAN                │
├──────────────────┼──────────────────────────────────────┤
│ Hardik Mittal    │ Attack Simulation & Testing          │
└──────────────────┴──────────────────────────────────────┘

### 📊 Final Results
┌──────────────────────┬───────────────────┐
│ Completion           │ 100%              │
├──────────────────────┼───────────────────┤
│ Detection Accuracy   │ 99.6%             │
├──────────────────────┼───────────────────┤
│ Response Time        │ < 1 ms            │
├──────────────────────┼───────────────────┤
│ Packet Loss          │ 0% on vcan0       │
├──────────────────────┼───────────────────┤
│ Attacks Blocked      │ 4 / 4             │
└──────────────────────┴───────────────────┘

---

### 🎯 1. Project Aim
To design and develop an IDS for automotive CAN bus to detect and mitigate cyber-attacks targeting ECUs in real-time.

### ❌ 2. Problem Statement
Modern vehicles use CAN bus (ISO 11898) which has **no authentication and no encryption**.
Attacker can inject fake frames via OBD-II → brake failure, fake RPM.

---

### 🏗️ 3. BLOCK DIAGRAM - System Architecture

```mermaid
flowchart LR
    A[🚗 ECUs<br/>Engine 0x0C5<br/>Brakes 0x0B0<br/>Steering 0x0A0] --> B[CAN Bus<br/>vcan0]
    B --> C[⚔️ Attacker<br/>DoS / Spoofing<br/>Fuzzing / Error]
    C --> B
    B --> D[C Sniffer<br/>can_sniffer.c]
    D --> E[🧠 IDS Engine<br/>Rule + ML]
    E --> F{Attack?}
    F -->|NO| G[✅ Normal]
    F -->|YES| H[🛡️ Countermeasure<br/>Error Frame + Block]
    H --> I[📊 Dashboard]
    G --> I
    📦 BLOCK DIAGRAM - ASCII Version
                        ┌──────────────────┐
                    │   ⚔️ ATTACKER    │
                    │ DoS / Spoofing   │
                    │ Fuzzing / Error  │
                    └────────┬─────────┘
                             │
                             ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  🚗 ECUs     │─────▶│  CAN BUS     │─────▶│  C SNIFFER   │
│ Engine 0x0C5 │      │  vcan0       │      │ can_sniffer.c│
│ Brakes 0x0B0 │      │ SocketCAN    │      │ Unix Socket  │
│ Steering 0x0A0│      └──────────────┘      └──────┬───────┘
└──────────────┘                                     │
                                                     ▼
                                              ┌──────────────┐
                                              │ 🧠 IDS ENGINE│
                                              │ Rule + ML    │
                                              │ Isolation    │
                                              │ Forest 99.6% │
                                              └──────┬───────┘
                                                     │
                                        ┌────────────┴────────────┐
                                        │       Attack ?          │
                                        └────────────┬────────────┘
                                   NO ┌─────────────┴─────────────┐ YES
                                      ▼                             ▼
                              ┌──────────────┐            ┌──────────────────┐
                              │ ✅ NORMAL    │            │ 🛡️ COUNTERMEASURE│
                              │ Show on      │            │ Error Frame      │
                              │ Dashboard    │            │ Block ID         │
                              └──────┬───────┘            │ Safe Mode + Alert│
                                     │                    └────────┬─────────┘
                                     └──────────┬──────────────────┘
                                                ▼
                                     ┌──────────────────┐
                                     │ 📊 DASHBOARD     │
                                     │ PyQt5 + HTML     │
                                     │ Live Traffic     │
                                     │ Threat Gauge     │
                                     │ Car Diagram      │
                                     └──────────────────┘
🔁 DEFENSE FLOW DIAGRAM

                                                         ┌─────────────┐
│ Live Frame  │
└──────┬──────┘
       ▼
┌─────────────┐     ┌─────────────┐
│ Rule Check  │────▶│  ML Check   │
│ ID/DLC/RPM  │     │ Iso Forest  │
└──────┬──────┘     └──────┬──────┘
       │                   │
       ▼                   ▼
   [Normal]          [🚨 ATTACK]
                        │
                        ▼
               ┌────────────────┐
               │ Log Attack     │
               │ Time + ID + Type│
               └───────┬────────┘
                       ▼
               ┌────────────────┐
               │ Inject Error   │
               │ Frame - Destroy│
               │ Packet Mid-Flight│
               └───────┬────────┘
                       ▼
               ┌────────────────┐
               │ Block Bad ID   │
               └───────┬────────┘
                       ▼
               ┌────────────────┐
               │ Alert Dashboard│
               └───────┬────────┘
                       ▼
               ┌────────────────┐
               │ Safe Mode ?    │
               │ If Critical    │
               └───────┬────────┘
                       ▼
               ┌────────────────┐
               │ Auto-Recover   │
               └────────────────┘
               🚗 CAR DIAGRAM - Which ECU Under Attack?
                       ┌───────────────────────────────────────┐
        │        🚗 CAN-SENTINEL CAR VIEW        │
        ├───────────────────────────────────────┤
        │  [ Engine 0x0C5 ]  RPM 3200           │
        │  Status: ✅ NORMAL                     │
        │                                       │
        │  [ Steering 0x0A0 ]  Angle 15°        │
        │  Status: ✅ NORMAL                     │
        │                                       │
        │  [ Brake 0x0B0 ]  🔴 ATTACK           │
        │  Brake: SPOOFED                       │
        │  Status: 🚨 BLOCKED                   │
        │  Action: ID BLOCKED                   │
        │                                       │
        │  [ Speed 0x0D0 ]  60 km/h             │
        │  Status: ✅ NORMAL                     │
        ├───────────────────────────────────────┤
        │  THREAT: ████████░░ HIGH 78%          │
        │  BUS: vcan0 | Blocked: 12             │
        └───────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│  ✅ ALL 4 ATTACKS DETECTED + BLOCKED                         │
│  DoS ✅ | Spoofing ✅ | Fuzzing ✅ | Error Injection ✅      │
└──────────────────────────────────────────────────────────────┘
💻 4. Tech Stack
┌──────────────┬──────────────────────────────────────────────┐
│ Core         │ Python, C, Pandas, NumPy                     │
├──────────────┼──────────────────────────────────────────────┤
│ Detection    │ Scikit-Learn Isolation Forest + Rule IDS    │
├──────────────┼──────────────────────────────────────────────┤
│ Dashboard    │ PyQt5 + HTML/CSS/JS                         │
├──────────────┼──────────────────────────────────────────────┤
│ Low-Level    │ C, SocketCAN, GCC, Unix Domain Sockets      │
├──────────────┼──────────────────────────────────────────────┤
│ Tools        │ GitHub, VS Code, Ubuntu Live USB            │
└──────────────┴──────────────────────────────────────────────┘
📁 5. Project Structure
CAN-Sentinel/
├── can_simulator.py       # 4 ECUs Simulator
├── can_detector.py        # Rule IDS
├── can_attacker.py        # DoS + Spoofing
├── can_anomaly.py         # ML Model 99.6%
├── ecu_sim.c              # C ECU vcan0
├── attacker.c             # C Attacker
├── can_sniffer.c          # Live Sniffer
├── realtime_detector.py   # Sub-ms Inference
├── dashboard.py           # PyQt5 Dashboard
├── index.html             # Web Dashboard 100%
├── error_injector.py      # [Week 4] Error Frame
├── countermeasure.py      # [Week 4] Block + Rate Limit
├── defense.py             # [Week 4] Safe Mode + Alert
└── README.md

🛡️ 6. Week 4 - Countermeasures
Detect → Log → Error Frame → Block ID → Alert → Safe Mode → Auto-Recover

▶️ 7. How To Run
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
python3 can_simulator.py
python3 dashboard.py
python3 can_attacker.py
bash audit.sh

🏆 8. Final Results
┌──────────────────────────────────────────────────┐
│ ✅ Final Report + Demo Video Ready               │
│ ✅ Final Presentation + Viva - Ready              │
│ ✅ Project 100% Completed                        │
└──────────────────────────────────────────────────┘



                                     
