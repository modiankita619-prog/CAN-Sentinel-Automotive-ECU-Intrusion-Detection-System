# CAN-Sentinel: Automotive ECU Intrusion Detection System

**Project Code:** ITS/CS/1076 | **Group No:** 1 | **Domain:** Cyber Security | **Duration:** 3 Months
**Status:** In Progress - MID Stage
*Last Update: 18 Oct 2026 - Working on Ankita branch for MID Review | Commit Days: 8/10*

### Team Members - Group No 1
- Garima Verma
- Ankita Modi
- Akhil Bojja
- Hardik Mittal

---

### 1. Project Aim
To design and develop an Intrusion Detection System (IDS) for automotive CAN (Controller Area Network) bus to detect and mitigate cyber-attacks targeting ECUs in real-time.

### 2. Problem Statement
Modern vehicles use CAN bus protocol (ISO 11898) which has no authentication and encryption. Attackers can inject malicious frames via OBD-II port or wireless interfaces, causing critical safety risks like brake failure and fake sensor readings. This project builds a defense layer to detect such intrusions.

### 3. Types of Attacks Detected
1.  **DoS Attack:** Flooding the bus with high-priority ID 0x000 @ 10ms interval
2.  **Spoofing Attack:** Injecting fake RPM / Speed messages on ID 0x0B0 / 0x0C0
3.  **Fuzzing Attack:** Injecting random CAN IDs (0x7FF, 0x123) with random data
4.  **Frequency Anomaly:** Normal 40 frames/sec to >100 frames/sec under attack

### 4. Tech Stack
- **Core:** Python, python-can, Pandas, NumPy
- **Detection:** Scikit-Learn (Isolation Forest), Rule-based IDS
- **Dashboard:** Flask, HTML, CSS, JavaScript (Live threat gauge)
- **Tools:** GitHub, VS Code Codespaces, Infotact Portal

### 5. System Architecture
`Virtual CAN Bus -> Normal ECU Traffic (80%) + Attack Injector (20%) -> IDS Detection Engine (DLC & ID Check) -> Web Dashboard (Alerts)`

### 6. Project Structure
- `/simulator` - can_simulator.py - CAN traffic simulator (4 ECUs)
- `/attacks` - can_attacker.py - DoS + Spoofing modules
- `/detection` - can_detector.py - Anomaly detection engine
- `/utils` - can_utils.py - Data loader & filter
- `/dashboard` - index.html - Live monitoring dashboard

### 7. Day-wise Progress (As per Infotact)
- **Day 1 - 10 Oct 2026:** Repository Created & Linked to Infotact Portal, main branch init
- **Day 2 - 11 Oct 2026:** Created index.html dashboard (CAN matrix, threat gauge) + Detailed README
- **Day 3 - 12 Oct 2026:** Created can_simulator.py - Simulated 20 CAN frames (4 ECUs: 0x0C0,0x0D0,0x0B0,0x0A0), Normal/Anomaly 80/20, DLC=8, Tested in Terminal
- **Day 4 - 13 Oct 2026:** Implemented can_attacker.py - DoS Flood (ID 0x000 @10ms) + Brake Spoofing - Tested 30 malicious frames
- **Day 5-6 - 14-16 Oct 2026:** Added can_utils.py, can_detector.py - Fixed anomaly logic (int/string ID handling), Integrated IDS with simulator. Current Stats: 15 Commits, 6 Date Groups, 15 Files, 350 LOC

**Note on Date Groups:** Due to UTC cutoff (5:30 AM IST), Oct 11 late night commits + Oct 12 commits counted as single group in Infotact dashboard. Hence 4 days work = 3 groups initially.

### 8. How to Run
```bash
pip install python-can scikit-learn flask pandas
python can_simulator.py
python can_attacker.py
python -m flask run
