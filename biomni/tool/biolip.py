import gzip
import pandas as pd
from Bio import SeqIO
from io import StringIO
import os
import pickle


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data/biomni_data")

BIOLIP_TXT_PATH = os.path.join(DATA_DIR, "biolip/biolip.pkl")
PROTEIN_FASTA_PATH = os.path.join(DATA_DIR, "biolip/protein.pkl")
DNA_FASTA_PATH = os.path.join(DATA_DIR, "biolip/dna.pkl")
RNA_FASTA_PATH = os.path.join(DATA_DIR, "biolip/rna.pkl")
PEPTIDE_FASTA_PATH = os.path.join(DATA_DIR, "biolip/peptide.pkl")



def parse_biolip_interactions(pdb_id=None, chain=None):
    with open(BIOLIP_TXT_PATH, "rb") as f:
        df = pickle.load(f)

    pdb_id = pdb_id.lower()
    
    if chain is None:
        return df[df["PDB"] == pdb_id]
    else:
        return df[df[df["PDB"] == pdb_id]["Chain"] == chain]
    
    return df


def biolip_dna(pdb_id, chain=None):
    with open(DNA_FASTA_PATH, "rb") as f:
        df = pickle.load(f)
    
    pdb_lower = pdb_id.lower()
    if chain is None:
        prefix = f"{pdb_lower}_dna_"
        return df[df["identifier"].str.startswith(prefix)].copy()
    else:
        if len(chain) != 1:
            raise ValueError("Incorrect chain. Must be single letter")
        identifier = f"{pdb_lower}_dna_{chain.upper()}"
        return df[df["identifier"] == identifier].copy()


def biolip_peptide(pdb_id, chain=None):
    if len(pdb_id) != 4 and len(pdb_id) != 12:
        raise ValueError("Incorrect pdb_id. Must be 4 character id, or 12 if integrated in new PDB system")
    
    with open(PEPTIDE_FASTA_PATH, "rb") as f:
        df = pickle.load(f)
    
    pdb_lower = pdb_id.lower()
    
    if chain is None:
        prefix = f"{pdb_lower}_peptide_"
        return df[df["identifier"].str.startswith(prefix)].copy()
    else:
        if len(chain) != 1:
            raise ValueError("Incorrect chain. Must be single letter")
        identifier = f"{pdb_lower}_peptide_{chain.upper()}"
        return df[df["identifier"] == identifier].copy()


def biolip_protein(pdb_id, chain=None):
    if len(pdb_id) != 4 and len(pdb_id) != 12:
        raise ValueError("Incorrect pdb_id. Must be 4 character id, or 12 if integrated in new PDB system")
    
    with open(PROTEIN_FASTA_PATH, "rb") as f:
        df = pickle.load(f)
    
    pdb_lower = pdb_id.lower()
    
    if chain is None:
        prefix = f"{pdb_lower}"
        return df[df["identifier"].str.startswith(prefix)].copy()
    else:
        if len(chain) != 1:
            raise ValueError("Incorrect chain. Must be single letter")
        identifier = f"{pdb_lower}{chain.upper()}"
        return df[df["identifier"] == identifier].copy()


def biolip_rna(pdb_id, chain=None):
    if len(pdb_id) != 4 and len(pdb_id) != 12:
        raise ValueError("Incorrect pdb_id. Must be 4 character id, or 12 if integrated in new PDB system")
    
    with open(RNA_FASTA_PATH, "rb") as f:
        df = pickle.load(f)
    
    pdb_lower = pdb_id.lower()
    
    if chain is None:
        prefix = f"{pdb_lower}_rna_"
        return df[df["identifier"].str.startswith(prefix)].copy()
    else:
        if len(chain) != 1 and len(chain) != 2:
            raise ValueError("Incorrect chain. Must be 1-2 letter(s)")
        identifier = f"{pdb_lower}_rna_{chain.upper()}"
        return df[df["identifier"] == identifier].copy()


def biolip_ligands(pdb_id, chain=None):
    """
    Get ligand IDs for a given PDB ID and optionally chain.
    """
    interactions = parse_biolip_interactions(pdb_id, chain)
    return interactions['Ligand'].unique().tolist()

'''
# Example usage (same as before)
interactions = parse_biolip_interactions(pdb_id='1GG1')
print(f"Interactions for 1GG1: {interactions}")

dna = biolip_dna("1a1k", "B")
dna_all_chains = biolip_dna("1a1k")
print(f"DNA for single chain: \n{dna}")
print(f"DNA for all chains: \n{dna_all_chains}")

peptide = biolip_peptide("4a1g", "G")
peptide_all_chains = biolip_peptide("4a1g")
print(f"Peptide for single chain: \n{peptide}")
print(f"Peptide for all chains: \n{peptide_all_chains}")

protein = biolip_protein("8q5w", "B")
protein_all_chains = biolip_protein("8q5w")
print(f"Protein for single chain: \n{protein}")
print(f"Protein for all chains: \n{protein_all_chains}")

rna = biolip_rna("8a3w", "S1")
rna_all_chains = biolip_rna("8a3w")
print(f"RNA for single chain: \n{rna}")
print(f"RNA for all chains: \n{rna_all_chains}")

'''

