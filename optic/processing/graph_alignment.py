from __future__ import annotations
from ..type_definitions import *
import networkx as nx
import pandas as pd


# Build undirected graph for multi-session ROI alignment.
# Nodes: (session_label, roi_id) tuples for every ROI in every session (isolated nodes kept).
# Edges: pairwise matches taken from dict_roi_matching["match"][t_pri][t_sec].
def buildSessionROIGraph(
    dict_roi_matching: Dict[str, Any],
    list_session_labels: List[str],
) -> nx.Graph:
    G = nx.Graph()
    n_sessions = len(list_session_labels)

    dict_id = dict_roi_matching.get("id", {})
    for t, roi_ids in dict_id.items():
        if t >= n_sessions:
            continue
        label = list_session_labels[t]
        for roi in roi_ids:
            G.add_node((label, int(roi)))

    dict_match = dict_roi_matching.get("match", {})
    for t_pri, sec_dict in dict_match.items():
        if t_pri >= n_sessions:
            continue
        label_pri = list_session_labels[t_pri]
        for t_sec, match_dict in sec_dict.items():
            if t_sec >= n_sessions:
                continue
            label_sec = list_session_labels[t_sec]
            for roi_pri, roi_sec in match_dict.items():
                if roi_sec is None:
                    continue
                G.add_edge((label_pri, int(roi_pri)), (label_sec, int(roi_sec)))
    return G


# Split graph's connected components into complete subgraphs (cliques) and incomplete subgraphs.
# Single-node components are counted as cliques (isolated ROIs preserved as single-session entries).
def classifySubgraphs(
    G: nx.Graph,
) -> Tuple[List[List[Tuple[str, int]]], List[List[Tuple[str, int]]]]:
    list_clique = []
    list_incomplete = []
    for nodes in nx.connected_components(G):
        subG = G.subgraph(nodes)
        n_nodes = len(subG.nodes)
        n_edges = len(subG.edges)
        if n_nodes == 1:
            list_clique.append(list(subG.nodes))
        elif n_edges == n_nodes * (n_nodes - 1) // 2:
            list_clique.append(list(subG.nodes))
        else:
            list_incomplete.append(list(subG.nodes))
    return list_clique, list_incomplete


# Convert cliques into a DataFrame: rows = ROI identities, columns = session labels.
# Missing entries become -1. Rows are sorted ascending by all columns (-1 sorts as +inf).
def buildMasterTrackingTable(
    list_clique: List[List[Tuple[str, int]]],
    list_session_labels: List[str],
) -> pd.DataFrame:
    cols = list(list_session_labels)
    data = [[-1] * len(cols) for _ in range(len(list_clique))]
    col_idx = {c: i for i, c in enumerate(cols)}
    for row, clique in enumerate(list_clique):
        for label, roi in clique:
            data[row][col_idx[label]] = int(roi)
    df = pd.DataFrame(data, columns=cols, dtype="int32")
    if len(df) > 0:
        df = df.sort_values(
            by=df.columns.tolist(),
            key=lambda col: col.apply(lambda x: float("inf") if x == -1 else x),
        )
        df.index = range(len(df))
    return df


# Top-level entry: build graph -> classify -> assemble master tracking table.
def generateMasterTrackingTable(
    dict_roi_matching: Dict[str, Any],
    list_session_labels: List[str],
) -> Tuple[pd.DataFrame, List[List[Tuple[str, int]]], List[List[Tuple[str, int]]]]:
    G = buildSessionROIGraph(dict_roi_matching, list_session_labels)
    list_clique, list_incomplete = classifySubgraphs(G)
    df = buildMasterTrackingTable(list_clique, list_session_labels)
    return df, list_clique, list_incomplete
