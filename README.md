# Biolab: RSMDA Biomni Wrapper Development Environment

This repository provides a containerized development environment for extending and experimenting with the Biomni AI framework. It is tailored for AI research, prompt engineering, and collaborative contributions within the RSMDA research group.

---

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/Verkhivker-Research-Group/Biolab.git
cd Biolab
```

### Step 2: Build the Docker Image

```bash
docker compose build
```

### Step 3: Run the Development Container

```bash
docker compose up -d
docker exec -it biomni-dev bash
conda activate biomni_e1
```

This command launches a fully configured Conda environment (`biomni_e1`) inside the container.

---

## 🔧 Development Environment Features

* **Python 3.11 (via Miniconda)**
* **Conda environment:** `biomni_e1`
* **Pre-installed Libraries:**

  * AI & NLP: `langchain`, `openai`, `transformers`, `sentencepiece`
  * Visualization: `matplotlib`, `seaborn`, `networkx`
  * Scientific computing: `numpy`, `scipy`, `pandas`, `statsmodels`
  * Developer tools: `pytest`, `jupyter`, `gradio`, `dotenv`, etc.
* Biomni core modules and utilities preloaded

---

## 🛠️ Common Commands

### Stop the container

```bash
docker compose down
```

### View container logs

```bash
docker compose logs -f
```

### Rebuild from scratch

```bash
docker compose down --volumes
docker compose build --no-cache
```

---

## 🧪 Recommended Workflow

* Edit and experiment in the `/app` directory (mounted from host)
* Use `jupyter notebook` or `python` for live development
* Install additional dependencies into `biomni_e1` if needed

---

## 📁 Repository Structure

```
Biolab/
├── biomni/                 # Biomni toolchain modules
├── environment.yml         # Conda AI environment definition
├── Dockerfile              # Environment build instructions
├── docker-compose.yml      # Container orchestration
└── README.md               # Project documentation
```

---

## 🤝 Contributing

This repository is maintained by the RSMDA AI Development Team. If you encounter issues or want to contribute, please reach out to:

* Fares Alhezaimi (@faresalhezaimi)

---

