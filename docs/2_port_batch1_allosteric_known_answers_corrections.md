# Dated corrections to the port batch 1 known answers

**Dated 2026-10-23.** Per the standing rule the criteria file
`docs/2_port_batch1_allosteric_known_answers.md` is NOT edited; the
corrections are recorded here, each with the evidence that forced it.

The batch was implemented and run once. Three expectations in that file
did not match reality. The implementation was changed to match the
*intent* of each expectation, and the two expectations that were simply
wrong about the upstream API are corrected here.

## C-1 — A-3: `"XXXX"` is a 4-character id, so it never reaches the length check

A-3 states that input `"XXXX"` returns `success=False` with an error
mentioning the 4-character requirement. It does not: `"XXXX"` **is**
four characters, so the length check passes and the tool queries PDBe.

**Evidence** (in-container run, 2026-10-23):

```
E  AssertionError: assert '4-character' in "PDBe request failed:
   HTTPError('404 Client Error: Not Found for url:
   https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/XXXX')"
```

**Correction.** The length check fires for any id whose length is not
4. The negative control for it is a 5-character id, e.g. `"1TIMX"`.
`"XXXX"` is the negative control for the *lookup* (see C-2), not for
the length check.

**Why the implementation was left as is.** The length check is correct
and unchanged; only the example in the criteria was wrong.

## C-2 — A-4: PDBe answers 404 for an unknown id, not an empty mapping

A-4 states that input `"ZZZZ"` returns `success=True` with
`chains == {}` and `uniprot_ids == []`. The *outcome* in A-4 is right,
but the mechanism differs: PDBe returns **HTTP 404** for a
well-formed but unknown id, not a 200 with an empty mapping.

**Evidence** (same run):

```
E  AssertionError: PDBe request failed: HTTPError('404 Client Error:
   Not Found for url: .../mappings/uniprot/ZZZZ')
```

**Correction.** A 404 is treated as "no mapping" and the tool returns
`success=True` with `chains == {}` and `uniprot_ids == []`, which is
what A-4 requires. This also matches the old tool's behaviour: the old
`pdb_to_uniprot` called `resp.raise_for_status()` inside a
`try/except requests.RequestException` that returned `{}`.

**Why the implementation was changed.** The first port turned the 404
into `success=False`, which would have made "this structure has no
UniProt mapping" indistinguishable from "the service is broken". The
old behaviour (empty result, not an error) is both correct and
preserved.

## C-3 — A-8: ChEMBL returns `full_mwt` as a string

A-8 states `chembl_properties.molecular_weight == 493.62` (a number).
The ChEMBL web service returns `full_mwt` as the **string** `"493.62"`.

**Evidence** (same run):

```
E  AssertionError: assert '493.62' == 493.62
```

**Correction.** The ported tool coerces the numeric ChEMBL fields to
numbers: `molecular_weight`, `alogp` and `psa` to float,
`first_approval` to int, `max_phase` to float. A missing value stays
`None`. This matches the intent of A-8 (a numeric field) and makes the
returned types consistent with the rest of the contract, which is JSON.

**Why the implementation was changed.** Coercing is the only way the
value can be compared numerically downstream; a string `"493.62"` would
silently break any numeric use of the field.

## Unchanged

A-1, A-2, A-5, A-6, A-7, A-9, A-10, A-11, A-12, A-13, A-14, A-15, A-16,
A-17, A-18, A-19, A-20, A-21 and B-1..B-12 all held as written.

One implementation detail was added without changing any expectation:
`pdb_to_uniprot` now de-duplicates the chain -> accession list. PDBe
returns `P00940` twice for chain A of 1TIM (two sequence ranges,
2-201 and 203-248), and the old tool appended the accession once per
mapping, so `chains["A"]` was `["P00940", "P00940"]`. The `mappings`
list still carries all four entries, so no information is lost.
