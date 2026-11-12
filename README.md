# AlloAgent

AlloAgent is an allosteric-research agent built by specializing
[Biomni](https://github.com/snap-stanford/Biomni), the open-source
general-purpose biomedical agent, for allosteric drug discovery. The
AlloAgent agent configuration exposes **45 tools** - 44 of them new to
Biomni, one (`run_python_repl`) modified upstream - in six groups:
structural analysis (12), ML prediction (1), dynamics and networks (3),
database access for allosteric and ligand data (17), database access for
variants and predicted sites (4), and mapping and search (6). The two tools
outside those groups are the import-policy tool and the Python REPL. The
list is frozen in [`alloagent/exposed_tools.txt`](alloagent/exposed_tools.txt)
and applied with `biomni.tool._registration.apply_exposed_tools(agent)`.

Against the Biomni baseline on 120 paired runs per arm, AlloAgent used about
**4.4x fewer tokens** (0.61M vs 2.67M per run), **2.1x fewer steps** (28.5 vs
59.8) and **2.6x less wall time** (352 s vs 911 s), at the same task success
(1 of 120 runs in both arms; the paired difference is 0.0000, p = 1.0). The
numbers are committed in [`benchmark/results/`](benchmark/results/), the
method in [`benchmark/analysis_plan.md`](benchmark/analysis_plan.md), and
the per-tool evidence in [`docs/tool_cards/`](docs/tool_cards/).

Paper: [link to be added]

## Quick start

### 1. Build the image

The allosteric tools call programs the image carries - fpocket 4.2.3,
P2Rank 2.5.1, AutoDock Vina 1.2.7, PocketMiner, ProDy, Biotite - so run
AlloAgent from its container.

```bash
git clone https://github.com/Verkhivker-Research-Group/AlloAgent.git
cd AlloAgent

docker build \
    --target dev \
    --build-arg GIT_COMMIT="$(git rev-parse HEAD)" \
    --build-arg GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD)" \
    -t alloagent-dev:latest .
```

The `eval` target builds the same image with the whole repository copied in
(`docker build --target eval -t alloagent-eval:latest .`). The image
layout, the two conda environments and the secrets policy are described in
[`docs/dev_container.md`](docs/dev_container.md).

### 2. Give the agent a key

The agent reads its provider from the environment. Keep the key in a file
outside the repository and pass it with `--env-file`; never mount a `.env`
into the container (see [`docs/0c_secrets_hygiene.md`](docs/0c_secrets_hygiene.md)).

```bash
cat > /tmp/alloagent.env <<EOF
ANTHROPIC_API_KEY=...
EOF
chmod 600 /tmp/alloagent.env
```

`LLM_SOURCE` (or `BIOMNI_SOURCE`) picks the provider - `OpenAI`,
`AzureOpenAI`, `Anthropic`, `Ollama`, `Gemini`, `Bedrock`, `Groq` or
`Custom` - and `BIOMNI_LLM` names the model. The runs behind the paper used
**MiniMax-M3**, served as an OpenAI-compatible endpoint:

```bash
cat > /tmp/alloagent.env <<EOF
MINIMAX_API_KEY=...
BIOMNI_LLM=MiniMax-M3
BIOMNI_SOURCE=Custom
BIOMNI_CUSTOM_BASE_URL=https://api.minimax.io/v1
EOF
```

(`MINIMAX_API_KEY` is the key variable the run scripts read; the agent reads
`BIOMNI_CUSTOM_API_KEY`.) Any provider the configuration supports can be
used instead - set `LLM_SOURCE` and the matching key.

### 3. Run the agent

```bash
docker run --rm -it \
    --env-file /tmp/alloagent.env \
    -v "$(pwd):/workspace" \
    -w /workspace \
    alloagent-dev:latest \
    /opt/conda/envs/alloagent_e1/bin/python
```

```python
from biomni.agent import A1

agent = A1(path="./data", llm="MiniMax-M3")
agent.go(
    "In PDB entry 1T4J (human PTP1B, UniProt P18031), identify the bound "
    "allosteric ligand and list the residues within 4 angstroms of it, "
    "using UniProt numbering."
)
```

That is one of the benchmark prompts. The tool it reaches
(`get_ligand_contacts`) fetches the entry from RCSB and returns the 11
residues within 4 A of the allosteric ligand FRJ.

## Data

The AlloAgent tools read six sources that Biomni's data lake does not
carry. Three of them are fetched with the scripts in `scripts/`; the other
three are snapshots of the data lake that the agent mounts read-only.

| source | what it is | how to get it |
| --- | --- | --- |
| **ChEMBL 37** | the ChEMBL 37 SQLite release the bioactivity tool queries | `python scripts/fetch_chembl.py --download --out ./data/chembl` (5.4 GB tarball) |
| **ClinVar** | the NCBI ClinVar variant summary | `python scripts/fetch_clinvar.py --download --out ./data/clinvar` |
| **AlphaMissense** | the DeepMind pathogenicity score per substitution | `python scripts/fetch_alphamissense.py --download --out ./data/alphamissense` |
| **ASD** (Allosteric Database) | curated allosteric sites and modulators, with the XF functional files and the 2D/3D structures of the modulators | not redistributed: it is academic use with per-request registration, so you fetch it yourself and mount it read-only at `/biolab_data/asd` |
| **BioLiP** | protein-ligand interaction snapshots (interactions, proteins, DNA, RNA, peptides) | mounted read-only at `/biolab_data` |
| **CovalentInDB** | the covalent-probe attachment sites | mounted read-only at `/biolab_data/data_lake/CovInDB_All.csv` |

The scripts print the file sizes before they download (`--check-size`) and
record the checksum of every file they fetch. The PDB structures the
structural tools parse are fetched with
`python scripts/fetch_structure_cache.py ./data/structures`. The three
mounted snapshots have their paths fixed in the tool wrappers;
`ASD_ROOT`, `ALLOAGENT_BIOLIP_DIR` and `ALLOAGENT_COVINDB` override them.

The licence and the terms of every source - including the ASD registration -
are in [`THIRD_PARTY_LICENSES`](THIRD_PARTY_LICENSES).

## Tools

| group | tools | what they use |
| --- | ---: | --- |
| structural analysis | 12 | pocket detection with fpocket 4.2.3 and P2Rank 2.5.1, ligand contacts from the RCSB mmCIF and the SIFTS alignment, residue geometry, accessibility and hydration, and the combined allosteric-site workflow |
| ML prediction | 1 | PocketMiner pocket scoring, a learned model with its weights in the image |
| dynamics and networks | 3 | ProDy normal modes (ANM/GNM), the residue contact network (Biotite + NetworkX) and AutoDock Vina docking |
| database access for allosteric and ligand data | 17 | the Allosteric Database and BioLiP snapshots, ChEMBL 37 (local SQLite or the web service), PubChem, CovalentInDB and the large-dataset reader |
| database access for variants and predicted sites | 4 | UniProt variants, ClinVar, the AlphaMissense scores and the STINGAllo predicted-residue service |
| mapping and search | 6 | the PDBe SIFTS mappings API, the RCSB Search API and the structure lookups |

Every tool has a card under [`docs/tool_cards/`](docs/tool_cards/) with the
question it answers, its inputs, its sources and its versions;
[`docs/new_tools_and_data.md`](docs/new_tools_and_data.md) has the full
table of the 44 new tools and the seven data sources that are not upstream.

## Benchmark

[`benchmark/`](benchmark/) holds the evaluation prompts, the validated
checklists, the launch and restricted prompt sets, the scorer, the judge
material and the results of the 240-run analysis set. It is self-contained
and can be deleted: nothing outside the folder reads from it or breaks when
it is removed.

```bash
pytest benchmark/tests/
```

The judge-batch tests read the run records of the launch, which are not part
of this repository; they error out in a fresh clone until those records are
in place.

## Security

The agent executes LLM-generated code with full system privileges. Run it in
a container or a sandbox, not on a machine you care about, and keep the
write mounts to a scratch directory. The Python REPL can refuse whole module
prefixes (`set_restricted_imports`); the policy is enforced by a static scan
and by the importer itself.

## License

AlloAgent is released under the Apache License 2.0 ([`LICENSE`](LICENSE)).
Biomni itself is Apache 2.0-licensed, but certain integrated tools,
databases, or software may carry more restrictive commercial licenses.
Review each component carefully before any commercial use - the licences and
terms of every third-party tool and dataset are listed in
[`THIRD_PARTY_LICENSES`](THIRD_PARTY_LICENSES).

## Acknowledgments

AlloAgent is built on [Biomni](https://github.com/snap-stanford/Biomni), the
open-source general-purpose biomedical AI agent by the Biomni team, and
keeps its agent framework, its tool registry and its data lake.

### Please cite Biomni if you use this work

```
@article{huang2025biomni,
  title={Biomni: A General-Purpose Biomedical AI Agent},
  author={Huang, Kexin and Zhang, Serena and Wang, Hanchen and Qu, Yuanhao and Lu, Yingzhou and Roohani, Yusuf and Li, Ryan and Qiu, Lin and Zhang, Junze and Di, Yin and others},
  journal={bioRxiv},
  pages={2025--05},
  year={2025},
  publisher={Cold Spring Harbor Laboratory}
}
```
