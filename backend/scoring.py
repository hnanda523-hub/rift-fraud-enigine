# scoring.py - No pandas version

def calculate_suspicion_scores(G, rows, cycle_rings, smurfing_rings, shell_rings):
    scores = {}
    for node in G.nodes():
        scores[node] = {"score": 0.0, "patterns": []}

    # Cycles: +40
    for ring in cycle_rings:
        for account in ring:
            if account in scores:
                scores[account]["score"] += 40
                pattern = f"cycle_length_{len(ring)}"
                if pattern not in scores[account]["patterns"]:
                    scores[account]["patterns"].append(pattern)

    # Smurfing: hub +35, others +20, window +15
    for ring in smurfing_rings:
        members   = ring["members"]
        pattern   = ring["pattern"]
        in_window = ring.get("in_window", False)
        hub       = members[0] if pattern == "fan_out" else members[-1]

        for account in members:
            if account in scores:
                points = 35 if account == hub else 20
                scores[account]["score"] += points
                if pattern not in scores[account]["patterns"]:
                    scores[account]["patterns"].append(pattern)
                if in_window:
                    scores[account]["score"] += 15
                    if "high_velocity" not in scores[account]["patterns"]:
                        scores[account]["patterns"].append("high_velocity")

    # Shell: +20
    for ring in shell_rings:
        for account in ring:
            if account in scores:
                scores[account]["score"] += 20
                if "shell_account" not in scores[account]["patterns"]:
                    scores[account]["patterns"].append("shell_account")

    # High volume penalty
    tx_counts = {}
    for row in rows:
        s = str(row.get("sender_id", "")).strip()
        r = str(row.get("receiver_id", "")).strip()
        tx_counts[s] = tx_counts.get(s, 0) + 1
        tx_counts[r] = tx_counts.get(r, 0) + 1

    for account, count in tx_counts.items():
        if account in scores and count >= 20:
            penalty = min(40, count)
            scores[account]["score"] -= penalty
            if "high_volume_merchant" not in scores[account]["patterns"]:
                scores[account]["patterns"].append("high_volume_merchant")

    # Clamp 0-100
    for account in scores:
        scores[account]["score"] = round(
            max(0.0, min(100.0, scores[account]["score"])), 1
        )

    return scores