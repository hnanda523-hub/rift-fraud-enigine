# main.py
# This is the entry point of our FastAPI backend.
# It receives the CSV file, runs all detectors, and returns the result.

import time
import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import io

from graph_builder import build_graph
from detectors.cycle_detector import detect_cycles
from detectors.smurfing_detector import detect_smurfing
from detectors.shell_detector import detect_shell_accounts
from scoring import calculate_suspicion_scores
from output_builder import build_output

# Create FastAPI app
app = FastAPI(title="RIFT Fraud Detection Engine")

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "RIFT Fraud Detection Engine is running"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    start_time = time.time()

    # ── 1. Read and validate the uploaded CSV ──────────────────────────
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file. Could not read it.")

    # Check required columns exist
    required_columns = {"transaction_id", "sender_id", "receiver_id", "amount", "timestamp"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise HTTPException(
            status_code=400,
            detail=f"CSV is missing required columns: {missing}"
        )

    # Clean up data
    df = df.dropna(subset=["sender_id", "receiver_id", "amount"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    if len(df) == 0:
        raise HTTPException(status_code=400, detail="CSV has no valid transaction rows.")

    # ── 2. Build the transaction graph ─────────────────────────────────
    # G is a NetworkX directed graph
    # Nodes = account IDs
    # Edges = transactions (with amount and timestamp as metadata)
    G = build_graph(df)

    # ── 3. Run all three detection algorithms ──────────────────────────
    cycle_rings      = detect_cycles(G)           # List of account ID lists
    smurfing_rings   = detect_smurfing(G, df)     # List of account ID lists
    shell_rings      = detect_shell_accounts(G)   # List of account ID lists

    all_rings = cycle_rings + smurfing_rings + shell_rings

    # ── 4. Calculate suspicion score per account ───────────────────────
    scores = calculate_suspicion_scores(G, df, cycle_rings, smurfing_rings, shell_rings)

    # ── 5. Build the exact required JSON output ────────────────────────
    processing_time = round(time.time() - start_time, 2)
    result = build_output(G, df, scores, all_rings, cycle_rings, smurfing_rings, shell_rings, processing_time)

    return result