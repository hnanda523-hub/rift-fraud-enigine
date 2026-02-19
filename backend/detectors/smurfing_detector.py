# smurfing_detector.py
# Detects smurfing patterns: fan-in and fan-out.
#
# Fan-out: One account sends money to 10+ different accounts
#          → Suspicious dispersal (breaking up large sums)
#
# Fan-in:  10+ different accounts send money to one account
#          → Suspicious aggregation (collecting layered funds)
#
# Extra suspicion: If this happens within a 72-hour window.

import pandas as pd
from datetime import timedelta


# Threshold: how many connections trigger smurfing flag
FAN_THRESHOLD = 10  # 10+ unique senders or receivers


def detect_smurfing(G, df):
    """
    Detects fan-in and fan-out smurfing patterns.
    Returns a list of rings. Each ring contains the hub account
    and all its connected accounts.
    """
    rings = []
    seen  = set()

    for node in G.nodes():

        # ── Fan-out: node sends to many receivers ──────────────────────
        out_neighbors = list(G.successors(node))
        if len(out_neighbors) >= FAN_THRESHOLD:
            key = ("fanout", node)
            if key not in seen:
                seen.add(key)
                ring_members = [node] + out_neighbors

                # Check if it happens in a 72-hour window (more suspicious)
                in_window = _check_72hr_window(df, node, out_neighbors, direction="out")

                rings.append({
                    "members":    ring_members,
                    "pattern":    "fan_out",
                    "in_window":  in_window
                })

        # ── Fan-in: node receives from many senders ────────────────────
        in_neighbors = list(G.predecessors(node))
        if len(in_neighbors) >= FAN_THRESHOLD:
            key = ("fanin", node)
            if key not in seen:
                seen.add(key)
                ring_members = in_neighbors + [node]

                in_window = _check_72hr_window(df, node, in_neighbors, direction="in")

                rings.append({
                    "members":   ring_members,
                    "pattern":   "fan_in",
                    "in_window": in_window
                })

    return rings


def _check_72hr_window(df, hub_account, neighbors, direction):
    """
    Checks whether the transactions between hub and neighbors
    occurred within any 72-hour window.
    Returns True if suspicious temporal clustering is found.
    """
    try:
        if direction == "out":
            txs = df[
                (df["sender_id"].astype(str) == str(hub_account)) &
                (df["receiver_id"].astype(str).isin([str(n) for n in neighbors]))
            ]
        else:
            txs = df[
                (df["receiver_id"].astype(str) == str(hub_account)) &
                (df["sender_id"].astype(str).isin([str(n) for n in neighbors]))
            ]

        timestamps = txs["timestamp"].dropna().sort_values()
        if len(timestamps) < 2:
            return False

        # Sliding window: check if 5+ transactions happen within 72 hours
        window = timedelta(hours=72)
        timestamps = list(timestamps)
        for i in range(len(timestamps)):
            count = sum(1 for t in timestamps[i:] if t - timestamps[i] <= window)
            if count >= 5:
                return True

    except Exception:
        pass

    return False