# smurfing_detector.py - No pandas version
from datetime import datetime, timedelta

FAN_THRESHOLD = 10


def detect_smurfing(G, rows):
    rings = []
    seen  = set()

    for node in G.nodes():

        # Fan-out
        out_neighbors = list(G.successors(node))
        if len(out_neighbors) >= FAN_THRESHOLD:
            key = ("fanout", node)
            if key not in seen:
                seen.add(key)
                in_window = _check_72hr_window(rows, node, out_neighbors, "out")
                rings.append({
                    "members":   [node] + out_neighbors,
                    "pattern":   "fan_out",
                    "in_window": in_window,
                })

        # Fan-in
        in_neighbors = list(G.predecessors(node))
        if len(in_neighbors) >= FAN_THRESHOLD:
            key = ("fanin", node)
            if key not in seen:
                seen.add(key)
                in_window = _check_72hr_window(rows, node, in_neighbors, "in")
                rings.append({
                    "members":   in_neighbors + [node],
                    "pattern":   "fan_in",
                    "in_window": in_window,
                })

    return rings


def _check_72hr_window(rows, hub, neighbors, direction):
    try:
        neighbor_set = set(str(n) for n in neighbors)
        hub_str      = str(hub)
        timestamps   = []

        for row in rows:
            sender   = str(row.get("sender_id", "")).strip()
            receiver = str(row.get("receiver_id", "")).strip()

            if direction == "out" and sender == hub_str and receiver in neighbor_set:
                ts = _parse_ts(row.get("timestamp", ""))
                if ts:
                    timestamps.append(ts)
            elif direction == "in" and receiver == hub_str and sender in neighbor_set:
                ts = _parse_ts(row.get("timestamp", ""))
                if ts:
                    timestamps.append(ts)

        timestamps.sort()
        window = timedelta(hours=72)

        for i in range(len(timestamps)):
            count = sum(1 for t in timestamps[i:] if t - timestamps[i] <= window)
            if count >= 5:
                return True

    except Exception:
        pass

    return False


def _parse_ts(ts_str):
    try:
        return datetime.fromisoformat(str(ts_str).strip())
    except Exception:
        return None