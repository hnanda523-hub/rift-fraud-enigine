# 🔍 FinCrimeGraph — Money Mule Detection Engine

> **RIFT 2026 Hackathon — Graph Theory / Financial Crime Detection Track**

A real-time, graph-based financial forensics engine that detects money muling networks using advanced graph algorithms. Upload a CSV of transactions and instantly visualize fraud rings, suspicious accounts, and layered shell networks.

🌐 **Live Demo:** https://rift-fraud-enigine.vercel.app/
📦 **Backend API:** https://rift-fraud-backend.onrender.com/
🎥 **Demo Video:** [LinkedIn Post Link Here]

---

## 🧠 Problem Statement

Money muling is a critical component of financial crime where criminals use networks of individuals to transfer and layer illicit funds through multiple accounts. Traditional database queries fail because:

- They look at individual transactions, not patterns across networks
- They cannot detect multi-hop circular flows
- They miss smurfing patterns that span many accounts

**Our solution uses graph theory** to model accounts as nodes and transactions as directed edges — making fraud rings mathematically detectable.

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + Vite | Fast, modern UI |
| Styling | TailwindCSS | Dark cybersecurity theme |
| Graph Viz | Cytoscape.js | Interactive directed graph |
| HTTP | Axios | API communication |
| Backend | FastAPI (Python) | High-performance REST API |
| Graph Engine | NetworkX | Graph construction and algorithms |
| Deployment | Vercel + Render | Free, production-grade hosting |

---

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────┐
│                    USER BROWSER                     │
│                                                     │
│  ┌─────────────┐         ┌──────────────────────┐  │
│  │ Upload CSV  │─POST──▶️│   FastAPI Backend     │  │
│  │             │◀️─JSON──│   (Render.com)        │  │
│  └─────────────┘         └──────────────────────┘  │
│                                    │                │
│  ┌─────────────────────┐    ┌──────▼─────────┐     │
│  │  Cytoscape Graph    │    │   NetworkX      │     │
│  │  Fraud Table        │    │   Graph Engine  │     │
│  │  Node Details       │    └────────────────┘     │
│  │  JSON Download      │                            │
│  └─────────────────────┘                            │
│         React Frontend (Vercel)                     │
└─────────────────────────────────────────────────────┘
```

**Data Flow:**
1. User uploads CSV → FastAPI parses it
2. NetworkX builds directed graph (accounts=nodes, transactions=edges)
3. Three detection algorithms run simultaneously
4. Suspicion scores calculated per account (0-100)
5. JSON response sent to React frontend
6. Cytoscape renders interactive graph visualization

---

## 🔬 Algorithm Approach

### Algorithm 1 — Cycle Detection (Circular Fund Routing)

Detects money loops like A → B → C → A using DFS-based simple cycle enumeration via NetworkX. We only detect cycles of length 3, 4, and 5 — longer cycles are too common in normal networks and cause false positives.

- Time Complexity: O(V + E) per cycle
- Space Complexity: O(V) for DFS stack

### Algorithm 2 — Smurfing Detection (Fan-in / Fan-out)

Detects one account sending to 10+ accounts (fan-out) or 10+ accounts sending to one account (fan-in). Includes temporal analysis — transactions within a 72-hour window receive a high-velocity bonus score.

- Time Complexity: O(V + E)
- Space Complexity: O(V)

### Algorithm 3 — Shell Account Detection (Layered Chains)

Detects intermediate accounts used only to pass money through. Signs: only 2-3 total transactions, always in middle position with both incoming and outgoing edges. We trace full chains of 3+ hops.

- Time Complexity: O(V + E)
- Space Complexity: O(V)

**Overall Pipeline Complexity: O(V + E + C)**
Where V = accounts, E = transactions, C = detected cycles

---

## 📊 Suspicion Score Methodology

Every account receives a score from 0 to 100:
```
+40  → Account is part of a detected cycle
+35  → Account is the hub of a smurfing ring
+20  → Account is a connected node in smurfing ring
+20  → Account is a shell account (middle of chain)
+15  → Transactions within 72-hour window (high velocity)
−20  → Account has 20+ transactions (merchant/payroll penalty)

Final Score = clamp(total, 0, 100)
```

### Risk Categories

| Score | Category | Node Color |
|---|---|---|
| 0 – 40 | Low Risk | Green |
| 41 – 70 | Medium Risk | Yellow |
| 71 – 100 | High Risk | Red |

### False Positive Prevention

- High-volume merchants receive score penalty (20+ transactions)
- Payroll accounts with monthly batch payments are not flagged
- Cycles of length 2 are ignored (normal payments)
- Only smurfing within 72-hour windows gets velocity bonus

---

## 📁 Project Structure
```
rift-fraud-engine/
│
├── backend/
│   ├── main.py                   ← API server, /analyze endpoint
│   ├── graph_builder.py          ← CSV to NetworkX graph
│   ├── scoring.py                ← Suspicion score calculator
│   ├── output_builder.py         ← Required JSON format builder
│   ├── requirements.txt
│   ├── runtime.txt
│   └── detectors/
│       ├── __init__.py
│       ├── cycle_detector.py     ← DFS cycle detection (length 3-5)
│       ├── smurfing_detector.py  ← Fan-in/fan-out + 72hr window
│       └── shell_detector.py    ← Shell account chain detection
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── UploadSection.jsx
│       │   ├── GraphView.jsx
│       │   ├── FraudTable.jsx
│       │   ├── NodeDetails.jsx
│       │   └── SummaryBar.jsx
│       ├── utils/
│       │   └── api.js
│       └── App.jsx
│
└── README.md
```

---

## 🚀 Installation and Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- Git

### Backend Setup
```bash
git clone https://github.com/YOURUSERNAME/rift-fraud-engine.git
cd rift-fraud-engine/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```

---

## 📋 Usage Instructions

1. Prepare your CSV file with these exact columns:
```
transaction_id, sender_id, receiver_id, amount, timestamp
```

2. Open the app and drag and drop your CSV file
3. Click **Run Fraud Detection**
4. Explore the interactive graph — click any node for details
5. Download the JSON output with one click

---

## 📤 Input Format
```csv
transaction_id,sender_id,receiver_id,amount,timestamp
T001,ACC_001,ACC_002,5000,2024-01-01 10:00:00
T002,ACC_002,ACC_003,4800,2024-01-01 11:00:00
T003,ACC_003,ACC_001,4600,2024-01-01 12:00:00
```

## 📥 Output Format
```json
{
  "suspicious_accounts": [
    {
      "account_id": "ACC_001",
      "suspicion_score": 80.0,
      "detected_patterns": ["cycle_length_3"],
      "ring_id": "RING_001"
    }
  ],
  "fraud_rings": [
    {
      "ring_id": "RING_001",
      "member_accounts": ["ACC_001", "ACC_002", "ACC_003"],
      "pattern_type": "cycle",
      "risk_score": 92.0
    }
  ],
  "summary": {
    "total_accounts_analyzed": 18,
    "suspicious_accounts_flagged": 6,
    "fraud_rings_detected": 3,
    "processing_time_seconds": 0.02
  }
}
```

---

## ⚡ Performance

| Dataset Size | Processing Time |
|---|---|
| 100 transactions | under 0.1 seconds |
| 1,000 transactions | under 0.5 seconds |
| 10,000 transactions | under 3 seconds |

---

## ⚠️ Known Limitations

- Cycles longer than length 5 are not detected (intentional — reduces false positives)
- Very dense graphs with 100K+ transactions may exceed 30 seconds
- Smurfing threshold is fixed at 10 connections
- Shell account detection requires minimum 3-hop chains
- Free Render instance may have 50-second cold start after inactivity

---

## 👤 Team Members

| Hemant Nanda | Team Leader |
|---|---|
| Developer — Algorithm Design |

| Sunny | 
|---|---|
| Developer — Full Stack |

| Varsha Biswal | 
|---|---|
| Developer — Testing and Error Handelling |


---

## 🏆 Hackathon

**RIFT 2026** — Graph Theory / Financial Crime Detection Track
**Challenge:** Money Muling Detection
**Submitted:** February 2026

---

*Built with love for RIFT 2026 — Follow the money.*
