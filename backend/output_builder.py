# output_builder.py - Fixed version
import time

def build_output(G, df, scores, all_rings, cycle_rings, smurfing_rings, shell_rings, processing_time):

    fraud_rings_output = []
    ring_counter       = 1
    account_to_ring    = {}

    # ── Helper to add rings ────────────────────────────────────────────
    def process_rings(rings, default_pattern):
        nonlocal ring_counter

        for ring in rings:
            # Handle smurfing rings (dict) vs cycle/shell rings (list)
            if isinstance(ring, dict):
                members      = ring["members"]
                pattern_type = ring["pattern"]
                in_window    = ring.get("in_window", False)
            else:
                members      = ring
                pattern_type = default_pattern
                in_window    = False

            # Skip empty rings
            if not members:
                continue

            # Remove duplicates while preserving order
            seen_members = []
            seen_set     = set()
            for m in members:
                if m not in seen_set:
                    seen_set.add(m)
                    seen_members.append(m)
            members = seen_members

            ring_id = f"RING_{str(ring_counter).zfill(3)}"
            ring_counter += 1

            # Assign ring_id to accounts (first ring wins — no duplicate assignment)
            for acc in members:
                if acc not in account_to_ring:
                    account_to_ring[acc] = ring_id

            # Calculate risk score for this ring
            member_scores = [scores[m]["score"] for m in members if m in scores]
            if not member_scores:
                continue
            avg_score = sum(member_scores) / len(member_scores)

            # Pattern-based risk multiplier
            multipliers = {
                "cycle":       1.15,
                "fan_out":     1.10,
                "fan_in":      1.10,
                "shell_chain": 1.05,
            }
            multiplier = multipliers.get(pattern_type, 1.0)
            risk_score = round(min(100.0, avg_score * multiplier), 1)

            fraud_rings_output.append({
                "ring_id":         ring_id,
                "member_accounts": members,
                "pattern_type":    pattern_type,
                "risk_score":      risk_score,
            })

    # Process in priority order (cycles first — highest priority)
    process_rings(cycle_rings,    "cycle")
    process_rings(smurfing_rings, "smurfing")
    process_rings(shell_rings,    "shell_chain")

    # ── Suspicious accounts (score > 0, sorted descending) ────────────
    suspicious_accounts = []
    for account_id, data in scores.items():
        if data["score"] > 0:
            suspicious_accounts.append({
                "account_id":        account_id,
                "suspicion_score":   data["score"],
                "detected_patterns": data["patterns"],
                "ring_id":           account_to_ring.get(account_id, "UNASSIGNED"),
            })

    suspicious_accounts.sort(key=lambda x: x["suspicion_score"], reverse=True)

    # ── Summary ────────────────────────────────────────────────────────
    summary = {
        "total_accounts_analyzed":    G.number_of_nodes(),
        "suspicious_accounts_flagged": len(suspicious_accounts),
        "fraud_rings_detected":        len(fraud_rings_output),
        "processing_time_seconds":     processing_time,
    }

    # ── Frontend graph data ────────────────────────────────────────────
    nodes_for_frontend = []
    for node in G.nodes():
        nodes_for_frontend.append({
            "id":              node,
            "suspicion_score": scores.get(node, {}).get("score", 0),
            "flags":           scores.get(node, {}).get("patterns", []),
        })

    edges_for_frontend = []
    for u, v, data in G.edges(data=True):
        edges_for_frontend.append({
            "source": u,
            "target": v,
            "amount": round(data.get("amount", 0), 2),
        })

    return {
        # Exact judge format
        "suspicious_accounts": suspicious_accounts,
        "fraud_rings":         fraud_rings_output,
        "summary":             summary,
        # Frontend extras
        "nodes":               nodes_for_frontend,
        "edges":               edges_for_frontend,
    }