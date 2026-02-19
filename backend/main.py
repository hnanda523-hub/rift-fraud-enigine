# main.py - No pandas version
import time
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from graph_builder import build_graph, parse_csv
from detectors.cycle_detector import detect_cycles
from detectors.smurfing_detector import detect_smurfing
from detectors.shell_detector import detect_shell_accounts
from scoring import calculate_suspicion_scores
from output_builder import build_output

app = FastAPI(title="RIFT Fraud Detection Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    # Read file
    try:
        contents = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read file.")

    # Parse CSV
    try:
        rows = parse_csv(contents)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file.")

    if not rows:
        raise HTTPException(status_code=400, detail="CSV has no rows.")

    # Check required columns
    required = {"transaction_id", "sender_id", "receiver_id", "amount", "timestamp"}
    if rows:
        missing = required - set(rows[0].keys())
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"CSV missing columns: {missing}"
            )

    # Build graph
    G, df = build_graph(contents)

    # Run detectors
    cycle_rings    = detect_cycles(G)
    smurfing_rings = detect_smurfing(G, df)
    shell_rings    = detect_shell_accounts(G)
    all_rings      = cycle_rings + smurfing_rings + shell_rings

    # Score
    scores = calculate_suspicion_scores(G, df, cycle_rings, smurfing_rings, shell_rings)

    # Build output
    processing_time = round(time.time() - start_time, 2)
    result = build_output(G, df, scores, all_rings, cycle_rings, smurfing_rings, shell_rings, processing_time)

    return result