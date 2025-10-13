#!/usr/bin/env python3
"""
Professor-style Gemini audit for Biomni benchmark.
- Default model: gemini-1.5-flash (lower quota usage)
- Appends review to an output file (default: /app/bench_report.txt)
"""

import os, sys, json, time, argparse
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

PROFESSOR_PROMPT = """You are the **leading allosteric scientist and AI agent auditor**, reviewing a Biomni JSON submission for allosteric site prediction.  
Your voice should be authoritative, technical, and constructive, as if you were a world expert in computational allostery evaluating a peer’s work.  
Avoid grades. Focus on scientific rigor, quantitative metrics, and methodological soundness.

### Structure of Review

**Overall Scientific Assessment:**  
One or two paragraphs summarizing the overall impression of the submission (conceptual sketch, partial analysis, or rigorous study).  
Comment on whether the JSON demonstrates sufficient rigor to qualify as a reliable allosteric pipeline output.

**Major Strengths:**  
- Highlight the strongest elements (e.g., correct identification of regulatory sites, choice of MD engine, plausible hypotheses).  

**Major Weaknesses:**  
- List the critical deficiencies (e.g., missing pocket druggability, lack of pathway centrality metrics, absence of disruption scoring, no docking/binding analysis).  

**Detailed Sectional Critique:**  
- **Metadata:** Evaluate clarity of assumptions, transparency, and scientific validity.  
- **Allosteric Sites:** Assess structural plausibility and emphasize missing quantitative descriptors (pocket volume, hydrophobicity, druggability).  
- **Communication Pathways:** Critique cutoff choices, absence of path centrality scores, and scientific interpretability.  
- **Simulation Design:** Judge adequacy of engine, length, and CVs. Suggest better CVs to capture allosteric communication.  
- **Mutation Impact:** Evaluate mutation choice, need for disruption scoring, and validation strategies.  
- **Modulator Ranking:** Criticize absence of docking/binding results; stress why binding modes and scores are essential.  
- **Hypotheses:** Assess mechanistic soundness, testability, and alignment with literature.  

**Recommendations for Next Steps:**  
A bullet list of computational experiments required (e.g., compute druggability with DoGSite, run network centrality, perform RMSF analysis, docking studies).  

**Closing Scientific Note:**  
Summarize whether the current submission meets standards for computational allostery.  
End with:  
`Recheck: Run: python benchmark_legacy.py /app/biomni_output.json`
"""

def audit(json_text: str, model_name: str, max_retries: int = 5, backoff: float = 8.0) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set in environment.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    prompt = PROFESSOR_PROMPT + "\n\n## Student submission:\n```json\n" + json_text + "\n```"

    for attempt in range(1, max_retries + 1):
        try:
            resp = model.generate_content(prompt)
            return (getattr(resp, "text", "") or "").strip()
        except Exception as e:
            msg = str(e)
            quota = ("429" in msg) or ("quota" in msg.lower())
            if not quota or attempt == max_retries:
                raise
            time.sleep(backoff)
            backoff *= 1.7

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path", help="Path to biomni_output.json")
    ap.add_argument("--model", default="gemini-2.0-flash-lite")
    ap.add_argument("--out", default="/app/bench_report.txt")
    args = ap.parse_args()

    if not os.path.exists(args.json_path):
        print(f"ERROR: file not found: {args.json_path}", file=sys.stderr)
        sys.exit(2)

    with open(args.json_path, "r", encoding="utf-8") as f:
        json_text = f.read()

    review = audit(json_text, args.model)

    # Print and append
    print("\n===== GEMINI PROFESSOR REVIEW =====\n")
    print(review)
    with open(args.out, "a", encoding="utf-8") as fo:
        fo.write("\n\n===== GEMINI PROFESSOR REVIEW =====\n\n")
        fo.write(review)
        fo.write("\n")

if __name__ == "__main__":
    main()
