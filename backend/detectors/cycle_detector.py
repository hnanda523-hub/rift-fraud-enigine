# cycle_detector.py
# Detects circular money flows (fraud rings).
# Example: A → B → C → A  ← This is a cycle of length 3.
# We look for cycles of length 3, 4, and 5 only.
# Longer cycles are too common in normal networks (false positives).

import networkx as nx


def detect_cycles(G):
    """
    Finds all simple cycles of length 3 to 5 in the directed graph.
    Returns a list of rings. Each ring is a list of account IDs.

    Example return:
    [
        ["ACC_001", "ACC_002", "ACC_003"],        ← cycle of length 3
        ["ACC_010", "ACC_011", "ACC_012", "ACC_013"]  ← cycle of length 4
    ]
    """
    rings = []
    seen  = set()  # Prevents duplicate rings

    try:
        # nx.simple_cycles finds ALL cycles in a directed graph
        for cycle in nx.simple_cycles(G):
            length = len(cycle)

            # Only keep cycles of length 3, 4, or 5
            if 3 <= length <= 5:
                # Sort so we don't add the same ring twice
                key = tuple(sorted(cycle))
                if key not in seen:
                    seen.add(key)
                    rings.append(cycle)
    except Exception:
        pass  # If graph has issues, return empty list safely

    return rings