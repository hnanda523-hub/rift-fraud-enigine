# graph_builder.py
# Converts the CSV dataframe into a NetworkX directed graph.
# Each unique account becomes a node.
# Each transaction becomes a directed edge (sender → receiver).

import networkx as nx


def build_graph(df):
    """
    Takes a pandas DataFrame with transaction data.
    Returns a NetworkX DiGraph (directed graph).
    """
    G = nx.DiGraph()

    for _, row in df.iterrows():
        sender   = str(row["sender_id"]).strip()
        receiver = str(row["receiver_id"]).strip()
        amount   = float(row["amount"])
        timestamp = row["timestamp"]

        # Add nodes (NetworkX auto-skips if already exists)
        G.add_node(sender)
        G.add_node(receiver)

        # Add directed edge with metadata
        # If edge already exists, we accumulate the amount
        if G.has_edge(sender, receiver):
            G[sender][receiver]["amount"]      += amount
            G[sender][receiver]["tx_count"]    += 1
            G[sender][receiver]["timestamps"].append(timestamp)
        else:
            G.add_edge(
                sender,
                receiver,
                amount=amount,
                tx_count=1,
                timestamps=[timestamp]
            )

    return G