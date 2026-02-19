# shell_detector.py - Fixed: don't flag cycle members as shells

import networkx as nx

SHELL_TX_THRESHOLD = 3
MIN_CHAIN_LENGTH   = 3


def detect_shell_accounts(G):
    rings = []
    seen  = set()

    # First find all accounts already in cycles
    # so we don't double-flag them as shell accounts
    cycle_members = set()
    try:
        for cycle in nx.simple_cycles(G):
            if 3 <= len(cycle) <= 5:
                for node in cycle:
                    cycle_members.add(node)
    except Exception:
        pass

    shell_nodes = _find_shell_nodes(G, cycle_members)

    for shell in shell_nodes:
        chain = _trace_chain(G, shell, shell_nodes)
        if len(chain) >= MIN_CHAIN_LENGTH:
            key = tuple(sorted(chain))
            if key not in seen:
                seen.add(key)
                rings.append(chain)

    return rings


def _find_shell_nodes(G, exclude_nodes):
    shells = []
    for node in G.nodes():
        # Skip nodes already in cycles — they're not shells
        if node in exclude_nodes:
            continue

        in_degree  = G.in_degree(node)
        out_degree = G.out_degree(node)
        total      = in_degree + out_degree

        if in_degree >= 1 and out_degree >= 1 and total <= SHELL_TX_THRESHOLD:
            shells.append(node)

    return shells


def _trace_chain(G, start_shell, shell_nodes):
    chain   = [start_shell]
    current = start_shell

    # Trace forward
    for _ in range(10):
        successors = list(G.successors(current))
        if len(successors) == 1:
            nxt = successors[0]
            if nxt not in chain:
                chain.append(nxt)
                current = nxt
            else:
                break
        else:
            break

    # Trace backward
    current = start_shell
    for _ in range(10):
        predecessors = list(G.predecessors(current))
        if len(predecessors) == 1:
            prev = predecessors[0]
            if prev not in chain:
                chain.insert(0, prev)
                current = prev
            else:
                break
        else:
            break

    return chain
