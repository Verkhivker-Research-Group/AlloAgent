# Dated corrections to the port batch 3 known answers

**Dated 2026-10-23.** Per the standing rule the criteria file
`docs/2_port_batch3_allosteric_core_known_answers.md` is NOT edited; the
corrections are recorded here, each with the evidence that forced it.

The batch was implemented and run once. Four expectations in that file
were wrong, in the same way: they quoted an **unrounded** intermediate
value, or a count that was derived from a different code path, instead
of the value the tool actually returns. The implementation is faithful to
the old code (including its rounding) and was not changed.

## C-4 — E-10: the network has 12 nodes, not 13

E-10 states `network_metrics.total_nodes == 13` and
`allosteric_node_count == 13`.

**Evidence** (in-container run, 2026-10-23):

```
E  assert 12 == 13
```

**Correction.** 12. The ASD XF site residue string for P0AB91 is

```
Chain A:PRO150,GLN151,ALA154,GLY178,LEU179,SER180,PHE209,SER211,LYS214,VAL221; Chain B:ASP6,ASP7,ILE10
```

Splitting on `,` gives **12** pieces, not 13, because the tenth piece is
the combined `"VAL221; Chain B:ASP6"` -- the `; Chain B:` separator
sits inside one comma-delimited field. The 13 figure in the criteria
was taken from the ASD **AS** table, which splits on `;` as well as `,`
and therefore does yield 13 residues (that is the 13 in E-6/E-7). The
two code paths count differently, and E-10 describes the network path.

The implementation was **not** changed: the old code split the same
string the same way, so a port that "fixed" the count would no longer
be a port.

## C-5 — E-17: `avg_distance` is reported rounded to 2 decimals

E-17 states `avg_distance == 5.4861` and `all_distances == [5.486]`.

**Evidence:**

```
E  assert 5.49 == 5.4861
```

**Correction.** `avg_distance == 5.49` and `all_distances == [5.49]`.
The old code returned `round(avg_distance, 2)` and
`round(d, 2)` per distance; the port keeps that rounding. The
unrounded 5.4861 was the probe's intermediate value.

`score == 0.3` was already correct and is unchanged.

## C-6 — E-18: `asphericity` is reported rounded to 3 decimals

E-18 states `asphericity == 0.2102`.

**Evidence:**

```
E  assert np.float64(0.21) == 0.2102
```

**Correction.** `asphericity == 0.21`. The old code returned
`round(A, 3)`; the port keeps that rounding. The unrounded 0.2102 was
the probe's intermediate value.

`volume == 928.3`, `max_extent == 18.74`, `shape_score_pmi == 1.0` and
`score == 1.0` all held as written and are unchanged.

## C-7 — E-20: `avg_conservation` is reported rounded to 3 decimals

E-20 states `avg_conservation == 0.019573`.

**Evidence:**

```
E  assert 0.02 == 0.019573
```

**Correction.** `avg_conservation == 0.02`. The old code returned
`round(avg_conservation, 3)`; the port keeps that rounding. The
unrounded 0.019573 was the probe's intermediate value.

`score == 0.034` and the reproducibility requirement (the same value on
every call, in every process) are unchanged and still hold -- that is
the point of the stable-seed fix.

## Unchanged

E-1..E-9, E-11..E-16, E-18's other fields, E-19 and E-20's score all
held as written on the first run.

Two test bugs were also fixed in the ported test file (not in the
criteria): the two ported old `test_*` functions read `hotspot_count` and
`candidate_count` from the top level of the result, but the contract
nests them under `data`.
