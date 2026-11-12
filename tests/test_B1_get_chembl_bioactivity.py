"""B1 get_chembl_bioactivity tests (Part 2 / batch 2).

These tests cover all 18 criteria committed in
docs/2_get_chembl_bioactivity_criteria.md. Tests use a
synthetic SQLite database (the real ChEMBL 37 file is ~15-20 GB
unpacked; T10 stays PARTIAL until that file is placed). The
web API path is exercised via mocking.
"""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from unittest import mock

import pytest

REPO = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# REAL ChEMBL 37 schema.
#
# These CREATE TABLE statements are copied VERBATIM out of the real
# ChEMBL 37 SQLite distribution (data/chembl/chembl_37_sqlite/chembl_37.db,
# `SELECT sql FROM sqlite_master WHERE type='table' AND name=?`, read-only)
# for the seven tables the B1 wrapper touches:
#
#     activities, assays, molecule_dictionary, molecule_synonyms,
#     target_dictionary, target_components, component_sequences
#
# They are NOT hand-written approximations. That distinction matters:
# an earlier revision of this file used a hand-written, hand-simplified
# schema, and because that simplified schema happened to agree with the
# wrapper's own (wrong) assumptions, the tests passed while every live
# query against the real database failed with
# "no such column: a.target_chembl_id". Copying the real DTL -- with its
# NOT NULL and CHECK constraints intact -- means a fixture can no longer
# accidentally agree with a wrong query.
#
# Foreign keys point at tables that are not created here (docs, source,
# compound_records, ...). SQLite only enforces FKs when
# `PRAGMA foreign_keys=ON`, which is off by default; the fixture leaves it
# off, exactly as a real ChEMBL client does not need it.
#
# The ROWS inserted below are FABRICATED (clearly labelled as such) so the
# suite stays fast. Identities and casing that a test depends on are taken
# from the real database; the numeric values are invented.
# ---------------------------------------------------------------------------

_REAL_CHEMBL_37_DDL = """
CREATE TABLE activities (
	activity_id BIGINT NOT NULL,
	assay_id BIGINT NOT NULL,
	doc_id BIGINT,
	record_id BIGINT NOT NULL,
	molregno BIGINT,
	standard_relation VARCHAR(50),
	standard_value NUMERIC,
	standard_units VARCHAR(100),
	standard_flag SMALLINT,
	standard_type VARCHAR(250),
	activity_comment VARCHAR(4000),
	data_validity_comment VARCHAR(30),
	potential_duplicate SMALLINT,
	pchembl_value NUMERIC(4, 2),
	bao_endpoint VARCHAR(11),
	uo_units VARCHAR(10),
	qudt_units VARCHAR(70),
	toid INTEGER,
	upper_value NUMERIC,
	standard_upper_value NUMERIC,
	src_id INTEGER,
	type VARCHAR(250) NOT NULL,
	relation VARCHAR(50),
	value NUMERIC,
	units VARCHAR(100),
	text_value VARCHAR(1000),
	standard_text_value VARCHAR(1000),
	action_type VARCHAR(50),
	modality VARCHAR(1000),
	CONSTRAINT pk_act_activity_id PRIMARY KEY (activity_id),
	CONSTRAINT fk_act_action_type FOREIGN KEY(action_type) REFERENCES action_type (action_type) ON DELETE CASCADE,
	CONSTRAINT fk_act_assay_id FOREIGN KEY(assay_id) REFERENCES assays (assay_id) ON DELETE CASCADE,
	CONSTRAINT fk_act_bao_endpoint FOREIGN KEY(bao_endpoint) REFERENCES bioassay_ontology (bao_id) ON DELETE CASCADE,
	CONSTRAINT fk_act_doc_id FOREIGN KEY(doc_id) REFERENCES docs (doc_id) ON DELETE CASCADE,
	CONSTRAINT fk_act_molregno FOREIGN KEY(molregno) REFERENCES molecule_dictionary (molregno) ON DELETE CASCADE,
	CONSTRAINT fk_act_record_id FOREIGN KEY(record_id) REFERENCES compound_records (record_id) ON DELETE CASCADE,
	CONSTRAINT fk_act_src_id FOREIGN KEY(src_id) REFERENCES source (src_id) ON DELETE CASCADE,
	CONSTRAINT fk_data_val_comm FOREIGN KEY(data_validity_comment) REFERENCES data_validity_lookup (data_validity_comment) ON DELETE CASCADE,
	CONSTRAINT ck_potential_dup CHECK (POTENTIAL_DUPLICATE IN (0,1)),
	CONSTRAINT ck_stand_flag CHECK (standard_flag in (0,1)),
	CONSTRAINT ck_stand_relation CHECK (standard_relation in ('>','<','=','~','<=','>=','<<','>>'))
);
CREATE TABLE assays (
	assay_id BIGINT NOT NULL,
	doc_id BIGINT NOT NULL,
	description VARCHAR(4000),
	assay_type VARCHAR(1),
	assay_test_type VARCHAR(20),
	assay_category VARCHAR(50),
	assay_organism VARCHAR(250),
	assay_tax_id BIGINT,
	assay_strain VARCHAR(200),
	assay_tissue VARCHAR(100),
	assay_cell_type VARCHAR(100),
	assay_subcellular_fraction VARCHAR(100),
	tid BIGINT,
	relationship_type VARCHAR(1),
	confidence_score SMALLINT,
	src_id INTEGER NOT NULL,
	src_assay_id VARCHAR(50),
	chembl_id VARCHAR(20) NOT NULL,
	cell_id BIGINT,
	bao_format VARCHAR(11),
	tissue_id BIGINT,
	variant_id BIGINT,
	aidx VARCHAR(200) NOT NULL,
	assay_group VARCHAR(200),
	CONSTRAINT pk_assays_assay_id PRIMARY KEY (assay_id),
	CONSTRAINT fk_assays_assaytype FOREIGN KEY(assay_type) REFERENCES assay_type (assay_type) ON DELETE CASCADE,
	CONSTRAINT fk_assays_cell_id FOREIGN KEY(cell_id) REFERENCES cell_dictionary (cell_id) ON DELETE CASCADE,
	CONSTRAINT fk_assays_chembl_id FOREIGN KEY(chembl_id) REFERENCES chembl_id_lookup (chembl_id) ON DELETE CASCADE,
	CONSTRAINT fk_assays_confscore FOREIGN KEY(confidence_score) REFERENCES confidence_score_lookup (confidence_score) ON DELETE CASCADE,
	CONSTRAINT fk_assays_doc_id FOREIGN KEY(doc_id) REFERENCES docs (doc_id) ON DELETE CASCADE,
	CONSTRAINT fk_assays_reltype FOREIGN KEY(relationship_type) REFERENCES relationship_type (relationship_type) ON DELETE CASCADE,
	CONSTRAINT fk_assays_src_id FOREIGN KEY(src_id) REFERENCES source (src_id) ON DELETE CASCADE,
	CONSTRAINT fk_assays_tid FOREIGN KEY(tid) REFERENCES target_dictionary (tid) ON DELETE CASCADE,
	CONSTRAINT fk_assays_tissue_id FOREIGN KEY(tissue_id) REFERENCES tissue_dictionary (tissue_id) ON DELETE CASCADE,
	CONSTRAINT fk_assays_variant_id FOREIGN KEY(variant_id) REFERENCES variant_sequences (variant_id) ON DELETE CASCADE,
	CONSTRAINT fk_chembl_bao_format FOREIGN KEY(bao_format) REFERENCES bioassay_ontology (bao_id) ON DELETE CASCADE,
	CONSTRAINT ck_assays_category CHECK (assay_category in
               ('screening', 'panel', 'confirmatory', 'summary', 'other', 'Thermal shift assay QC liability',
                'Thermal shift assay', 'Affinity biochemical assay', 'Incucyte cell viability',
                'Affinity phenotypic cellular assay', 'HTRF assay', 'Selectivity assay', 'Cell health data',
                'NanoBRET assay', 'Alphascreen assay', 'Affinity on-target cellular assay', 'ITC assay',
                'GPCR beta-arrestin recruitment assay', 'PDSP assay')),
	CONSTRAINT ck_assays_chemblid CHECK (chembl_id like ('CHEMBL%')),
	CONSTRAINT ck_assays_testtype CHECK (assay_test_type in ('In vivo','In vitro','Ex vivo')),
	CONSTRAINT uk_assays_chemblid UNIQUE (chembl_id)
);
CREATE TABLE molecule_dictionary (
	molregno BIGINT NOT NULL,
	pref_name VARCHAR(255),
	chembl_id VARCHAR(20) NOT NULL,
	max_phase NUMERIC(2, 1),
	therapeutic_flag SMALLINT NOT NULL,
	dosed_ingredient SMALLINT NOT NULL,
	structure_type VARCHAR(10) NOT NULL,
	molecule_type VARCHAR(30),
	first_approval INTEGER,
	oral SMALLINT NOT NULL,
	parenteral SMALLINT NOT NULL,
	topical SMALLINT NOT NULL,
	black_box_warning SMALLINT NOT NULL,
	natural_product SMALLINT NOT NULL,
	first_in_class SMALLINT NOT NULL,
	chirality SMALLINT NOT NULL,
	prodrug SMALLINT NOT NULL,
	inorganic_flag SMALLINT NOT NULL,
	usan_year INTEGER,
	availability_type SMALLINT,
	usan_stem VARCHAR(50),
	polymer_flag SMALLINT,
	usan_substem VARCHAR(50),
	usan_stem_definition VARCHAR(1000),
	withdrawn_flag SMALLINT NOT NULL,
	chemical_probe SMALLINT NOT NULL,
	orphan SMALLINT NOT NULL,
	veterinary SMALLINT,
	CONSTRAINT pk_moldict_molregno PRIMARY KEY (molregno),
	CONSTRAINT fk_moldict_chembl_id FOREIGN KEY(chembl_id) REFERENCES chembl_id_lookup (chembl_id) ON DELETE CASCADE,
	CONSTRAINT ck_moldict_app CHECK (first_approval < 2050 and first_approval > 1900),
	CONSTRAINT ck_moldict_bbw CHECK (black_box_warning in (-1,0,1)),
	CONSTRAINT ck_moldict_chi CHECK (chirality in (-1,0,1,2)),
	CONSTRAINT ck_moldict_dosed CHECK (dosed_ingredient in (0,1)),
	CONSTRAINT ck_moldict_fic CHECK (first_in_class in (-1,0,1)),
	CONSTRAINT ck_moldict_inor CHECK (inorganic_flag in (-1,0,1)),
	CONSTRAINT ck_moldict_np CHECK (natural_product in (-1,0,1)),
	CONSTRAINT ck_moldict_oral CHECK (oral in (0,1)),
	CONSTRAINT ck_moldict_par CHECK (parenteral in (0,1)),
	CONSTRAINT ck_moldict_polyflag CHECK (polymer_flag IN (0, 1, null)),
	CONSTRAINT ck_moldict_pro CHECK (prodrug in (-1,0,1)),
	CONSTRAINT ck_moldict_strtype CHECK (structure_type in ('NONE','MOL','SEQ','BOTH')),
	CONSTRAINT ck_moldict_theraflag CHECK (therapeutic_flag IN (0, 1)),
	CONSTRAINT ck_moldict_top CHECK (topical in (0,1)),
	CONSTRAINT ck_moldict_usanyear CHECK (usan_year > 1900 and usan_year < 2050),
	CONSTRAINT ck_moldict_withd CHECK (WITHDRAWN_FLAG in (0,1)),
	CONSTRAINT uk_moldict_chemblid UNIQUE (chembl_id)
);
CREATE TABLE molecule_synonyms (
	molregno BIGINT NOT NULL,
	syn_type VARCHAR(50) NOT NULL,
	molsyn_id BIGINT NOT NULL,
	synonyms VARCHAR(250),
	CONSTRAINT pk_cmpdsyns_synid PRIMARY KEY (molsyn_id),
	CONSTRAINT fk_cmpdsyns_molregno FOREIGN KEY(molregno) REFERENCES molecule_dictionary (molregno) ON DELETE CASCADE,
	CONSTRAINT uk_cmpdsyns UNIQUE (molregno, syn_type, synonyms)
);
CREATE TABLE target_dictionary (
	tid BIGINT NOT NULL,
	target_type VARCHAR(30),
	pref_name VARCHAR(200) NOT NULL,
	tax_id BIGINT,
	organism VARCHAR(150),
	chembl_id VARCHAR(20) NOT NULL,
	species_group_flag SMALLINT NOT NULL,
	CONSTRAINT pk_targdict_tid PRIMARY KEY (tid),
	CONSTRAINT fk_targdict_chembl_id FOREIGN KEY(chembl_id) REFERENCES chembl_id_lookup (chembl_id) ON DELETE CASCADE,
	CONSTRAINT fk_targdict_target_type FOREIGN KEY(target_type) REFERENCES target_type (target_type) ON DELETE CASCADE,
	CONSTRAINT ck_targdict_species CHECK (species_group_flag in (0,1)),
	CONSTRAINT uk_targdict_chemblid UNIQUE (chembl_id)
);
CREATE TABLE target_components (
	tid BIGINT NOT NULL,
	component_id BIGINT NOT NULL,
	targcomp_id BIGINT NOT NULL,
	homologue SMALLINT NOT NULL,
	CONSTRAINT pk_targcomp_id PRIMARY KEY (targcomp_id),
	CONSTRAINT fk_targcomp_compid FOREIGN KEY(component_id) REFERENCES component_sequences (component_id) ON DELETE CASCADE,
	CONSTRAINT fk_targcomp_tid FOREIGN KEY(tid) REFERENCES target_dictionary (tid) ON DELETE CASCADE,
	CONSTRAINT ck_targcomp_hom CHECK (homologue in (0,1,2)),
	CONSTRAINT uk_targcomp_tid_compid UNIQUE (tid, component_id)
);
CREATE TABLE component_sequences (
	component_id BIGINT NOT NULL,
	component_type VARCHAR(50),
	accession VARCHAR(25),
	sequence TEXT,
	sequence_md5sum VARCHAR(32),
	description VARCHAR(200),
	tax_id BIGINT,
	organism VARCHAR(150),
	db_source VARCHAR(25),
	db_version VARCHAR(10),
	CONSTRAINT pk_targcomp_seqs_compid PRIMARY KEY (component_id),
	CONSTRAINT ck_targcomp_seqs_src CHECK (db_source in ('SWISS-PROT','TREMBL','Manual')),
	CONSTRAINT ck_targcomp_seqs_taxid CHECK (tax_id > 0),
	CONSTRAINT ck_targcomp_seqs_type CHECK (component_type in ('PROTEIN','DNA','RNA')),
	CONSTRAINT uk_targcomp_seqs_acc UNIQUE (accession)
);
"""

# Real-database facts this fixture mirrors (verified read-only against
# data/chembl/chembl_37_sqlite/chembl_37.db on 2026-10-22):
#   CHEMBL941  -> molregno 88797, pref_name 'IMATINIB'   (upper-case)
#   synonyms for 88797 are 'Imatinib' (ATC/BAN/INN), 'GLEEVEC', 'CGP-57148B'
#     -- note there is NO all-lower-case 'imatinib' row, which is exactly
#     why the old case-sensitive lookup missed it.
#   CHEMBL1421 -> dasatinib (pref_name 'DASATINIB')
#   ABL1 P00519 -> CHEMBL1862 ; ABL2 P00520 -> CHEMBL4013
# The activity VALUES below are FABRICATED.
_REAL_IMATINIB_MOLREGNO = 88797
_REAL_DASATINIB_MOLREGNO = 88798


def _write_synthetic_chembl(db_path: Path) -> Path:
    """Write a synthetic ChEMBL 37 SQLite database using the REAL
    ChEMBL 37 table definitions for every table the wrapper touches.

    The DDL is verbatim from the real database (see
    ``_REAL_CHEMBL_37_DDL`` above). The rows are fabricated.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.executescript(_REAL_CHEMBL_37_DDL)

    # --- target_dictionary: ABL1 (CHEMBL1862), ABL2 (CHEMBL4013) ------
    conn.executemany(
        "INSERT INTO target_dictionary "
        "(tid, target_type, pref_name, tax_id, organism, chembl_id, "
        " species_group_flag) VALUES (?,?,?,?,?,?,?)",
        [
            (1, "SINGLE PROTEIN", "Tyrosine-protein kinase ABL1", 9606,
             "Homo sapiens", "CHEMBL1862", 0),
            (2, "SINGLE PROTEIN", "Tyrosine-protein kinase ABL2", 9606,
             "Homo sapiens", "CHEMBL4013", 0),
        ],
    )
    # --- target_components: the tid -> component_id bridge --------------
    conn.executemany(
        "INSERT INTO target_components (tid, component_id, targcomp_id, "
        "homologue) VALUES (?,?,?,?)",
        [(1, 1, 1, 0), (2, 2, 2, 0)],
    )
    # --- component_sequences: ABL1 -> P00519, ABL2 -> P00520 -----------
    conn.executemany(
        "INSERT INTO component_sequences (component_id, component_type, "
        "accession, sequence, sequence_md5sum, description, tax_id, "
        "organism, db_source, db_version) VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            (1, "PROTEIN", "P00519", "MGSNKSKPKDASQRRRSLE", "0"*32,
             "Tyrosine-protein kinase ABL1", 9606, "Homo sapiens",
             "SWISS-PROT", "385"),
            (2, "PROTEIN", "P00520", "MAVLYDITSRQEHL", "1"*32,
             "Tyrosine-protein kinase ABL2", 9606, "Homo sapiens",
             "SWISS-PROT", "385"),
        ],
    )
    # --- molecule_dictionary: imatinib + dasatinib --------------------
    # (the long flag tail is fixed at 0 / 'MOL' to satisfy the real
    #  NOT NULL + CHECK constraints the real DDL carries)
    conn.executemany(
        "INSERT INTO molecule_dictionary (molregno, pref_name, chembl_id, "
        " max_phase, therapeutic_flag, dosed_ingredient, structure_type, "
        " molecule_type, first_approval, oral, parenteral, topical, "
        " black_box_warning, natural_product, first_in_class, chirality, "
        " prodrug, inorganic_flag, withdrawn_flag, chemical_probe, orphan)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (_REAL_IMATINIB_MOLREGNO, "IMATINIB", "CHEMBL941", 4, 1, 1,
             "MOL", "Small molecule", 2001,
             1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (_REAL_DASATINIB_MOLREGNO, "DASATINIB", "CHEMBL1421", 4, 1, 1,
             "MOL", "Small molecule", 2006,
             1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ],
    )
    # --- molecule_synonyms: real ChEMBL casing, no lower-case 'imatinib'
    conn.executemany(
        "INSERT INTO molecule_synonyms (molregno, syn_type, molsyn_id, "
        "synonyms) VALUES (?,?,?,?)",
        [
            (_REAL_IMATINIB_MOLREGNO, "INN", 3277892, "Imatinib"),
            (_REAL_IMATINIB_MOLREGNO, "PND", 3398784, "GLEEVEC"),
            (_REAL_IMATINIB_MOLREGNO, "PND", 3398793, "CGP057148B"),
            (_REAL_DASATINIB_MOLREGNO, "INN", 3286812, "Dasatinib"),
            (_REAL_DASATINIB_MOLREGNO, "PND", 3398799, "BMS-354825"),
        ],
    )
    # --- assays: carry tid (target link) + confidence_score -----------
    conn.executemany(
        "INSERT INTO assays (assay_id, doc_id, description, assay_type, "
        " assay_test_type, assay_category, assay_organism, assay_tax_id, "
        " tid, relationship_type, confidence_score, src_id, chembl_id, "
        " aidx) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (101, 90001, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 1, "=", 9, 1, "CHEMBL686370",
             "FABRICATED-AIDX-101"),
            (102, 90002, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 1, "=", 9, 1, "CHEMBL686371",
             "FABRICATED-AIDX-102"),
            (103, 90003, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 1, "=", 8, 1, "CHEMBL686372",
             "FABRICATED-AIDX-103"),
            (104, 90004, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 1, "=", 7, 1, "CHEMBL686373",
             "FABRICATED-AIDX-104"),
            (105, 90005, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 1, "=", 9, 1, "CHEMBL686374",
             "FABRICATED-AIDX-105"),
            (106, 90006, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 2, "=", 6, 1, "CHEMBL686375",
             "FABRICATED-AIDX-106"),
            (107, 90007, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 1, "=", 9, 1, "CHEMBL686376",
             "FABRICATED-AIDX-107"),
            (108, 90008, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 1, "=", 9, 1, "CHEMBL686377",
             "FABRICATED-AIDX-108"),
            (109, 90009, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 1, "=", 8, 1, "CHEMBL686378",
             "FABRICATED-AIDX-109"),
            (110, 90010, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 2, "=", 7, 1, "CHEMBL686379",
             "FABRICATED-AIDX-110"),
            (111, 90011, "FABRICATED binding assay", "B", "In vitro", "confirmatory",
             "Homo sapiens", 9606, 2, "=", 6, 1, "CHEMBL686380",
             "FABRICATED-AIDX-111"),
        ],
    )
    # --- activities: FABRICATED values, real column set ----------------
    # (activity_id, assay_id, doc_id, record_id, molregno,
    #  standard_relation, standard_value, standard_units, standard_flag,
    #  standard_type, pchembl_value, src_id, type, units)
    rows = [
        (1, 101, 90001, 80001, _REAL_IMATINIB_MOLREGNO, "=", 13.0, "nM", 1,
         "IC50", 7.9, 1, "IC50", "nM"),
        (2, 102, 90002, 80001, _REAL_IMATINIB_MOLREGNO, "=", 25.0, "nM", 1,
         "IC50", 7.6, 1, "IC50", "nM"),
        (3, 103, 90003, 80001, _REAL_IMATINIB_MOLREGNO, "=", 600.0, "nM", 1,
         "IC50", 6.2, 1, "IC50", "nM"),
        (4, 104, 90004, 80001, _REAL_IMATINIB_MOLREGNO, "=", 2800.0, "nM", 1,
         "IC50", 5.6, 1, "IC50", "nM"),
        (5, 105, 90005, 80001, _REAL_IMATINIB_MOLREGNO, "=", 10.0, "nM", 1,
         "Ki", 8.0, 1, "Ki", "nM"),
        (6, 106, 90006, 80001, _REAL_IMATINIB_MOLREGNO, "=", 7000.0, "nM", 1,
         "IC50", 5.2, 1, "IC50", "nM"),
        (7, 107, 90007, 80002, _REAL_DASATINIB_MOLREGNO, "=", 0.5, "nM", 1,
         "IC50", 9.3, 1, "IC50", "nM"),
        (8, 108, 90008, 80002, _REAL_DASATINIB_MOLREGNO, "=", 0.8, "nM", 1,
         "IC50", 9.1, 1, "IC50", "nM"),
        (9, 109, 90009, 80002, _REAL_DASATINIB_MOLREGNO, "=", 1.2, "nM", 1,
         "IC50", 8.9, 1, "IC50", "nM"),
        (10, 110, 90010, 80002, _REAL_DASATINIB_MOLREGNO, "=", 50.0, "nM", 1,
         "IC50", 7.3, 1, "IC50", "nM"),
        (11, 111, 90011, 80002, _REAL_DASATINIB_MOLREGNO, "=", 100.0, "nM", 1,
         "IC50", 7.0, 1, "IC50", "nM"),
    ]
    conn.executemany(
        "INSERT INTO activities (activity_id, assay_id, doc_id, record_id, "
        " molregno, standard_relation, standard_value, standard_units, "
        " standard_flag, standard_type, pchembl_value, src_id, type, units)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def synthetic_chembl(tmp_path: Path) -> Path:
    """Real-schema fixture with the LEGACY single ``MANIFEST`` file.

    The legacy layout is still supported by ``_read_manifest`` and keeps
    the historical ``downloaded_at`` assertion honest. The per-file
    ``MANIFEST.<name>`` layout that the real fetch script writes is
    covered separately by ``real_layout_chembl``.
    """
    db = tmp_path / "chembl_37.db"
    _write_synthetic_chembl(db)
    manifest = tmp_path / "MANIFEST"
    manifest.write_text(
        "url: https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/chembl_37_sqlite.tar.gz\n"
        "size_bytes: 5764252857\n"
        "downloaded_at: 2026-10-11T20:00:00Z\n"
        "tool: curl -L -C -\n"
    )
    return db


@pytest.fixture
def real_layout_chembl(tmp_path: Path) -> Path:
    """Real-schema fixture in the REAL on-disk layout.

    ``scripts/fetch_chembl.py`` (via ``scripts/_resumable.py``) writes a
    PER-FILE manifest named ``MANIFEST.<basename>`` and records
    ``completed_at`` -- there is no legacy ``MANIFEST`` file and no
    ``downloaded_at`` key. That is exactly what exists next to the real
    database in ``data/chembl/chembl_37_sqlite/``.
    """
    d = tmp_path / "real_layout"
    d.mkdir(parents=True, exist_ok=True)
    db = d / "chembl_37.db"
    _write_synthetic_chembl(db)
    (d / "MANIFEST.chembl_37.db").write_text(
        "url: https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/chembl_37_sqlite.tar.gz\n"
        "size_bytes: 5764252857\n"
        "sha256: 33c203740555f96067710cdfc1c3c55d890660e5908ec5cbf5817492c290d281\n"
        "md5: c000a05b0939e4b4f00b9e1cede7d4bf\n"
        "started_at: 2026-10-22T03:55:28Z\n"
        "completed_at: 2026-10-22T05:46:06Z\n"
    )
    return db


def test_b1_known_answer_imatinib_vs_abl1(synthetic_chembl: Path):
    """B1-6: imatinib (CHEMBL941) vs ABL1 (CHEMBL1862) returns >= 1 IC50 in nM."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is True
    assert result["data"]["total_count"] >= 1
    for r in result["data"]["records"]:
        assert r["standard_type"] == "IC50"
        assert r["standard_units"] == "nM"
        assert r["molecule_chembl_id"] == "CHEMBL941"
        assert r["target_chembl_id"] == "CHEMBL1862"


def test_b1_uniprot_resolution_p00519_to_chembl1862(synthetic_chembl: Path):
    """B1-3, B1-7: UniProt P00519 resolves to CHEMBL1862 and returns the same results."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result_chembl = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    result_uniprot = get_chembl_bioactivity(
        "P00519", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result_chembl["success"] is True
    assert result_uniprot["success"] is True
    assert result_chembl["data"]["total_count"] == result_uniprot["data"]["total_count"]
    assert result_uniprot["data"]["target_chembl_id"] == "CHEMBL1862"


def test_b1_compound_name_resolution(synthetic_chembl: Path):
    """B1-4: compound name 'imatinib' resolves to CHEMBL941."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "imatinib", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is True
    assert result["data"]["molecule_chembl_id"] == "CHEMBL941"
    assert result["data"]["total_count"] >= 1


def test_b1_compound_synonym_resolution(synthetic_chembl: Path):
    """B1-4: compound synonym 'Gleevec' resolves to CHEMBL941 via molecule_synonyms."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "Gleevec", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is True
    assert result["data"]["molecule_chembl_id"] == "CHEMBL941"


def test_b1_negative_control_unknown_target(synthetic_chembl: Path):
    """B1-8: unknown target returns 0 records with success=True."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL99999999", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is True
    assert result["data"]["total_count"] == 0
    assert result["data"]["records"] == []


def test_b1_negative_control_unknown_compound(synthetic_chembl: Path):
    """B1-9: unknown compound returns 0 records with success=True."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL99999999", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is True
    assert result["data"]["total_count"] == 0


def test_b1_negative_control_unknown_gene_name(synthetic_chembl: Path):
    """B1-8: unknown UniProt accession returns success=False."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "ZZZZZZ", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is False
    assert "no ChEMBL target" in result["error"]


def test_b1_standard_type_filter(synthetic_chembl: Path):
    """B1-5: Ki filter returns only Ki records (imatinib vs ABL1 has 1 Ki)."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "Ki", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is True
    assert result["data"]["total_count"] == 1
    assert result["data"]["records"][0]["standard_type"] == "Ki"


def test_b1_max_records_limit(synthetic_chembl: Path):
    """B1-11: max_records limits the number of returned records."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=2,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is True
    assert len(result["data"]["records"]) == 2


def test_b1_determinism(synthetic_chembl: Path):
    """B1-10: two calls return the same records in the same order."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    a = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    b = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert a["data"]["records"] == b["data"]["records"]


def test_b1_return_contract_keys(synthetic_chembl: Path):
    """B1-15: the function returns the standard 6 keys."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    for key in ("success", "data", "source", "source_version", "query_time_utc"):
        assert key in result


def test_b1_local_source_field(synthetic_chembl: Path):
    """B1-12: local mode sets data.source to 'local:chembl_37:<downloaded_at>'."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["data"]["source"].startswith("local:chembl_37:")
    assert result["data"]["release_date"] == "2026-10-11T20:00:00Z"


def test_b1_invalid_target_returns_success_false(synthetic_chembl: Path):
    """B1-14: empty or None target returns success=False."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    assert get_chembl_bioactivity("", "CHEMBL941", "IC50", mode="local", data_path=synthetic_chembl)["success"] is False
    assert get_chembl_bioactivity(None, "CHEMBL941", "IC50", mode="local", data_path=synthetic_chembl)["success"] is False


def test_b1_invalid_standard_type_returns_success_false(synthetic_chembl: Path):
    """B1-14: invalid standard_type returns success=False."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "bogus", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is False
    assert "standard_type" in result["error"]


def test_b1_invalid_max_records_returns_success_false(synthetic_chembl: Path):
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    assert get_chembl_bioactivity("CHEMBL1862", "CHEMBL941", "IC50", max_records=0, mode="local", data_path=synthetic_chembl)["data"]["total_count"] == 0
    result = get_chembl_bioactivity("CHEMBL1862", "CHEMBL941", "IC50", max_records=-1, mode="local", data_path=synthetic_chembl)
    assert result["success"] is False


def test_b1_invalid_mode_returns_success_false(synthetic_chembl: Path):
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", mode="bogus",
        data_path=synthetic_chembl,
    )
    assert result["success"] is False
    assert "mode" in result["error"]


def test_b1_missing_file_returns_graceful_error(tmp_path: Path):
    """B1-3: local mode with missing file returns success=False."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    missing = tmp_path / "does_not_exist.db"
    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", mode="local", data_path=missing,
    )
    assert result["success"] is False
    assert "not found" in result["error"].lower()
    assert "fetch_chembl.py" in result["error"]


def test_b1_web_api_fallback():
    """B1-13: web API fallback uses the ChEMBL REST API."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    fake_response = mock.Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "activities": [
            {
                "activity_id": 1,
                "molecule_chembl_id": "CHEMBL941",
                "target_chembl_id": "CHEMBL1862",
                "standard_type": "IC50",
                "standard_value": 13.0,
                "standard_units": "nM",
                "standard_relation": "=",
                "assay_chembl_id": "CHEMBL686370",
                "confidence_score": 9,
            }
        ]
    }

    with mock.patch(
        "biomni.tool.get_chembl_bioactivity.requests.get",
        return_value=fake_response,
    ):
        result = get_chembl_bioactivity(
            "CHEMBL1862", "CHEMBL941", "IC50", max_records=20, mode="web",
        )
    assert result["success"] is True
    assert result["data"]["total_count"] == 1
    assert result["data"]["source"].startswith("web:")
    assert result["data"]["release_date"] is None


def test_b1_sql_injection_blocked(synthetic_chembl: Path):
    """B1-18: arbitrary string parameters cannot inject SQL."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    # Try SQL injection in the target parameter
    result = get_chembl_bioactivity(
        "P00519'; DROP TABLE activities; --", "CHEMBL941", "IC50",
        max_results=20,  # type: ignore[name-defined]
        mode="local", data_path=synthetic_chembl,
    )
    # The injection attempt should fail gracefully (no target found)
    # and NOT drop the activities table.
    assert result["success"] is False

    # Verify the activities table still exists and has data.
    result2 = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result2["success"] is True
    assert result2["data"]["total_count"] >= 1


# ---------------------------------------------------------------------------
# Regression tests for the three defects the live run exposed.
#
# Each of these fails against the pre-27a9956 wrapper and passes after.
# They exist because the original fixture was hand-written and agreed
# with the wrapper's wrong assumptions, so the suite was green while
# every real-DB query was broken. The fixture above now uses the real
# ChEMBL 37 DDL, which is what makes these tests able to fail at all.
# ---------------------------------------------------------------------------


def test_b1_regression_activities_has_no_target_column(synthetic_chembl: Path):
    """Defect 1: `activities` must NOT carry target/assay/confidence
    columns, which is why the query needs the two-hop join.

    Before the fix the wrapper selected a.target_chembl_id directly and
    every real query raised "no such column: a.target_chembl_id". This
    test pins the schema fact that makes that query shape invalid, so a
    future edit that reintroduces it fails here first.
    """
    conn = sqlite3.connect(str(synthetic_chembl))
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(activities)")}
    finally:
        conn.close()
    for absent in ("target_chembl_id", "assay_chembl_id", "confidence_score"):
        assert absent not in cols, (
            f"activities unexpectedly has {absent!r}; if ChEMBL 37 really "
            f"carried it the two-hop join through assays would be redundant"
        )
    # ...and the columns it DOES have that the join relies on.
    for present in ("assay_id", "molregno", "standard_type",
                    "standard_value", "standard_units"):
        assert present in cols


def test_b1_regression_two_hop_join_resolves_target_and_assay(synthetic_chembl: Path):
    """Defect 1: target_chembl_id / assay_chembl_id / confidence_score
    are resolved through activities -> assays -> target_dictionary."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is True, result.get("error")
    recs = result["data"]["records"]
    assert len(recs) == 4
    for r in recs:
        assert r["target_chembl_id"] == "CHEMBL1862"
        assert r["assay_chembl_id"].startswith("CHEMBL")
        assert r["confidence_score"] in (7, 8, 9)
        assert r["activity_id"] in (1, 2, 3, 4)


def test_b1_regression_compound_name_case_insensitive(synthetic_chembl: Path):
    """Defect 2: a lower-case compound name must resolve against the
    upper-case `pref_name` ChEMBL actually stores.

    Real ChEMBL 37 has pref_name 'IMATINIB' and NO all-lower-case
    'imatinib' synonym, so a case-sensitive `=` comparison finds nothing
    and the call raised ValueError.
    """
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    # The fixture genuinely has no lower-case synonym to fall back on.
    conn = sqlite3.connect(str(synthetic_chembl))
    try:
        lower_hits = conn.execute(
            "SELECT count(*) FROM molecule_synonyms WHERE synonyms = 'imatinib'"
        ).fetchone()[0]
    finally:
        conn.close()
    assert lower_hits == 0, "fixture would not exercise the defect"

    result = get_chembl_bioactivity(
        "CHEMBL1862", "imatinib", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is True, result.get("error")
    assert result["data"]["molecule_chembl_id"] == "CHEMBL941"
    assert result["data"]["total_count"] == 4


def test_b1_regression_synonym_case_insensitive(synthetic_chembl: Path):
    """Defect 2 also affected molecule_synonyms ('gleevec' vs 'GLEEVEC')."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "gleevec", "IC50", max_records=20,
        mode="local", data_path=synthetic_chembl,
    )
    assert result["success"] is True, result.get("error")
    assert result["data"]["molecule_chembl_id"] == "CHEMBL941"


def test_b1_regression_manifest_real_layout_release_date(real_layout_chembl: Path):
    """Defect 3: the real on-disk layout is MANIFEST.<basename> with a
    `completed_at` key; reading only the legacy `MANIFEST` reported
    release_date='unknown'."""
    from biomni.tool.get_chembl_bioactivity import (
        _read_manifest,
        get_chembl_bioactivity,
    )

    manifest = _read_manifest(real_layout_chembl)
    assert manifest["completed_at"] == "2026-10-22T05:46:06Z"

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=20,
        mode="local", data_path=real_layout_chembl,
    )
    assert result["success"] is True, result.get("error")
    assert result["data"]["release_date"] == "2026-10-22T05:46:06Z"
    assert result["data"]["source"] == "local:chembl_37:2026-10-22T05:46:06Z"


def test_b1_regression_autodetect_uses_real_layout(real_layout_chembl: Path):
    """Defect 3 also broke auto-detection: with no legacy `MANIFEST`
    present, mode=None fell through to the web API instead of the local
    database."""
    from biomni.tool.get_chembl_bioactivity import get_chembl_bioactivity

    result = get_chembl_bioactivity(
        "CHEMBL1862", "CHEMBL941", "IC50", max_records=20,
        mode=None, data_path=real_layout_chembl,
    )
    assert result["success"] is True, result.get("error")
    assert result["data"]["source"].startswith("local:chembl_37:")