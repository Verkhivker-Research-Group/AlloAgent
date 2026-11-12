"""T7 residue_contact_network (Part 2).

Residue-residue contact graph from an mmCIF file (heavy atoms within
4.5 A), NetworkX 3.6.1 betweenness centrality, seeded community
detection, and optional shortest-path between two residues. Offline
tool (no network required once the mmCIF is on disk).
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from biomni.tool._blocklist import benchmark_blocklist
from biomni.tool._netcall import with_return_contract

_TIMEOUT_S = 60
_CONTACT_CUTOFF_A = 4.5
_DEFAULT_SEED = 42


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _source() -> str:
    return (
        "Biotite 1.6.0 (mmCIF parser) + NetworkX 3.6.1 "
        "(graph algorithms)"
    )


def _parse_mmcif_atoms(mmcif_path: Path):
    """Return a Biotite AtomArray (heavy atoms only) for the file.

    Returns None on parse error (the caller turns that into
    success=True, n_residues=0 to match the empty-input contract).
    """
    import biotite.structure as bstruc
    import biotite.structure.io.pdbx as pdbx

    try:
        cif_file = pdbx.CIFFile.read(str(mmcif_path))
    except Exception:
        return None
    try:
        atoms = pdbx.get_structure(
            cif_file, model=1, use_author_fields=False
        )
    except Exception:
        return None
    if atoms is None or atoms.array_length() == 0:
        return None
    try:
        heavy_mask = bstruc.filter_amino_acids(atoms) & (
            atoms.element != "H"
        )
        return atoms[heavy_mask]
    except Exception:
        return None


def _build_contact_graph(atoms, cutoff: float):
    """Build a NetworkX graph whose nodes are residue IDs and edges
    connect residue pairs with at least one pair of heavy atoms within
    `cutoff` Angstrom. Each residue node carries the list of its
    heavy atom coordinates for downstream shortest-path use.
    """
    import networkx as nx
    import numpy as np

    if atoms is None or atoms.array_length() == 0:
        return nx.Graph()

    residue_ids = atoms.res_id
    chain_ids = atoms.chain_id
    coord = atoms.coord

    by_res: dict[tuple, dict[str, Any]] = {}
    for i in range(atoms.array_length()):
        key = (str(chain_ids[i]), int(residue_ids[i]))
        slot = by_res.setdefault(
            key, {"coords": [], "residue_number": int(residue_ids[i])}
        )
        slot["coords"].append(coord[i])

    nodes = sorted(by_res.keys())
    index = {k: i for i, k in enumerate(nodes)}
    coords_arr = {
        k: np.asarray(by_res[k]["coords"], dtype=float) for k in nodes
    }
    residue_numbers = {k: by_res[k]["residue_number"] for k in nodes}

    g = nx.Graph()
    for k in nodes:
        g.add_node(k, residue_number=residue_numbers[k])

    for i, ki in enumerate(nodes):
        ri = coords_arr[ki]
        for j in range(i + 1, len(nodes)):
            kj = nodes[j]
            rj = coords_arr[kj]
            d = np.linalg.norm(ri[:, None, :] - rj[None, :, :], axis=2)
            if d.min() <= cutoff:
                g.add_edge(ki, kj)
    return g


def _louvain_communities(g, seed: int):
    """Return a list of frozensets (one per community) using
    NetworkX `louvain_communities(g, seed=...)`. Deterministic for
    a fixed seed across hosts and Python/NetworkX versions.
    """
    from networkx.algorithms.community import louvain_communities

    if g.number_of_nodes() == 0:
        return []
    return [frozenset(c) for c in louvain_communities(g, seed=seed)]


def _label_propagation_communities(g, seed: int):
    """Return a list of frozensets using a deterministic seeded
    label-propagation pass. The NetworkX
    `label_propagation_communities` does NOT accept a `seed`
    parameter; this wrapper is reproducible because the node order
    is shuffled with the seeded RNG before the call.
    """
    import random

    import networkx as nx
    from networkx.algorithms.community import (
        label_propagation_communities,
    )

    if g.number_of_nodes() == 0:
        return []

    rng = random.Random(seed)
    order = list(g.nodes())
    rng.shuffle(order)
    g_ordered = nx.relabel_nodes(
        g, {n: i for i, n in enumerate(order)}
    )
    inv = {i: n for i, n in enumerate(order)}
    comms_ordered = label_propagation_communities(g_ordered)
    out: list[frozenset] = []
    for c in comms_ordered:
        out.append(frozenset(inv[n] for n in c))
    return out


def _seeded_communities(g, seed: int, algorithm: str = "louvain"):
    """Dispatch to the chosen seeded community-detection algorithm.

    algorithm="louvain" (default) -> NetworkX `louvain_communities(g, seed=...)`.
    algorithm="label_propagation" -> deterministic seeded label-propagation
    (NetworkX's `label_propagation_communities` does not take a seed;
    we shuffle the node labels with the seeded RNG before calling).
    """
    algo = algorithm.lower().strip()
    if algo == "louvain":
        return _louvain_communities(g, seed)
    if algo in ("label_propagation", "label-propagation", "lp"):
        return _label_propagation_communities(g, seed)
    raise ValueError(
        f"unknown community-detection algorithm {algorithm!r} "
        "(use 'louvain' or 'label_propagation')"
    )


def _betweenness(g):
    import networkx as nx

    if g.number_of_nodes() == 0:
        return {}
    return {
        node: float(score)
        for node, score in nx.betweenness_centrality(
            g, normalized=False
        ).items()
    }


def _shortest_path(g, source_residue, target_residue):
    import networkx as nx

    if g.number_of_nodes() == 0 or source_residue is None or target_residue is None:
        return []
    source_node = _match_node(g, source_residue)
    target_node = _match_node(g, target_residue)
    if source_node is None or target_node is None:
        return []
    try:
        path = nx.shortest_path(g, source_node, target_node)
    except nx.NetworkXNoPath:
        return []
    return path


def _match_node(g, residue_id):
    """Resolve a user-supplied residue string like 'A.42' or '42' to a
    graph node. Returns None if no match.
    """
    if isinstance(residue_id, str) and "." in residue_id:
        chain, num = residue_id.split(".", 1)
        try:
            num_int = int(num)
        except ValueError:
            return None
        for n in g.nodes():
            if n[0] == chain and n[1] == num_int:
                return n
        return None
    try:
        target = int(residue_id)
    except (TypeError, ValueError):
        return None
    for n in g.nodes():
        if n[1] == target:
            return n
    return None


@with_return_contract(source_version="1.0")
@benchmark_blocklist
def residue_contact_network(
    mmcif_path,
    source_residue=None,
    target_residue=None,
    seed: int = _DEFAULT_SEED,
    community_algorithm: str = "louvain",
):
    """Build a residue-residue contact graph from an mmCIF file and
    return betweenness, communities, and (optionally) a shortest
    path between two residues.

    Parameters
    ----------
    mmcif_path : str or Path
        Path to an mmCIF file.
    source_residue : str or None
        Optional. A residue identifier in the form ``"<chain>.<resnum>"``
        (e.g. ``"A.42"``) or just the resnum (e.g. ``"42"``).
    target_residue : str or None
        Same format as ``source_residue``.
    seed : int
        Random seed for the community detector (deterministic
        across runs for a fixed NetworkX version).
    community_algorithm : str, default "louvain"
        "louvain" -> NetworkX `louvain_communities(g, seed=...)`.
        "label_propagation" -> seeded label-propagation (NetworkX's
        label_propagation_communities has no seed kwarg; the wrapper
        is reproducible because the node order is shuffled with the
        seeded RNG before the call).

    Returns
    -------
    dict
        Contract dict
        ``{success, data, error, source, source_version,
        query_time_utc}``. ``data`` is::

            {
                "n_residues": <int>,
                "n_edges": <int>,
                "betweenness": {<chain_id>, <resnum>: <score>, ...},
                "communities": [<set of (chain, resnum), ...], ...],
                "shortest_path": [<chain>, <resnum>, ...] | [],
                "seed": <int>,
                "community_algorithm": "louvain" or "label_propagation"
            }
    """
    path = Path(mmcif_path)
    atoms = _parse_mmcif_atoms(path)
    if atoms is None:
        return {
            "success": True,
            "data": {
                "n_residues": 0,
                "n_edges": 0,
                "betweenness": {},
                "communities": [],
                "shortest_path": [],
                "seed": seed,
            },
        }

    g = _build_contact_graph(atoms, _CONTACT_CUTOFF_A)
    communities = _seeded_communities(g, seed, community_algorithm)
    betweenness = _betweenness(g)
    shortest_path = _shortest_path(g, source_residue, target_residue)

    return {
        "success": True,
        "data": {
            "n_residues": g.number_of_nodes(),
            "n_edges": g.number_of_edges(),
            "betweenness": {
                f"{node[0]}.{node[1]}": score
                for node, score in betweenness.items()
            },
            "communities": [
                sorted([f"{c[0]}.{c[1]}" for c in comm]) for comm in communities
            ],
            "shortest_path": [f"{n[0]}.{n[1]}" for n in shortest_path],
            "seed": seed,
            "community_algorithm": community_algorithm.lower().strip(),
        },
    }