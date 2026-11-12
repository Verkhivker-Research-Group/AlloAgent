# syntax=docker/dockerfile:1.7
#
# AlloAgent-v2 container image.
#
# Layering strategy:
#   1. base-system    : OS packages (git, build-essential, JDK 17, curl).
#   2. base-deps      : alloagent_e1 conda env (numpy, rdkit, gemmi, prody,
#                       biotite, networkx) + langchain/pip deps.
#   3. base-binaries  : fpocket (built from source) + P2Rank (extracted) +
#                       Meeko, vina, torch installed in alloagent_e1.
#   4. base-pocketminer: pocketminer_env (tf 2.15, np 1.26.4, mdtraj) +
#                       PocketMiner + AE-PocketMiner clones, with the
#                       legacy-Adam patch applied via a build-time patch
#                       file (NOT a runtime sed).
#   5. base-appuser   : appuser creation, ownership of /opt, smoke test
#                       of all package imports.
#   6. dev            : bind-mount-friendly target for development.
#                       `COPY . /workspace` is in dev only, so source
#                       edits don't invalidate layers 1-5.
#   7. eval           : same base as dev, but `COPY . /workspace` is
#                       committed (no bind mount). Use this for the
#                       final evaluation image.
#
# Build targets:
#   docker build --target dev  -t alloagent-dev:latest .
#   docker build --target eval -t alloagent-eval:latest .
#
# Development run (bind mount source, code edits need no rebuild):
#   docker run --rm -it \
#       --env-file .env.test \
#       -v "$(pwd):/workspace" \
#       alloagent-dev:latest bash
#
# Evaluation run (image contains the repo, no bind mount):
#   docker run --rm \
#       --env-file .env.test \
#       alloagent-eval:latest pytest /workspace/tests/ -q
#
# Notes:
#   * All secrets are passed via --env-file (not mounted .env files).
#   * The .env.test file is created outside the repo, contains only
#     the variables the tests need, and is deleted after the run.
#   * All build-time work runs as root; the container switches to
#     `appuser` (uid 997) at the end.
#   * The `pocketminer_legacy_adam.patch` is a build-time patch
#     file (NOT a runtime sed). It rewrites
#     `tf.keras.optimizers.Adam` to
#     `tf.keras.optimizers.legacy.Adam` so the TF 1.x checkpoints
#     in PocketMiner / AE-PocketMiner restore correctly under
#     tf 2.15.

# ----------------------------------------------------------------------------
# 1. base-system : OS packages
# ----------------------------------------------------------------------------
FROM condaforge/miniforge3@sha256:f752860f77bd417aa4db35be3d2e906fdb740fb80f40755ed651fff9e8873aad AS base-system

ARG GIT_COMMIT=unknown
ARG GIT_BRANCH=unknown
ARG GIT_DIRTY=unknown
ENV DEBIAN_FRONTEND=noninteractive
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        libnetcdf-dev \
        openjdk-17-jdk \
        curl \
        ca-certificates \
        patch \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
ENV CONDA_ALWAYS_YES=true
ENV GIT_COMMIT=${GIT_COMMIT}
ENV GIT_BRANCH=${GIT_BRANCH}
ENV GIT_DIRTY=${GIT_DIRTY}

# ----------------------------------------------------------------------------
# 2. base-deps : alloagent_e1 conda env
# ----------------------------------------------------------------------------
FROM base-system AS base-deps

RUN mamba create -n alloagent_e1 -c conda-forge -c bioconda -y \
        python=3.11 \
        "numpy>=2.3" \
        "pandas>=2.3" \
        "scipy>=1.16" \
        "scikit-learn>=1.7" \
        "pydantic>=2.13,<3" \
        "biopython>=1.85" \
        "requests>=2.32" \
        "networkx>=3.6" \
        "openai>=2.50,<3" \
        "tiktoken>=0.7" \
        "prody=2.6.1" \
        "biotite=1.6.0" \
        "rdkit=2024.09.6" \
        gemmi

RUN /opt/conda/envs/alloagent_e1/bin/pip install --no-cache-dir \
        "langchain>=0.3,<0.4" \
        "langchain-core<0.4" \
        "langgraph==0.3.18" \
        "langchain-openai<0.4" \
        "langchain-community<0.4" \
        "langchain-anthropic<0.4" \
        "langchain-google-genai<0.4" \
        "python-dotenv>=1.0" \
        "pytest>=7,<9" \
        "meeko==0.8.0" \
        "vina==1.2.7" \
        "torch==2.4.1+cpu" \
        --extra-index-url https://download.pytorch.org/whl/cpu

# Pure-Python pip deps needed by the old (Biolab) alloagent tools'
# thin import paths during the Part B review. Keeps the existing
# pip install layer cached (these are additive).
#
# NOTE: `googlesearch` is intentionally NOT installed here -- it
# scrapes a third-party search engine, which the user flagged as
# a separate decision in the old-tool review (moved out of this tree to ../alloagent_private/docs/old_tool_review/SUMMARY.md). The
# single tool that imports it (`literature.py`) stays PARTIAL
# with a documented "scrapes a search engine" verdict until the
# user explicitly approves the dep.
#
# `transformers` is also NOT installed: the only importer
# (`systems_biology.py::query_chatnt`) uses a deferred
# `from transformers import pipeline` inside the function body,
# so the module-level import of systems_biology.py succeeds
# without transformers. The import-test path used by Part B
# therefore passes. Installing transformers (~2 GB) is
# deferred until query_chatnt is actually exercised.
RUN /opt/conda/envs/alloagent_e1/bin/pip install --no-cache-dir \
        "chembl_webresource_client>=0.10" \
        "gget>=0.28" \
        "PyPDF2>=3.0,<4.0" \
        "beautifulsoup4>=4.12" \
        "pubchempy>=1.0,<2.0" \
        "gseapy>=1.1,<2.0"

# ---------------------------------------------------------------------------
# Baseline-health dependencies (STEP 5 import audit).
#
# scripts/upstream_import_audit.py imports every upstream Biomni tool
# module on the `baseline` branch in this image. A module-level import
# surfaces only the FIRST missing name in a chain, so
# scripts/external_dep_scan.py additionally parses each module's AST and
# checks every top-level third-party import individually.
#
# Added here (all pinned, all pip-installable, none touching the
# torch / numpy / pandas pins):
#   nibabel, SimpleITK    bioimaging
#   fair-esm (esm)        genomics
#   scanpy                the OLD repo's genomics
#   pybiomart             genomics (the next blocker after esm)
#   opencv-python-headless (cv2), scikit-image (skimage)
#                        bioengineering, biophysics, cell_biology,
#                        immunology, microbiology, pathology,
#                        pharmacology, physiology
#
# The remaining upstream-tool dependencies are installed in the NEXT
# layer (docs/dev_installs.txt). Nothing is deferred for dependency
# reasons any more.
#
# `pandas==3.0.6` is pinned explicitly: scanpy's resolver otherwise
# downgrades pandas to 2.3.x, which silently changes the dataframe
# semantics the other tools rely on. Verified: installing these leaves
# torch 2.4.1+cpu and numpy 2.3.5 untouched and keeps pandas at 3.0.6.
RUN /opt/conda/envs/alloagent_e1/bin/pip install --no-cache-dir \
        "nibabel>=5.2,<6.0" \
        "SimpleITK>=2.3,<3.0" \
        "fair-esm>=2.0.0,<3.0" \
        "scanpy>=1.10,<2.0" \
        "pybiomart>=0.2,<0.3" \
        "opencv-python-headless>=4.9,<5.0" \
        "scikit-image>=0.22,<0.26" \
        "pandas==3.0.6"

# ---------------------------------------------------------------------------
# Upstream-tool dependencies (docs/dev_installs.txt).
#
# Every third-party package the 31 upstream tool modules import, added
# in ONE layer. The versions below are the ones resolved and
# import-verified in the dev container on 2026-10-23/24 and recorded in
# docs/dev_installs.txt.
#
# The constraints file is load-bearing:
#   torch / torchvision  - the image pins torch 2.4.1+cpu; torchvision
#                           must match it or the compiled extensions
#                           disagree.
#   numpy / pandas       - the pinned versions the tools rely on.
#   setuptools<81        - setuptools 81 removed pkg_resources, which
#                           PyTDC imports.
#   the conda packages   - EVERY package the conda layer installed is
#                           pinned to its exact conda version. The build
#                           runs pip as root, so without these pins pip
#                           overwrites the conda build of a package in
#                           place.
#   setuptools<81        - listed as a REQUIREMENT, not only as a
#                           constraint: a constraint does not downgrade
#                           an already-installed package, and
#                           setuptools 81 removed pkg_resources, which
#                           PyTDC imports.
#
# PyTDC depends on `rdkit-pypi`, a separate PyPI project that installs
# into the SAME `rdkit` package directory and is compiled against NumPy
# 1.x. It therefore overwrites the conda rdkit build and `import rdkit`
# dies with "AttributeError: _ARRAY_API not found", taking Meeko (and
# so the B2 docking tool) with it. The layer restores the conda rdkit
# afterwards with `conda install --force-reinstall --no-deps`, and the
# verification step imports rdkit, meeko and tdc so this failure mode
# fails the BUILD instead of shipping.
# `transformers>=4.40,<5.0` and `bibtexparser<1.4` are requirements of
# this install, not constraints, so a heavier package cannot win them.
#
# NOT installed, with the evidence recorded in docs/dev_installs.txt:
#   FlowCytometryTools - newest release 0.5.1 uses
#       collections.MutableMapping and cannot import on Python 3.11.
#   harmony - no distribution provides the `harmony` module that
#       upstream genomics.py imports.
#   eval_single_anndata - no distribution provides that module.
# ---------------------------------------------------------------------------
RUN printf '%s\n' \
        'torch==2.4.1+cpu' \
        'torchvision==0.19.1+cpu' \
        'numpy==2.3.5' \
        'pandas==3.0.6' \
        'setuptools<81' \
        'scipy==1.17.1' \
        'rdkit==2024.9.6' \
        'prody==2.6.1' \
        'biotite==1.6.0' \
        'gemmi==0.7.5' \
        'biopython==1.88' \
        'networkx==3.6.1' \
        'pydantic==2.14.1' \
        'requests==2.34.2' \
        'urllib3==2.8.0' \
        'tiktoken==0.14.0' \
        'python-dotenv==1.2.4' \
        'langchain==0.3.30' \
        'langchain-core==0.3.86' \
        'langchain-openai==0.3.35' \
        'langchain-community==0.3.31' \
        'langchain-anthropic==0.3.22' \
        'langchain-google-genai==0.0.1' \
        'langgraph==0.3.18' \
        'meeko==0.8.0' \
        'vina==1.2.7' \
        'gseapy==1.3.1' \
        'chembl-webresource-client==0.10.9' \
        'pubchempy==1.0.5' \
        'gget==0.30.6' \
        'beautifulsoup4==4.15.0' \
        'PyPDF2==3.0.1' \
        > /tmp/alloagent_constraints.txt \
    && /opt/conda/envs/alloagent_e1/bin/pip install --no-cache-dir \
        --extra-index-url https://download.pytorch.org/whl/cpu \
        -c /tmp/alloagent_constraints.txt \
        "transformers>=4.40,<5.0" \
        "bibtexparser<1.4" \
        "setuptools<81" \
        googlesearch-python \
        scholarly \
        arxiv \
        pymed \
        ViennaRNA \
        python-louvain \
        nilearn \
        pyliftover \
        msprime \
        pykalman \
        trackpy \
        flowkit \
        python-libsbml \
        cobra \
        pybedtools \
        accelerate \
        cooler \
        PyTDC \
        DeepPurpose \
        cellpose \
        popv \
        scvi-tools \
        nnunet \
    && rm -f /tmp/alloagent_constraints.txt \
    && conda install --force-reinstall --no-deps -y -n alloagent_e1 \
        rdkit=2024.09.6 \
    && /opt/conda/envs/alloagent_e1/bin/python -c "\
import importlib.metadata as m; \
assert m.version('torch') == '2.4.1+cpu', m.version('torch'); \
assert m.version('numpy') == '2.3.5', m.version('numpy'); \
assert m.version('pandas') == '3.0.6', m.version('pandas'); \
assert m.version('transformers').startswith('4.'), m.version('transformers'); \
import scipy; assert scipy.__version__ == '1.17.1', scipy.__version__; \
import rdkit; assert rdkit.__version__.startswith('2024'), rdkit.__version__; \
from rdkit import Chem; \
from meeko import MoleculePreparation; \
import tdc; \
print('alloagent_e1 upstream deps OK: torch', m.version('torch'), \
'numpy', m.version('numpy'), 'pandas', m.version('pandas'), \
'transformers', m.version('transformers'), \
'rdkit', rdkit.__version__, 'scipy', scipy.__version__)"
# ----------------------------------------------------------------------------
FROM base-deps AS base-binaries

ARG FPOCKET_VERSION=4.2.3
ARG FPOCKET_TARBALL=fpocket-${FPOCKET_VERSION}.tar.gz
ARG FPOCKET_SHA256=62b3da6490eeab0db488f0182150d340de2be0be23f4fd1def9d5846ce724ede
ARG FPOCKET_URL=https://github.com/Discngine/fpocket/archive/refs/tags/${FPOCKET_VERSION}.tar.gz
RUN cd /tmp \
    && curl -fsSL "${FPOCKET_URL}" -o "${FPOCKET_TARBALL}" \
    && echo "${FPOCKET_SHA256}  ${FPOCKET_TARBALL}" | sha256sum -c - \
    && tar xzf "${FPOCKET_TARBALL}" \
    && cd "fpocket-${FPOCKET_VERSION}" \
    && make QCFLAGS="-O -g -pg -ansi -Isrc/qhull/src" -j"$(nproc)" \
    && cp bin/fpocket bin/tpocket bin/mdpocket /usr/local/bin/ \
    && fpocket --version \
    && cd /tmp && rm -rf "${FPOCKET_TARBALL}" "fpocket-${FPOCKET_VERSION}"

ARG P2RANK_VERSION=2.5.1
ARG P2RANK_TARBALL=p2rank_${P2RANK_VERSION}.tar.gz
ARG P2RANK_SHA256=d243f2d9036ac053fefb9407b5fe1c85f4fe077c519fd975ac585e995feab274
ARG P2RANK_URL=https://github.com/rdk/p2rank/releases/download/${P2RANK_VERSION}/p2rank_${P2RANK_VERSION}.tar.gz
RUN cd /tmp \
    && curl -fsSL "${P2RANK_URL}" -o "${P2RANK_TARBALL}" \
    && echo "${P2RANK_SHA256}  ${P2RANK_TARBALL}" | sha256sum -c - \
    && mkdir -p /opt/p2rank \
    && tar xzf "${P2RANK_TARBALL}" -C /opt/p2rank --strip-components=1 \
    && sed -e 's|^THIS_SCRIPT_DIR_REL_PATH=.*$|INSTALL_DIR=/opt/p2rank|' \
        -e '/^export INSTALL_DIR=.*$/d' \
        /opt/p2rank/prank > /usr/local/bin/prank \
    && chmod +x /usr/local/bin/prank \
    && ln -sf /opt/p2rank/bin/p2rank.jar /usr/local/bin/p2rank.jar \
    && rm -f /tmp/${P2RANK_TARBALL}

# ----------------------------------------------------------------------------
# 4. base-pocketminer : pocketminer_env + repo clones + legacy-Adam patch
# ----------------------------------------------------------------------------
FROM base-binaries AS base-pocketminer

ARG POCKETMINER_COMMIT=187062df3c94127e991669768009141a08fd5d8b
ARG AE_POCKETMINER_COMMIT=3328ca0376d3e4959545bac35e036435d582ff2e

# Create the pocketminer_env conda env (tf 2.15, np 1.26.4, mdtraj 1.11.1).
# Includes tqdm, pyyaml, biopython (deps of PocketMiner and AE-PocketMiner)
# so that nothing needs to be pip-installed at test time.
RUN mamba create -n pocketminer_env -c conda-forge -y \
        python=3.11 \
        "tensorflow=2.15.0" \
        "numpy=1.26.4" \
        "mdtraj=1.11.1" \
        scipy \
        requests \
        tqdm \
        pyyaml \
        biopython && \
    /opt/conda/envs/pocketminer_env/bin/pip install --no-cache-dir h5py

# Clone PocketMiner (Mickdub/gvp, branch pocket_pred) at pinned commit.
# Full clone (no --depth 1) so the pinned commit is fetchable.
RUN git clone https://github.com/Mickdub/gvp.git /opt/pocketminer && \
    cd /opt/pocketminer && \
    git checkout pocket_pred && \
    git checkout ${POCKETMINER_COMMIT} && \
    test -f LICENSE && \
    head -1 LICENSE | grep -qi MIT && \
    echo "PocketMiner MIT license verified at $(git rev-parse HEAD)"

# Clone AE-PocketMiner (bowman-lab/ae-pocketminer) at pinned commit.
RUN git clone https://github.com/bowman-lab/ae-pocketminer.git /opt/ae-pocketminer && \
    cd /opt/ae-pocketminer && \
    git checkout ${AE_POCKETMINER_COMMIT} && \
    echo "AE-PocketMiner cloned at $(git rev-parse HEAD)"

# Build-time patch: rewrite `tf.keras.optimizers.Adam` to
# `tf.keras.optimizers.legacy.Adam` in every .py file under the two
# cloned repos. This is the pattern the code actually uses (verified
# by `grep -rn 'tf.keras.optimizers.Adam' /opt/{pocketminer,
# ae-pocketminer}/src/`). The previous Dockerfile tried to match
# `tensorflow.keras.optimizers.Adam` (no leading `tf.`) which did
# not match; the legacy-Adam shim had to be re-applied at test time
# inside the running container, which doesn't persist across runs.
#
# The patch is applied at BUILD TIME (not runtime) via a checked-in
# Python script. The script is idempotent and rewrites only the
# specific token, leaving everything else untouched.
COPY docker/patches/apply_legacy_adam.py /tmp/apply_legacy_adam.py
RUN /opt/conda/envs/pocketminer_env/bin/python /tmp/apply_legacy_adam.py \
        /opt/pocketminer /opt/ae-pocketminer

# PocketMiner + AE-PocketMiner weights: the pre-trained checkpoints
# are committed under the cloned repos at models/pocketminer.{data,index}
# and models/aepocketminer.{data,index}. We do NOT re-download them;
# the SHA256 of the checkpoint files is recorded into the build log
# so the image is reproducible.
RUN cd /opt/pocketminer/models && \
    sha256sum pocketminer.data-00000-of-00001 pocketminer.index \
        | tee /opt/pocketminer_weights.sha256 && \
    cd /opt/ae-pocketminer/models && \
    sha256sum aepocketminer.data-00000-of-00001 aepocketminer.index \
        | tee /opt/ae-pocketminer_weights.sha256

# Mark the cloned repos as safe.directory so the runtime user can
# `git rev-parse HEAD` in them (otherwise git refuses with
# "dubious ownership" because the repos are owned by root but
# `appuser` is non-root). The flag is global but the two paths are
# the only git repos under /opt.
RUN git config --global --add safe.directory /opt/pocketminer && \
    git config --global --add safe.directory /opt/ae-pocketminer

# Verify both envs are importable as root (final USER appuser below).
RUN /opt/conda/envs/pocketminer_env/bin/python -c \
        "import tensorflow as tf; import mdtraj; import numpy; \
         import tqdm; import yaml; import Bio; \
         assert tf.__version__ == '2.15.0', f'tf={tf.__version__}'; \
         assert numpy.__version__ == '1.26.4', f'numpy={numpy.__version__}'; \
         assert mdtraj.__version__ == '1.11.1', f'mdtraj={mdtraj.__version__}'; \
         print('pocketminer_env OK:', tf.__version__, numpy.__version__, mdtraj.__version__)" && \
    /opt/conda/envs/pocketminer_env/bin/python -c "import sys; sys.path.insert(0, '/opt/pocketminer/src'); from models import MQAModel; print('PocketMiner MQAModel import OK')" && \
    /opt/conda/envs/pocketminer_env/bin/python -c "import sys; sys.path.insert(0, '/opt/ae-pocketminer/src'); from models import MQAModel; print('AE-PocketMiner MQAModel import OK')"

# Verify alloagent_e1 deps the runtime user actually needs.
RUN /opt/conda/envs/alloagent_e1/bin/python -c \
        "import vina, meeko, rdkit, gemmi, torch; \
         from Bio import SeqIO; \
         from meeko import MoleculePreparation, PDBQTMolecule, RDKitMolCreate, PDBQTReceptor; \
         print('alloagent_e1: vina=', vina.__version__ if hasattr(vina,'__version__') else '?', \
               'meeko=', meeko.__version__ if hasattr(meeko,'__version__') else '?', \
               'rdkit=', rdkit.__version__, \
               'gemmi=', gemmi.__version__ if hasattr(gemmi,'__version__') else '?')"

# ----------------------------------------------------------------------------
# 5. base-appuser : create the runtime user (BEFORE COPY --chown) and the
#    /workspace directory. /opt stays owned by root (clones are
#    read-only at runtime). Smoke-test all imports.
# ----------------------------------------------------------------------------
FROM base-pocketminer AS base-appuser

# Create the runtime user BEFORE the COPY --chown references it. The
# `--no-log-init` flag avoids the useradd mail-spool creation that has
# been observed to hang on some Windows-hosted Docker setups. The
# `-d` makes the home dir explicit (no /etc/skel traversal).
RUN groupadd --system appuser \
    && useradd --system --create-home --home-dir /home/appuser \
        --shell /bin/bash --gid appuser --no-log-init appuser

WORKDIR /workspace
RUN mkdir -p /workspace && chown -R appuser:appuser /workspace /home/appuser

ENV PATH=/opt/conda/envs/alloagent_e1/bin:$PATH
ENV CONDA_DEFAULT_ENV=alloagent_e1

# Smoke-test the alloagent_e1 imports as the non-root user.
USER appuser
RUN /opt/conda/envs/alloagent_e1/bin/python -c \
        "import vina, meeko, rdkit, gemmi; \
         from meeko import MoleculePreparation, PDBQTMolecule, RDKitMolCreate, PDBQTReceptor; \
         from rdkit import Chem; from rdkit.Chem import AllChem, rdMolAlign; \
         print('alloagent_e1 imports OK as appuser')" && \
    /opt/conda/envs/alloagent_e1/bin/python -m pytest --version

USER root

# ----------------------------------------------------------------------------
# 6. dev : bind-mount-friendly target for development.
#    Source edits to /workspace need no rebuild of layers 1-5; only
#    this layer's `pip install -e` re-runs when the pyproject.toml
#    changes. Recommended for day-to-day work.
# ----------------------------------------------------------------------------
FROM base-appuser AS dev

# The actual repo files are bind-mounted at /workspace in development:
#   docker run --rm -it -v "$(pwd):/workspace" alloagent-dev:latest bash
# For the dev image we still install the package metadata so that
# `import biomni` works even without the bind mount.
COPY --chown=appuser:appuser pyproject.toml README.md MANIFEST.in PINNED_UPSTREAM /workspace/
COPY --chown=appuser:appuser biomni /workspace/biomni
COPY --chown=appuser:appuser alloagent /workspace/alloagent
RUN /opt/conda/envs/alloagent_e1/bin/pip install --no-cache-dir -e /workspace

USER appuser
WORKDIR /workspace

CMD ["/opt/conda/envs/alloagent_e1/bin/python", "-m", "pytest", "tests/", "--no-header", "--no-summary", "-q"]

# ----------------------------------------------------------------------------
# 7. eval : same as dev but the WHOLE repo is COPY'd in. Use this for
#    the final evaluation image; no bind mount; image ID recorded in
#    docs/0a_installed_versions.md.
# ----------------------------------------------------------------------------
FROM base-appuser AS eval

COPY --chown=appuser:appuser . /workspace
RUN /opt/conda/envs/alloagent_e1/bin/pip install --no-cache-dir -e /workspace

USER appuser
WORKDIR /workspace

CMD ["/opt/conda/envs/alloagent_e1/bin/python", "-m", "pytest", "tests/", "--no-header", "--no-summary", "-q"]
