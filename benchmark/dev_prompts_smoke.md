# Smoke test - two development prompts, both arms

This is the **smoke test of the pipeline only**: two prompts, two arms,
one repeat. It is NOT the benchmark, and no benchmark prompt is used.

The two prompts are taken verbatim from `benchmark/dev_prompts_capability2.md`
(D2 and D5) - the two that were the fastest in gate 2, so the smoke test
finishes quickly. Their expected answers are in
`benchmark/dev_prompts_capability2.md` and are used for scoring only.

## The prompts

| # | id | prompt | the resource it needs |
|---|---|---|---|
| 1 | D2 | "For PDB entry 1KV2 (human p38 alpha MAP kinase, UniProt Q16539), what does BioLiP record: which ligand, in which protein chain, what are its binding-site residues, and what is the catalytic site?" | the local BioLiP snapshot (the per-entry export is not served as data) |
| 2 | D5 | "For human fructose-1,6-bisphosphatase 1 (UniProt P09467): report the ClinVar classification and the AlphaMissense score of the variants G164S and A177D, and the distance from each of those residues to the AMP allosteric site of PDB entry 1FTA (chain A). Are the two residues part of the AMP site?" | the pinned ClinVar and AlphaMissense releases |
