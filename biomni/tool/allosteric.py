from biomni.tool.database import query_uniprot, query_pdb
from biomni.tool.biolip import parse_biolip_interactions, biolip_ligands
from biomni.tool.asd import parse_asd_xf, load_asd_ap, load_asd_dr


import pandas as pd
import json
import logging
from typing import Dict, Any
import os
from typing import Dict, List, Tuple, Any, Optional
import re
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()



# VERIFIED
def biolip_ligands(pdb_id, chain=None):
    """
    Get ligand IDs for a given PDB ID and optionally chain.
    """
    interactions = parse_biolip_interactions(pdb_id, chain)
    print(f"Interactions: {interactions}")
    return interactions['Ligand'].unique().tolist()


# STILL IN TEST PHASES
def cross_reference_ligands(pdb_id: str, uniprot_id: str, ligands: list):
    """
    Cross-reference ligands against PDB, BioLiP, and ASD using PDB ID.
    """
    pdb_id = pdb_id.lower()
    results = {
        "pdb_id": pdb_id,
        "uniprot_id": uniprot_id,
        "cross_references": []
    }
    try:
        # ASD data - using Uniprot ID
        # PDB TO UNIPROT FUNCTION
        asd_experimental = parse_asd_xf(target_proteins=[uniprot_id])
        asd_predicted_sites = load_asd_ap(target_proteins=[uniprot_id])
        #asd_all_modulators = load_asd_dr()

        print(f"ASD_EXPERIMENTAL: {asd_experimental}")
        print(f"ASD PREDICTED: {asd_predicted_sites}")
        #print(f"MODULATORS: {asd_all_modulators}")

        for ligand in ligands:

            cross_ref = {
                "ligand_code": ligand,
                "cross_refs": {},
                "provenance": []
            }

            # Add PDB confirmation
            pdb_info = None
            #pdb_info = query_pdb(pdb_id)
            if pdb_info:
                cross_ref["cross_refs"]["pdb"] = pdb_info
                cross_ref["provenance"].append("PDB")

            # Add ASD allosteric annotation
            asd_match = None
            '''
            for modulator_id, modulator_data in asd_all_modulators.items():
                if (ligand_code in modulator_data.get('name', '') or
                    ligand_code in modulator_data.get('cas_id', '') or
                    ligand_code in modulator_data.get('drugbank_id', '')):
                    asd_match = modulator_data
                    break
            '''
            if asd_match or asd_experimental.get(pdb_id) or asd_predicted_sites.get(pdb_id):
                cross_ref["cross_refs"]["asd"] = {
                    "modulator_match": asd_match,
                    "experimental_sites": asd_experimental.get(pdb_id, {}),
                    "predicted_sites": asd_predicted_sites.get(pdb_id, [])
                }
                cross_ref["provenance"].append("ASD")

            results["cross_references"].append(cross_ref)

    except Exception as e:
        results["error"] = str(e)

    return results


def test_cross_reference_ligands(pdb_id, uniprot_id):
    """
    Test for cross_reference_ligands function using PDB ID.
    """
    print(f"Testing cross-reference for PDB {pdb_id}...")
    
    # Get ligands from PDB
    ligands = biolip_ligands(pdb_id)
    print(f"Found {len(ligands)} ligands")
    
    # Cross-reference ligands
    results = cross_reference_ligands(pdb_id, uniprot_id, ligands)
    print(f"RESULTS: {results}")
    
    # Print results
    print(f"Cross-references: {len(results.get('cross_references', []))}")
    for i, cross_ref in enumerate(results.get('cross_references', [])):
        asd_found = 'asd' in cross_ref['cross_refs']
        print(f"  {cross_ref['ligand_code']}: ASD match = {asd_found}")
        
    return results


test_cross_reference_ligands("1I09", "P49841")


# STILL IN TEST PHASES
def covalent_allosteric_examples(pdb_id):
    """
    Get covalent probe examples for allosteric pocket identification.
    """
    pdb_id = pdb_id.lower()
    interactions = parse_biolip_interactions(pdb_id)
    ligands = biolip_ligands(pdb_id)
    
    return {
        'pdb_id': pdb_id,
        'ligands': ligands,
        'interactions': interactions.to_dict('records') if not interactions.empty else [],
        'protein_chains': list(interactions['Chain'].unique()) if not interactions.empty else [],
        'total_interactions': len(interactions)
    }



'''---------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------'''

from typing import Dict, List, Tuple, Any, Optional
import re
import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationResult:
    """Standardized result format for each validation check"""
    check_name: str
    score: float
    confidence: float
    evidence: Dict[str, Any]
    explanation: str

def validate_allosteric_site(
    predicted_site: List[str],
    protein_id: str,
    pdb_id: str
) -> str:
    """
    Main function: 3-check allosteric validation system
    
    Args:
        predicted_site: List of residues like ["F185", "C166", "A167"]
        protein_id: UniProt ID for ASD queries
        pdb_id: PDB ID for BioLiP queries
        
    Returns:
        JSON string with complete validation results and detailed evidence
    """
    
    validation_results = []
    
    # Check 1: ASD Direct Match
    asd_result = check_asd_direct_match(predicted_site, protein_id, load_asd_ap)
    validation_results.append(asd_result)
    
    # Check 2: BioLiP Catalytic Conflict  
    catalytic_result = check_biolip_catalytic_conflict(predicted_site, pdb_id, parse_biolip_interactions)
    validation_results.append(catalytic_result)
    
    # Check 3: BioLiP Ligand Context
    ligand_result = check_biolip_ligand_context(predicted_site, pdb_id, parse_biolip_interactions, biolip_ligands)
    validation_results.append(ligand_result)
    
    # Combine results into final score
    final_result = combine_validation_results(validation_results)
    
    # Generate comprehensive evidence report
    evidence_report = generate_evidence_report(
        predicted_site, protein_id, pdb_id, 
        validation_results, final_result
    )
    
    return evidence_report

def check_asd_direct_match(predicted_site: List[str], protein_id: str, load_asd_ap) -> ValidationResult:
    """Check if predicted site matches known allosteric sites in ASD"""
    
    try:
        asd_data = load_asd_ap([protein_id])
        
        # Handle case where ASD returns error string
        if isinstance(asd_data, str):
            return ValidationResult(
                check_name="asd_direct_match",
                score=0,
                confidence=0,
                evidence={'error': asd_data},
                explanation=f"ASD error: {asd_data}"
            )
        
        # Handle empty dictionary or no data for this protein
        if not asd_data or protein_id not in asd_data:
            return ValidationResult(
                check_name="asd_direct_match",
                score=0,
                confidence=0.3,
                evidence={'total_asd_sites': 0, 'protein_found': False},
                explanation="No ASD data found for this protein"
            )
        
        known_sites = extract_asd_allosteric_sites(asd_data, protein_id)
        exact_matches, partial_matches = calculate_site_matches(predicted_site, known_sites)
        
        if exact_matches:
            score = 40
            explanation = f"Exact match with {len(exact_matches)} known allosteric sites"
        elif partial_matches:
            best_overlap = max(match['overlap_pct'] for match in partial_matches)
            if best_overlap >= 0.67:
                score = 25
            elif best_overlap >= 0.5:
                score = 15
            else:
                score = 5
            explanation = f"Partial match with best overlap: {best_overlap:.1%}"
        else:
            score = 0
            explanation = "No matches found in ASD allosteric sites"
        
        return ValidationResult(
            check_name="asd_direct_match",
            score=score,
            confidence=0.9 if exact_matches else 0.6 if partial_matches else 0.3,
            evidence={
                'exact_matches': exact_matches,
                'partial_matches': partial_matches,
                'total_asd_sites': len(known_sites),
                'protein_found': True
            },
            explanation=explanation
        )
        
    except Exception as e:
        return ValidationResult(
            check_name="asd_direct_match",
            score=0,
            confidence=0,
            evidence={'error': str(e)},
            explanation=f"Error accessing ASD: {str(e)}"
        )

def check_biolip_catalytic_conflict(predicted_site: List[str], pdb_id: str, parse_biolip_interactions) -> ValidationResult:
    """Check if predicted site conflicts with known catalytic sites"""
    
    try:
        biolip_df = parse_biolip_interactions(pdb_id)
        
        # Handle empty DataFrame
        if biolip_df.empty:
            return ValidationResult(
                check_name="biolip_catalytic_conflict",
                score=12,
                confidence=0.3,
                evidence={'pdb_found': False, 'total_interactions': 0},
                explanation="No BioLiP data found for this PDB"
            )
        
        catalytic_sites = extract_catalytic_sites_from_df(biolip_df)
        overlap_info = calculate_catalytic_overlap(predicted_site, catalytic_sites)
        
        overlap_pct = overlap_info['overlap_percentage']
        
        if overlap_pct == 0:
            score = 25
            explanation = "No overlap with catalytic sites"
        elif overlap_pct <= 15:
            score = 15
            explanation = f"Low catalytic overlap: {overlap_pct:.1f}%"
        elif overlap_pct <= 30:
            score = 5
            explanation = f"Moderate catalytic overlap: {overlap_pct:.1f}%"
        else:
            score = -20
            explanation = f"High catalytic overlap: {overlap_pct:.1f}%"
        
        # Add DataFrame info to evidence
        overlap_info['pdb_found'] = True
        overlap_info['total_interactions'] = len(biolip_df)
        
        return ValidationResult(
            check_name="biolip_catalytic_conflict",
            score=score,
            confidence=0.8,
            evidence=overlap_info,
            explanation=explanation
        )
        
    except Exception as e:
        return ValidationResult(
            check_name="biolip_catalytic_conflict",
            score=0,
            confidence=0,
            evidence={'error': str(e)},
            explanation=f"Error accessing BioLiP: {str(e)}"
        )

def check_biolip_ligand_context(predicted_site: List[str], pdb_id: str, parse_biolip_interactions, biolip_ligands) -> ValidationResult:
    """Check what types of ligands bind near the predicted site"""
    
    try:
        ligands = biolip_ligands(pdb_id)
        biolip_df = parse_biolip_interactions(pdb_id)
        
        # Handle no ligands or empty DataFrame
        if not ligands or biolip_df.empty:
            return ValidationResult(
                check_name="biolip_ligand_context",
                score=5,
                confidence=0.2,
                evidence={'ligands_found': False, 'total_ligands': 0, 'total_interactions': len(biolip_df) if not biolip_df.empty else 0},
                explanation="No ligands found for context analysis"
            )
        
        context_analysis = analyze_ligand_context_from_df(predicted_site, biolip_df, ligands)
        score_result = score_ligand_context(context_analysis)
        
        return ValidationResult(
            check_name="biolip_ligand_context",
            score=score_result['score'],
            confidence=0.6,
            evidence=context_analysis,
            explanation=score_result['explanation']
        )
        
    except Exception as e:
        return ValidationResult(
            check_name="biolip_ligand_context",
            score=0,
            confidence=0,
            evidence={'error': str(e)},
            explanation=f"Error analyzing ligand context: {str(e)}"
        )

def extract_asd_allosteric_sites(asd_data: Dict[str, List[Dict]], protein_id: str) -> List[List[str]]:
    """Extract allosteric site residue lists from ASD data"""
    sites = []
    
    if protein_id not in asd_data:
        return sites
    
    for site_info in asd_data[protein_id]:
        # Use the structured residue data from ASD
        residues = []
        
        # Try parsed residues first (most reliable)
        if 'residues_parsed' in site_info and site_info['residues_parsed']:
            for res_info in site_info['residues_parsed']:
                # Format: name_short + position (e.g., "F382")
                residue_id = f"{res_info['name_short']}{res_info['position']}"
                residues.append(residue_id)
        # Fallback to formatted residue string
        elif 'residues' in site_info and site_info['residues']:
            # Parse format like "F382:A; C464:A; A452:A" 
            residue_parts = site_info['residues'].split(';')
            for part in residue_parts:
                part = part.strip()
                if ':' in part:
                    residue_id = part.split(':')[0].strip()  # Take part before chain
                    if residue_id:
                        residues.append(residue_id)
        
        if residues:
            sites.append(residues)
    
    return sites

def extract_catalytic_sites_from_df(biolip_df) -> List[str]:
    """Extract catalytic site residues from BioLiP DataFrame"""
    catalytic_residues = []
    
    # Check if DataFrame has the expected columns
    if 'Catalytic_Site_Residues_PDB' in biolip_df.columns:
        for _, row in biolip_df.iterrows():
            cat_sites = row['Catalytic_Site_Residues_PDB']
            if pd.notna(cat_sites):
                # Split by spaces and add to list
                residues = str(cat_sites).split()
                catalytic_residues.extend(residues)
    
    # Remove duplicates and return
    return list(set(catalytic_residues))

def analyze_ligand_context_from_df(predicted_site: List[str], biolip_df, ligands: List[str]) -> Dict[str, Any]:
    """Analyze what types of ligands bind near the predicted site using DataFrame"""
    nearby_ligands = []
    ligand_categories = {
        'metal_ions': [],
        'cofactors': [],
        'substrates': [],
        'inhibitors': [],
        'nucleotides': [],
        'unknown': []
    }
    
    predicted_set = set(predicted_site)
    
    # Iterate through DataFrame rows
    for _, row in biolip_df.iterrows():
        # Get binding residues - check different possible column names
        binding_residues_str = ''
        for col in ['Binding_Site_Residues_PDB', 'residues', 'Residues']:
            if col in row and pd.notna(row[col]):
                binding_residues_str = str(row[col])
                break
        
        if binding_residues_str:
            binding_residues = set(binding_residues_str.split())
            
            # Check if this binding site overlaps with predicted site
            if binding_residues.intersection(predicted_set):
                # Get ligand ID
                ligand_id = ''
                for col in ['Ligand', 'ligand_id', 'Ligand_ID']:
                    if col in row and pd.notna(row[col]):
                        ligand_id = str(row[col])
                        break
                
                if ligand_id:
                    ligand_type = classify_ligand_type(ligand_id)
                    
                    nearby_ligands.append({
                        'ligand_id': ligand_id,
                        'ligand_type': ligand_type,
                        'binding_residues': list(binding_residues),
                        'overlap_with_predicted': list(binding_residues.intersection(predicted_set))
                    })
                    
                    ligand_categories[ligand_type].append(ligand_id)
    
    return {
        'nearby_ligands': nearby_ligands,
        'ligand_categories': ligand_categories,
        'total_nearby_ligands': len(nearby_ligands),
        'all_ligands_in_structure': ligands,
        'ligands_found': len(ligands) > 0,
        'total_ligands': len(ligands)
    }

def calculate_site_matches(predicted_site: List[str], known_sites: List[List[str]]) -> Tuple[List[Dict], List[Dict]]:
    """Calculate exact and partial matches between predicted and known sites"""
    exact_matches = []
    partial_matches = []
    
    predicted_set = set(predicted_site)
    
    for i, known_site in enumerate(known_sites):
        known_set = set(known_site)
        overlap = predicted_set.intersection(known_set)
        overlap_pct = len(overlap) / len(predicted_set) if predicted_set else 0
        
        match_info = {
            'known_site_index': i,
            'known_site': known_site,
            'overlapping_residues': list(overlap),
            'overlap_count': len(overlap),
            'overlap_pct': overlap_pct
        }
        
        if overlap_pct == 1.0:
            exact_matches.append(match_info)
        elif overlap_pct > 0:
            partial_matches.append(match_info)
    
    return exact_matches, partial_matches

def calculate_catalytic_overlap(predicted_site: List[str], catalytic_sites: List[str]) -> Dict[str, Any]:
    """Calculate overlap between predicted site and catalytic sites"""
    predicted_set = set(predicted_site)
    catalytic_set = set(catalytic_sites)
    
    overlap = predicted_set.intersection(catalytic_set)
    overlap_count = len(overlap)
    overlap_pct = (overlap_count / len(predicted_set)) * 100 if predicted_set else 0
    
    return {
        'overlapping_residues': list(overlap),
        'overlap_count': overlap_count,
        'overlap_percentage': overlap_pct,
        'total_predicted': len(predicted_site),
        'total_catalytic': len(catalytic_sites),
        'all_catalytic_sites': catalytic_sites,
        'predicted_site': predicted_site
    }
    """Classify ligand type based on common ligand IDs"""
    ligand_id = ligand_id.upper()
    
    metal_ions = ['ZN', 'MG', 'CA', 'FE', 'MN', 'CU', 'CO', 'NI', 'K', 'NA']
    if ligand_id in metal_ions:
        return 'metal_ions'
    
    cofactors = ['ATP', 'ADP', 'AMP', 'GTP', 'GDP', 'GMP', 'NAD', 'NADH', 'FAD', 'FMN', 'COA', 'HEM']
    if ligand_id in cofactors:
        return 'cofactors'
    
    nucleotides = ['A', 'T', 'G', 'C', 'U', 'DA', 'DT', 'DG', 'DC']
    if ligand_id in nucleotides:
        return 'nucleotides'
    
    inhibitors = ['STI', 'IMI', 'CHE', 'PPI']
    if ligand_id in inhibitors:
        return 'inhibitors'
    
    if len(ligand_id) <= 2:
        return 'metal_ions'
    elif 'ATP' in ligand_id or 'ADP' in ligand_id:
        return 'cofactors'
    else:
        return 'unknown'

def score_ligand_context(context_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Score the ligand context for allosteric potential"""
    categories = context_analysis['ligand_categories']
    score = 0
    explanations = []
    
    if categories['metal_ions']:
        score += 10
        explanations.append(f"Metal ions: {categories['metal_ions']}")
    
    if categories['nucleotides']:
        score += 15
        explanations.append(f"Nucleotides: {categories['nucleotides']}")
    
    if categories['cofactors'] and len(categories['cofactors']) <= 2:
        score += 5
        explanations.append(f"Cofactors: {categories['cofactors']}")
    
    if categories['inhibitors']:
        score += 20
        explanations.append(f"Inhibitors: {categories['inhibitors']}")
    
    if context_analysis['total_nearby_ligands'] == 0:
        score += 5
        explanations.append("Isolated from binding sites")
    
    explanation = "; ".join(explanations) if explanations else "No significant ligand context"
    
    return {
        'score': min(score, 20),
        'explanation': explanation
    }

def combine_validation_results(validation_results: List[ValidationResult]) -> Dict[str, Any]:
    """Combine results from all validation checks into final score"""
    if not validation_results:
        return {
            'score': 0,
            'confidence_category': 'NO_DATA',
            'explanation': 'No validation data available',
            'recommendation': 'Cannot validate - insufficient data'
        }
    
    total_score = sum(result.score for result in validation_results)
    normalized_score = max(0, min(100, (total_score + 30) / 85 * 100))
    
    confidence_category = categorize_confidence(normalized_score)
    explanations = [f"{result.check_name}: {result.explanation}" for result in validation_results]
    full_explanation = " | ".join(explanations)
    recommendation = generate_recommendation(normalized_score)
    
    return {
        'score': round(normalized_score, 1),
        'confidence_category': confidence_category,
        'explanation': full_explanation,
        'recommendation': recommendation
    }

def categorize_confidence(score: float) -> str:
    """Categorize confidence level based on score"""
    if score >= 80:
        return 'VERY_HIGH'
    elif score >= 65:
        return 'HIGH'
    elif score >= 50:
        return 'MEDIUM'
    elif score >= 35:
        return 'LOW'
    else:
        return 'VERY_LOW'

def generate_recommendation(score: float) -> str:
    """Generate actionable recommendation based on results"""
    if score >= 80:
        return "Strong evidence for allosteric site - high confidence prediction"
    elif score >= 65:
        return "Good evidence for allosteric site - proceed with experimental validation"
    elif score >= 50:
        return "Moderate evidence - additional computational analysis recommended"
    elif score >= 35:
        return "Weak evidence - consider alternative sites or gather more data"
    else:
        return "Insufficient evidence for allosteric site - likely false positive"

def generate_evidence_report(
    predicted_site: List[str],
    protein_id: str, 
    pdb_id: str,
    validation_results: List[ValidationResult],
    final_result: Dict[str, Any]
) -> str:
    """Generate comprehensive JSON evidence report"""
    
    evidence_breakdown = []
    total_raw_score = sum(result.score for result in validation_results)
    
    for result in validation_results:
        evidence_item = {
            "check_type": result.check_name,
            "points_contributed": result.score,
            "confidence_level": result.confidence,
            "finding": result.explanation,
            "detailed_evidence": format_detailed_evidence(result.check_name, result.evidence)
        }
        evidence_breakdown.append(evidence_item)
    
    report = {
        "validation_summary": {
            "predicted_allosteric_site": predicted_site,
            "protein_identifiers": {
                "uniprot_id": protein_id,
                "pdb_id": pdb_id
            },
            "final_confidence_score": final_result['score'],
            "confidence_category": final_result['confidence_category'],
            "is_likely_allosteric": final_result['score'] >= 50,
            "recommendation": final_result['recommendation']
        },
        
        "evidence_analysis": {
            "total_raw_points": total_raw_score,
            "normalized_score": final_result['score'],
            "evidence_breakdown": evidence_breakdown
        },
        
        "calculation_details": {
            "raw_score_total": total_raw_score,
            "normalization_applied": f"({total_raw_score} + 30) / 85 * 100 = {final_result['score']}%",
            "maximum_possible_score": "85 points (40 ASD + 25 catalytic + 20 ligand)"
        },
        
        "metadata": {
            "analysis_timestamp": datetime.now().isoformat(),
            "validation_version": "3-check-system-v1.0"
        }
    }
    
    return json.dumps(report, indent=2)

def format_detailed_evidence(check_name: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Format evidence with complete specifics"""
    
    if 'error' in evidence:
        return {"status": "error", "message": evidence['error']}
    
    if check_name == "asd_direct_match":
        formatted = {
            "total_known_allosteric_sites": evidence.get('total_asd_sites', 0),
            "protein_found_in_asd": evidence.get('protein_found', False)
        }
        
        if evidence.get('exact_matches'):
            formatted["exact_matches"] = []
            for match in evidence['exact_matches']:
                formatted["exact_matches"].append({
                    "known_allosteric_site": match['known_site'],
                    "overlapping_residues": match['overlapping_residues'],
                    "overlap_percentage": f"{match['overlap_pct'] * 100:.1f}%"
                })
        
        if evidence.get('partial_matches'):
            formatted["partial_matches"] = []
            for match in evidence['partial_matches']:
                formatted["partial_matches"].append({
                    "known_allosteric_site": match['known_site'],
                    "overlapping_residues": match['overlapping_residues'],
                    "overlap_percentage": f"{match['overlap_pct'] * 100:.1f}%"
                })
                
        return formatted
    
    elif check_name == "biolip_catalytic_conflict":
        return {
            "predicted_site": evidence.get('predicted_site', []),
            "all_catalytic_residues_in_protein": evidence.get('all_catalytic_sites', []),
            "residues_overlapping_with_catalytic": evidence.get('overlapping_residues', []),
            "overlap_count": evidence.get('overlap_count', 0),
            "overlap_percentage": f"{evidence.get('overlap_percentage', 0):.1f}%",
            "total_predicted_residues": evidence.get('total_predicted', 0),
            "total_catalytic_residues": evidence.get('total_catalytic', 0)
        }
    
    elif check_name == "biolip_ligand_context":
        formatted = {
            "total_ligands_in_structure": len(evidence.get('all_ligands_in_structure', [])),
            "all_ligands_in_structure": evidence.get('all_ligands_in_structure', []),
            "ligands_near_predicted_site": evidence.get('total_nearby_ligands', 0)
        }
        
        if evidence.get('nearby_ligands'):
            formatted["specific_nearby_ligands"] = []
            for ligand in evidence['nearby_ligands']:
                formatted["specific_nearby_ligands"].append({
                    "ligand_id": ligand['ligand_id'],
                    "ligand_type": ligand['ligand_type'],
                    "binding_residues": ligand['binding_residues'],
                    "residues_overlapping_with_prediction": ligand['overlap_with_predicted']
                })
        
        formatted["ligand_type_breakdown"] = {}
        for category, ligands in evidence.get('ligand_categories', {}).items():
            if ligands:
                formatted["ligand_type_breakdown"][category] = {
                    "count": len(ligands),
                    "specific_ligands": ligands
                }
        
        return formatted
    
    return evidence

# Test Cases
def run_test_cases():
    """Run three test cases to demonstrate system"""
    
    test_cases = [
        {
            'name': 'Test Case 1',
            'predicted_site': ['F382', 'C464', 'A452'],
            'protein_id': 'P00519',
            'pdb_id': '2hyy'
        },
        {
            'name': 'Test Case 2',
            'predicted_site': ['F85', 'L88', 'H92'],
            'protein_id': 'P68871',
            'pdb_id': '1a3n'
        },
        {
            'name': 'Test Case 3',
            'predicted_site': ['Y103', 'W121', 'L182'],
            'protein_id': 'Q99720',
            'pdb_id': '5hzm'
        }
    ]
    
    results = []
    for test_case in test_cases:
        result_json = validate_allosteric_site(
            predicted_site=test_case['predicted_site'],
            protein_id=test_case['protein_id'],
            pdb_id=test_case['pdb_id']
        )
        
        results.append({
            'test_name': test_case['name'],
            'input': test_case,
            'output': result_json
        })
    
    return results

#print(run_test_cases())