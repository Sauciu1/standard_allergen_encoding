import json
import re
from pathlib import Path

# UK top 14 allergen keywords (very lightweight; safe because it only matches explicit text)
ALLERGEN_KEYWORDS = {
    "celery": [r"\bcelery\b"],
    "cereals_containing_gluten": [r"\bgluten\b", r"\bwheat\b", r"\bbarley\b", r"\brye\b", r"\boats\b"],
    "crustaceans": [r"\bcrustacean(s)?\b", r"\bprawn(s)?\b", r"\bshrimp\b", r"\bcrab\b", r"\blobster\b"],
    "eggs": [r"\begg(s)?\b"],
    "fish": [r"\bfish\b"],
    "lupin": [r"\blupin\b"],
    "milk": [r"\bmilk\b", r"\bdairy\b", r"\bcheese\b", r"\bbutter\b", r"\bcream\b", r"\byoghurt\b", r"\byogurt\b"],
    "molluscs": [r"\bmollusc(s)?\b", r"\bmussel(s)?\b", r"\boyster(s)?\b", r"\bsquid\b", r"\boctopus\b"],
    "mustard": [r"\bmustard\b"],
    "nuts": [r"\bnut(s)?\b", r"\balmond(s)?\b", r"\bhazelnut(s)?\b", r"\bwalnut(s)?\b", r"\bcashew(s)?\b", r"\bpecan(s)?\b"],
    "peanuts": [r"\bpeanut(s)?\b"],
    "sesame": [r"\bsesame\b"],
    "soybeans": [r"\bsoy\b", r"\bsoya\b"],
    "sulphur_dioxide_sulphites": [r"\bsulphite(s)?\b", r"\bsulfite(s)?\b", r"\bsulphur dioxide\b", r"\bsulfur dioxide\b"],
}

DIETARY_KEYWORDS = {
    "vegan": [r"\bvegan\b", r"\bvg\b"],
    "vegetarian": [r"\bvegetarian\b", r"\bveg\b", r"\bv\b"],
    "gluten-free": [r"\bgluten[- ]?free\b", r"\bgf\b"],
    "dairy-free": [r"\bdairy[- ]?free\b"],
    "nut-free": [r"\bnut[- ]?free\b"],
    "halal": [r"\bhalal\b"],
    "kosher": [r"\bkosher\b"],
}

def find_matches(text: str, patterns: list[str]) -> list[str]:
    hits = []
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            # evidence = matched text
            hits.append(m.group(0))
    return hits

def analyse_ocr_text(raw: str) -> dict:
    # very simple "itemisation": keep as one block for now + extract global info
    # (we can improve splitting after we see your OCR style)
    allergens = []
    for allergen, pats in ALLERGEN_KEYWORDS.items():
        ev = find_matches(raw, pats)
        if ev:
            allergens.append({"allergen": allergen, "evidence": ev[0]})

    dietary = []
    for tag, pats in DIETARY_KEYWORDS.items():
        ev = find_matches(raw, pats)
        if ev:
            dietary.append({"tag": tag, "evidence": ev[0]})

    return {
        "allergens_found": allergens,
        "dietary_found": dietary,
        "note": "These are extracted from OCR text only; if not stated, information is unknown."
    }

def main():
    out_dir = Path("outputs")
    txt_files = sorted(out_dir.glob("*.txt"))

    if not txt_files:
        raise SystemExit("No .txt files found in ./outputs. Run OCR first (run_ocr_folder.py).")

    results = []
    for f in txt_files:
        raw = f.read_text(encoding="utf-8", errors="ignore")
        results.append({
            "source_file": f.name,
            **analyse_ocr_text(raw)
        })

    (out_dir / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"✅ Wrote {len(results)} result(s) to outputs/results.json")

if __name__ == "__main__":
    main()
