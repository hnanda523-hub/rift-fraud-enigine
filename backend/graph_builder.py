# graph_builder.py - No pandas version (works on any Python)
import networkx as nx
import csv
import io
from datetime import datetime


def build_graph_from_df(df):
    """Build graph from list of row dicts."""
    G = nx.DiGraph()

    for row in df:
        sender    = str(row["sender_id"]).strip()
        receiver  = str(row["receiver_id"]).strip()
        try:
            amount = float(row["amount"])
        except Exception:
            continue

        try:
            timestamp = datetime.fromisoformat(str(row["timestamp"]))
        except Exception:
            timestamp = None

        G.add_node(sender)
        G.add_node(receiver)

        if G.has_edge(sender, receiver):
            G[sender][receiver]["amount"]     += amount
            G[sender][receiver]["tx_count"]   += 1
            G[sender][receiver]["timestamps"].append(timestamp)
        else:
            G.add_edge(
                sender, receiver,
                amount=amount,
                tx_count=1,
                timestamps=[timestamp]
            )

    return G


def parse_csv(contents: bytes):
    """Parse CSV bytes into list of row dicts."""
    text    = contents.decode("utf-8")
    reader  = csv.DictReader(io.StringIO(text))
    rows    = []
    for row in reader:
        rows.append(row)
    return rows


def build_graph(contents: bytes):
    """Main entry: parse CSV and build graph."""
    rows = parse_csv(contents)
    return build_graph_from_df(rows), rows