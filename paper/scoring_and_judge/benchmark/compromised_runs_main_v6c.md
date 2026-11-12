# The compromised runs of the main run (launch-2026-10-28-v6c)

The rule, the same for both arms: a run is compromised when its
trace shows it **listing, reading or writing the shared host working
directory outside its own workspace**, or when its **outputs carry our
provenance strings or exposed tool names** that it could only have
learned from another run's files.  The runs proved by the
inventory-based audit (`benchmark/audit_shared_cwd.py`) are included.

A run's **own workspace** is the set of directories it created itself:
the first path component of every file it wrote and every directory it
made.  A path outside that set belongs to another run (or to the
development phase), so listing, reading or writing it exposes the
other runs.

| arm | compromised runs | runs of the arm |
|---|---:|---:|
| alloagent | 10 | 117 |
| baseline | 50 | 117 |

| evidence class | runs |
|---|---:|
| listed | 56 |
| read | 8 |
| the output names our exposed tool | 6 |
| the output carries our provenance string | 2 |
| the answer is identical to baseline/V05_r2 | 1 |
| the answer is identical to baseline/P08_r1 | 1 |

## The list

- **alloagent / C03_r2** (prompt C03, repeat 2) - listed '.', a directory of the shared tree it did not create
- **alloagent / C05_r2** (prompt C05, repeat 2) - listed '.', a directory of the shared tree it did not create
- **alloagent / G02_r1** (prompt G02, repeat 1) - listed '.', a directory of the shared tree it did not create
- **alloagent / H02_r3** (prompt H02, repeat 3) - listed '.', a directory of the shared tree it did not create
- **alloagent / L02_r2** (prompt L02, repeat 2) - the output carries our provenance string 'local:chembl_37'
- **alloagent / L03_r2** (prompt L03, repeat 2) - listed '.', a directory of the shared tree it did not create
- **alloagent / L03_r3** (prompt L03, repeat 3) - listed '.', a directory of the shared tree it did not create; the output carries our provenance string 'local:chembl_37'
- **alloagent / P01_r3** (prompt P01, repeat 3) - listed '.', a directory of the shared tree it did not create
- **alloagent / P03_r1** (prompt P03, repeat 1) - listed '.', a directory of the shared tree it did not create
- **alloagent / P07_r1** (prompt P07, repeat 1) - listed '.', a directory of the shared tree it did not create
- **baseline / C01_r1** (prompt C01, repeat 1) - listed '.', a directory of the shared tree it did not create
- **baseline / C01_r2** (prompt C01, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / C02_r1** (prompt C02, repeat 1) - the output names our exposed tool 'residue_contact_network', which the baseline arm cannot produce
- **baseline / C03_r1** (prompt C03, repeat 1) - listed '.', a directory of the shared tree it did not create
- **baseline / C03_r2** (prompt C03, repeat 2) - the output names our exposed tool 'normal_mode_analysis', which the baseline arm cannot produce
- **baseline / C03_r3** (prompt C03, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / C04_r2** (prompt C04, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / C06_r1** (prompt C06, repeat 1) - read 'workspace/shp2_nma/normal_mode_analysis_source.py', a file another run wrote; read 'workspace/shp2_nma/normal_mode_analysis_source.py', a file another run wrote; listed '.', a directory of the shared tree it did not create
- **baseline / C06_r2** (prompt C06, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / C06_r3** (prompt C06, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / G01_r1** (prompt G01, repeat 1) - listed '.', a directory of the shared tree it did not create
- **baseline / G01_r3** (prompt G01, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / G02_r1** (prompt G02, repeat 1) - read 'work/1opk/1OPK.pdb', a file another run wrote; read 'work/1opk/1OPK.pdb', a file another run wrote; listed '.', a directory of the shared tree it did not create
- **baseline / G02_r3** (prompt G02, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / G03_r1** (prompt G03, repeat 1) - listed '.', a directory of the shared tree it did not create; the output names our exposed tool 'normal_mode_analysis', which the baseline arm cannot produce
- **baseline / G03_r2** (prompt G03, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / G03_r3** (prompt G03, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / G04_r3** (prompt G04, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / H02_r1** (prompt H02, repeat 1) - read '1T4J_ligand_free_out/1T4J_ligand_free_info.txt', a file another run wrote; listed '.', a directory of the shared tree it did not create
- **baseline / H02_r2** (prompt H02, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / H02_r3** (prompt H02, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / K02_r1** (prompt K02, repeat 1) - listed '.', a directory of the shared tree it did not create
- **baseline / K03_r1** (prompt K03, repeat 1) - listed '.', a directory of the shared tree it did not create
- **baseline / K03_r2** (prompt K03, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / P01_r3** (prompt P01, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / P02_r1** (prompt P02, repeat 1) - listed '.', a directory of the shared tree it did not create
- **baseline / P02_r3** (prompt P02, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / P03_r2** (prompt P03, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / P03_r3** (prompt P03, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / P04_r1** (prompt P04, repeat 1) - read 'pocketminer_1btl_1pzo/pocketminer_1BTL_result.json', a file another run wrote; read 'pocketminer_1btl_1pzo/recomputed_fresh_1BTL_top10_and_1PZO_contacts.json', a file another run wrote; listed '.', a directory of the shared tree it did not create
- **baseline / P04_r2** (prompt P04, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / P04_r3** (prompt P04, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / P05_r1** (prompt P05, repeat 1) - listed '.', a directory of the shared tree it did not create
- **baseline / P06_r2** (prompt P06, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / P06_r3** (prompt P06, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / P07_r1** (prompt P07, repeat 1) - listed '.', a directory of the shared tree it did not create
- **baseline / P07_r3** (prompt P07, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / P08_r1** (prompt P08, repeat 1) - the answer is identical to baseline/V05_r2
- **baseline / P08_r2** (prompt P08, repeat 2) - listed '.', a directory of the shared tree it did not create; the output names our exposed tool 'pocketminer_score', which the baseline arm cannot produce
- **baseline / P08_r3** (prompt P08, repeat 3) - listed '.', a directory of the shared tree it did not create; the output names our exposed tool 'pocketminer_score', which the baseline arm cannot produce
- **baseline / S04_r1** (prompt S04, repeat 1) - listed '.', a directory of the shared tree it did not create
- **baseline / S04_r2** (prompt S04, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / S04_r3** (prompt S04, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / V03_r2** (prompt V03, repeat 2) - listed '.', a directory of the shared tree it did not create
- **baseline / V03_r3** (prompt V03, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / V04_r3** (prompt V04, repeat 3) - listed '.', a directory of the shared tree it did not create
- **baseline / V05_r2** (prompt V05, repeat 2) - listed '.', a directory of the shared tree it did not create; the answer is identical to baseline/P08_r1
- **baseline / V06_r1** (prompt V06, repeat 1) - listed '.', a directory of the shared tree it did not create; the output names our exposed tool 'pocketminer_score', which the baseline arm cannot produce
- **baseline / V06_r2** (prompt V06, repeat 2) - read 'temp_1btl_1pzo/1BTL_PocketMiner_top10.csv', a file another run wrote; listed '.', a directory of the shared tree it did not create
- **baseline / V06_r3** (prompt V06, repeat 3) - listed '.', a directory of the shared tree it did not create
