# Part 1 - PocketMiner wrapper: pass criteria (written BEFORE the fix)

Committed before the fix. The numbers come from an **independent
calculation** on 7WVB in `alloagent-eval:v4`: the wrapper was run, and
the per-chain means were computed from the returned per-residue scores
and the structure's own chain assignment, with no UniProt keying
anywhere.

## The defect this fixes

The gate-2 D1 expected answer was built from a dictionary keyed by
UniProt number, which **collapses the four chains of 7WVB** (the last
chain wins). The committed numbers (0.5615 for the contacts, 0.5488
for all residues) are therefore not the numbers any chain actually
has, and they cannot be reproduced from a per-chain result.

## The independent numbers for 7WVB

7WVB (human FBP1, apo R-state) has **1165 standard residues** in four
chains: A 293, B 293, C 293, D 286. The PocketMiner run in
`alloagent-eval:v4` scores all 1165.

| chain | n residues | mean | min | max |
|---|---|---|---|---|
| A | 293 | **0.542914** | 0.061176 | 0.907176 |
| B | 293 | **0.539538** | 0.051388 | 0.902098 |
| C | 293 | **0.545426** | 0.070282 | 0.929240 |
| D | 286 | **0.549240** | 0.058183 | 0.931921 |
| all | 1165 | **0.544250** (0.5442496641798849) | | |

The three numbers recorded in the gate-2 report are consistent with
this: **0.544250** is the mean over all 1165 scored residues,
**0.617489** is the mean over the 10 chain-A-resolved AMP contacts and
**0.584956** the mean over the 11 positions resolved in any chain.

## Criterion 1 - the result carries the chain of every residue

**Criterion: `pocketminer_score` returns, for every scored residue,
the chain it belongs to and its residue number, alongside the
score.** The per-residue chain and residue number must be in the
same order as `residue_scores`, so that a consumer can group the
scores per chain without re-parsing the structure.

## Criterion 2 - the per-chain means are exact

**Criterion: for 7WVB the result exposes four chains with the means
0.542914 (A), 0.539538 (B), 0.545426 (C) and 0.549240 (D), and the
overall mean 0.544250 over 1165 residues.** The per-chain means must
match the table above to six decimals; the wrapper must not round
them away.

## Criterion 3 - the UniProt-keyed collapse cannot happen

**Criterion: the result contains no field that mixes the chains of a
multi-chain structure into one number.** Concretely:

* the per-chain block lists **every** chain of the structure (four for
  7WVB) with its own mean, and the four means are **different**;
* the number of chains in the per-chain block equals the number of
  chains with scored residues, and a structure with one chain still
  reports that chain;
* there is no "the mean for this protein" field that a caller could
  mistake for a per-chain value. The all-residue mean may be reported,
  but it must be named as the all-residue mean and it must not be the
  only aggregate.

**A failing-before test is required**: a test that fails against the
current wrapper (which returns a flat `residue_scores` list with no
chain information at all) and passes after the fix. It must assert
the four per-chain means, the four chain names, and that the four
means are not equal to each other (i.e. the collapse is visible and
prevented).

## What is recorded

The chain names, the per-chain residue counts, the four per-chain
means, the all-residue mean, and the number of scored residues. If a
criterion is not met it is a FAIL with the numbers; the criteria are
not changed afterwards.
