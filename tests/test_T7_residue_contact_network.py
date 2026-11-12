"""T7 residue_contact_network tests (Part 2).

These tests cover all 10 criteria committed in docs/2_T7_criteria.md.
Biotite 1.6.0 + NetworkX 3.6.1 are required; the tests are collected
(and pass) inside the alloagent-dev:phase1 container. On a host
without these libraries the import-time collection succeeds but the
biotite/networkx-using tests skip with a clear message.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
FIX_1AKE_MMCIF = REPO / "tests" / "fixtures" / "1ake.cif"


def _has_biotite_and_nx() -> bool:
    try:
        import biotite  # noqa: F401
        import networkx  # noqa: F401
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _has_biotite_and_nx(),
    reason="biotite 1.6.0 + networkx 3.6.1 not installed in this env",
)


def _contract_keys_present(d: dict) -> bool:
    return (
        "success" in d
        and "data" in d
        and "source" in d
        and "source_version" in d
        and "query_time_utc" in d
    )


def _synthetic_mmcif_two_residues(entry_id, residues):
    """Build a minimal mmCIF text for a 2-residue structure.

    Each residue is a (comp_id, seq_id, [(x, y, z), ...]) tuple of
    three atoms (N, CA, C). The output includes the mandatory
    `pdbx_PDB_ins_code` column that Biotite requires.
    """
    rows = [
        "_atom_site.group_PDB",
        "_atom_site.id",
        "_atom_site.type_symbol",
        "_atom_site.label_atom_id",
        "_atom_site.label_alt_id",
        "_atom_site.label_comp_id",
        "_atom_site.label_asym_id",
        "_atom_site.label_entity_id",
        "_atom_site.label_seq_id",
        "_atom_site.pdbx_PDB_ins_code",
        "_atom_site.Cartn_x",
        "_atom_site.Cartn_y",
        "_atom_site.Cartn_z",
        "_atom_site.occupancy",
        "_atom_site.B_iso_or_equiv",
        "_atom_site.pdbx_PDB_model_num",
    ]
    lines = [
        f"data_{entry_id}",
        f"_struct.entry_id {entry_id}",
        "loop_",
    ]
    lines.extend(rows)
    serial = 1
    for comp_id, seq_id, coords in residues:
        for atom_name, (x, y, z) in zip(("N", "CA", "C"), coords):
            lines.append(
                f"ATOM {serial} {atom_name} {atom_name} . "
                f"{comp_id} A 1 {seq_id} ? {x:.3f} {y:.3f} {z:.3f} "
                f"1.00 0.00 1"
            )
            serial += 1
    return "\n".join(lines) + "\n"


def _synthetic_mmcif_single_residue(entry_id, comp_id, seq_id, coords):
    return _synthetic_mmcif_two_residues(
        entry_id,
        [(comp_id, seq_id, coords)],
    )


def test_t7_path_graph_betweenness_canonical():
    """A 5-node NetworkX path graph has betweenness {0:0, 1:3, 2:4,
    3:3, 4:0} when not normalized.
    """
    import networkx as nx

    g = nx.path_graph(5)
    bc = nx.betweenness_centrality(g, normalized=False)
    bc_rounded = {k: round(v, 6) for k, v in bc.items()}
    assert bc_rounded == {0: 0.0, 1: 3.0, 2: 4.0, 3: 3.0, 4: 0.0}


def test_t7_barbell_community_split_with_seed_42():
    """A barbell graph (K3 + K4 + bridge edge) splits into exactly two
    communities under the default `louvain` community detector.

    nx.barbell_graph(3, 1) is laid out as::

        clique A = {0, 1, 2}      -- K3, edges (0,1),(0,2),(1,2)
        bridge   = 2-3            -- single edge
        clique B = {3, 4, 5, 6}   -- K4, edges (3,4),(4,5),(4,6),(5,6)

    Louvain merges the bridge node (3) into clique A's community on
    this fixture, giving [{0,1,2,3}, {4,5,6}]. The test accepts this
    pattern AND the mirror where the bridge gets absorbed into
    clique B's side instead.
    """
    import networkx as nx

    from biomni.tool.residue_contact_network import _seeded_communities

    g = nx.barbell_graph(3, 1)
    comms = _seeded_communities(g, seed=42, algorithm="louvain")
    comm_sets = [frozenset(c) for c in comms]

    clique_a = frozenset({0, 1, 2})
    clique_b = frozenset({3, 4, 5, 6})

    expected_2comm = [
        (clique_a | {3}, clique_b - {3}),
        (clique_a, clique_b),
    ]
    found = any(
        any(c == ec_a for c in comm_sets) and any(c == ec_b for c in comm_sets)
        for ec_a, ec_b in expected_2comm
    )
    assert found, (
        f"missing expected split; got {comm_sets}"
    )
    assert len(comm_sets) == 2, f"expected 2 communities, got {comm_sets}"
    assert set().union(*comm_sets) == set(g.nodes())


def test_t7_louvain_equals_seeded_louvain_when_seed_42():
    """`_louvain_communities(g, seed=42)` matches `nx.louvain_communities(g, seed=42)`
    on the barbell fixture, confirming the wrapper is a thin pass-through.
    """
    import networkx as nx

    from biomni.tool.residue_contact_network import _louvain_communities

    g = nx.barbell_graph(3, 1)
    expected = sorted(
        sorted(c) for c in nx.community.louvain_communities(g, seed=42)
    )
    actual = sorted(sorted(c) for c in _louvain_communities(g, seed=42))
    assert actual == expected


def test_t7_louvain_is_seed_deterministic():
    """Two `_louvain_communities` calls with the same seed return the
    same partition (verifies the wrapper preserves determinism).
    """
    import networkx as nx

    from biomni.tool.residue_contact_network import _louvain_communities

    g = nx.barbell_graph(3, 1)
    a = sorted(sorted(c) for c in _louvain_communities(g, seed=7))
    b = sorted(sorted(c) for c in _louvain_communities(g, seed=7))
    assert a == b


def test_t7_label_propagation_still_supported():
    """The legacy `label_propagation` algorithm is still selectable.

    NetworkX's `label_propagation_communities` is unstable on small
    dense graphs (the 7-node barbell can collapse to a single
    community). The test only verifies that the dispatcher
    delegates correctly and that the result covers all nodes.
    """
    import networkx as nx

    from biomni.tool.residue_contact_network import (
        _label_propagation_communities,
        _seeded_communities,
    )

    g = nx.barbell_graph(3, 1)
    comms = _seeded_communities(g, seed=42, algorithm="label_propagation")
    comms_lp = _label_propagation_communities(g, seed=42)
    assert [sorted(c) for c in comms] == [sorted(c) for c in comms_lp]
    assert set().union(*[frozenset(c) for c in comms]) == set(g.nodes())
    assert len(comms) >= 1

    with pytest.raises(ValueError, match="unknown community-detection"):
        _seeded_communities(g, seed=42, algorithm="bogus")


def test_t7_label_propagation_seeded_deterministic():
    """The label-propagation wrapper is deterministic for a fixed seed
    (it shuffles nodes with the seeded RNG before calling NetworkX's
    non-seeded `label_propagation_communities`).
    """
    import networkx as nx

    from biomni.tool.residue_contact_network import _label_propagation_communities

    g = nx.barbell_graph(3, 1)
    a = sorted(sorted(c) for c in _label_propagation_communities(g, seed=42))
    b = sorted(sorted(c) for c in _label_propagation_communities(g, seed=42))
    assert a == b


def test_t7_residue_contact_network_synthetic_mmcif():
    """Write a synthetic mmCIF of two CA atoms 4.5 A apart and
    verify the tool returns n_residues=2, n_edges=1.
    """
    import tempfile

    mmcif_text = _synthetic_mmcif_two_residues(
        "1ABC",
        [
            ("ALA", 1, [(0.000, 0.000, 0.000), (0.000, 0.000, 0.000), (0.000, 0.000, 0.000)]),
            ("GLY", 2, [(4.400, 0.000, 0.000), (4.400, 0.000, 0.000), (4.400, 0.000, 0.000)]),
        ],
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cif", delete=False, encoding="utf-8"
    ) as f:
        f.write(mmcif_text)
        mmcif_path = Path(f.name)
    try:
        from biomni.tool.residue_contact_network import (
            residue_contact_network,
        )

        r = residue_contact_network(str(mmcif_path))
        assert _contract_keys_present(r)
        assert r["success"] is True
        assert r["data"]["n_residues"] == 2
        assert r["data"]["n_edges"] == 1
        assert "A.1" in r["data"]["betweenness"]
        assert "A.2" in r["data"]["betweenness"]
    finally:
        mmcif_path.unlink(missing_ok=True)


def test_t7_negative_control_empty_input():
    """An empty / non-CIF path returns success=True with n_residues=0."""
    from biomni.tool.residue_contact_network import (
        residue_contact_network,
    )

    r = residue_contact_network("/tmp/this-file-does-not-exist-xyzzy.cif")
    assert r["success"] is True
    assert r["data"]["n_residues"] == 0
    assert r["data"]["n_edges"] == 0
    assert r["data"]["betweenness"] == {}
    assert r["data"]["communities"] == []
    assert r["data"]["shortest_path"] == []


def test_t7_determinism():
    """Two calls with the same input return equal data."""
    mmcif_text = _synthetic_mmcif_two_residues(
        "1ABC",
        [
            ("ALA", 1, [(0.000, 0.000, 0.000)] * 3),
            ("GLY", 2, [(4.400, 0.000, 0.000)] * 3),
        ],
    )
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cif", delete=False, encoding="utf-8"
    ) as f:
        f.write(mmcif_text)
        mmcif_path = Path(f.name)
    try:
        from biomni.tool.residue_contact_network import (
            residue_contact_network,
        )

        a = residue_contact_network(str(mmcif_path))["data"]
        b = residue_contact_network(str(mmcif_path))["data"]
        assert a == b
    finally:
        mmcif_path.unlink(missing_ok=True)


def test_t7_lowercase_input_accepted():
    """A lowercase mmCIF path is processed without error."""
    mmcif_text = _synthetic_mmcif_two_residues(
        "1ABC",
        [
            ("ALA", 1, [(0.000, 0.000, 0.000)] * 3),
            ("GLY", 2, [(4.400, 0.000, 0.000)] * 3),
        ],
    )
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cif", delete=False, encoding="utf-8"
    ) as f:
        f.write(mmcif_text)
        mmcif_path = Path(f.name)
    try:
        from biomni.tool.residue_contact_network import (
            residue_contact_network,
        )

        r = residue_contact_network(str(mmcif_path).lower())
        assert r["success"] is True
        assert r["data"]["n_residues"] == 2
    finally:
        mmcif_path.unlink(missing_ok=True)


def test_t7_return_contract_keys_present():
    """Every call returns the 5 required contract keys."""
    from biomni.tool.residue_contact_network import (
        residue_contact_network,
    )

    r = residue_contact_network("/tmp/this-file-does-not-exist-xyzzy.cif")
    assert _contract_keys_present(r)
    assert r["source"] == "biomni.tool.residue_contact_network.residue_contact_network"
    assert r["source_version"] == "1.0"
    assert r["query_time_utc"].endswith("Z")


def test_t7_recorded_1ake_mmcif_if_present():
    """If the 1AKE mmCIF fixture is present, parse it and assert
    n_residues > 100 and the function returns within 60 s.
    """
    if not FIX_1AKE_MMCIF.is_file():
        pytest.skip(f"1AKE mmCIF fixture not at {FIX_1AKE_MMCIF}")
    from biomni.tool.residue_contact_network import (
        residue_contact_network,
    )

    t0 = time.perf_counter()
    r = residue_contact_network(str(FIX_1AKE_MMCIF))
    elapsed = time.perf_counter() - t0
    assert r["success"] is True
    assert r["data"]["n_residues"] > 100
    assert elapsed < 60.0, f"runtime {elapsed:.2f}s exceeded 60s budget"


def test_t7_shortest_path_between_two_residues():
    """source_residue and target_residue arguments produce a non-empty
    shortest_path for the synthetic 2-residue mmCIF.
    """
    mmcif_text = _synthetic_mmcif_two_residues(
        "1ABC",
        [
            ("ALA", 1, [(0.000, 0.000, 0.000)] * 3),
            ("GLY", 2, [(4.400, 0.000, 0.000)] * 3),
        ],
    )
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cif", delete=False, encoding="utf-8"
    ) as f:
        f.write(mmcif_text)
        mmcif_path = Path(f.name)
    try:
        from biomni.tool.residue_contact_network import (
            residue_contact_network,
        )

        r = residue_contact_network(
            str(mmcif_path),
            source_residue="A.1",
            target_residue="A.2",
        )
        assert r["success"] is True
        assert r["data"]["shortest_path"] == ["A.1", "A.2"]
    finally:
        mmcif_path.unlink(missing_ok=True)


def test_t7_blocklist_short_circuits(tmp_path, monkeypatch):
    """The benchmark_blocklist decorator short-circuits a blocked mmCIF
    path. The function never reaches the parser.
    """
    bl = tmp_path / "blocklist.tsv"
    blocked = "/tmp/blocked-mmcif-xyzzy.cif"
    bl.write_text(blocked + "\n", encoding="utf-8")
    monkeypatch.setenv("BENCHMARK_BLOCKLIST_FILE", str(bl))

    from biomni.tool.residue_contact_network import (
        residue_contact_network,
    )

    r = residue_contact_network(blocked)
    assert r["success"] is False
    assert "blocked" in r["error"].lower()