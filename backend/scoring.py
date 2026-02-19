# scoring.py - Fixed version with better smurfing scores

def calculate_suspicion_scores(G, df, cycle_rings, smurfing_rings, shell_rings):

    scores = {}
    for node in G.nodes():
        scores[node] = {"score": 0.0, "patterns": []}

    # ── Cycle: +40 points ─────────────────────────────────────────────
    for ring in cycle_rings:
        for account in ring:
            if account in scores:
                scores[account]["score"] += 40
                pattern = f"cycle_length_{len(ring)}"
                if pattern not in scores[account]["patterns"]:
                    scores[account]["patterns"].append(pattern)

    # ── Smurfing: +30 points (raised from 25) ─────────────────────────
    for ring in smurfing_rings:
        members   = ring["members"]
        pattern   = ring["pattern"]
        in_window = ring.get("in_window", False)

        # Hub account (first for fan_out, last for fan_in) gets extra score
        hub = members[0] if pattern == "fan_out" else members[-1]

        for account in members:
            if account in scores:
                # Hub gets +35, connected accounts get +20
                points = 35 if account == hub else 20
                scores[account]["score"] += points
                if pattern not in scores[account]["patterns"]:
                    scores[account]["patterns"].append(pattern)

                # Time window bonus: +15
                if in_window:
                    scores[account]["score"] += 15
                    if "high_velocity" not in scores[account]["patterns"]:
                        scores[account]["patterns"].append("high_velocity")

    # ── Shell accounts: +20 points ────────────────────────────────────
    for ring in shell_rings:
        for account in ring:
            if account in scores:
                scores[account]["score"] += 20
                if "shell_account" not in scores[account]["patterns"]:
                    scores[account]["patterns"].append("shell_account")

    # ── High volume merchant penalty: -20 ─────────────────────────────
    tx_counts = {}
    for _, row in df.iterrows():
        s = str(row["sender_id"]).strip()
        r = str(row["receiver_id"]).strip()
        tx_counts[s] = tx_counts.get(s, 0) + 1
        tx_counts[r] = tx_counts.get(r, 0) + 1

    for account, count in tx_counts.items():
        if account in scores and count >= 20:
            # Scale the penalty based on transaction volume
            penalty = min(40, count)  # max -40 penalty
            scores[account]["score"] -= penalty
            if "high_volume_merchant" not in scores[account]["patterns"]:
                scores[account]["patterns"].append("high_volume_merchant")

    # ── Clamp 0–100 ───────────────────────────────────────────────────
    for account in scores:
        scores[account]["score"] = round(
            max(0.0, min(100.0, scores[account]["score"])), 1
        )

    return scores