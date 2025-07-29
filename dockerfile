# Base image with Conda
FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Copy environment file early (for caching layers)
COPY environment.yml .

# Create conda environment from the file
RUN conda update -n base -c defaults conda -y && \
    conda env create -f environment.yml && \
    conda clean --all --yes

# Activate environment path
ENV PATH=/opt/conda/envs/biomni_e1/bin:$PATH  

# Copy all project files AFTER the env is installed
COPY . /app

# Ensure kernel is registered for Jupyter use
RUN conda run -n biomni_e1 python -m ipykernel install --user --name=biomni_e1

# Default shell command
CMD ["conda", "run", "-n", "biomni_e1", "bash"]
