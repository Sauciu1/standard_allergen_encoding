import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path to import AllergiesGetter
sys.path.insert(0, str(Path(__file__).parent / "src"))
from allergies_getter import AllergiesGetter


def normalise_words(csv: str) -> List[str]:
    return [w.strip().lower() for w in csv.split(",") if w.strip()]


def decode_allergen_phrases(phrases: List[str]) -> List[str]:
    """
    Decode allergen phrases into actual allergen names.

    Args:
        phrases: List of encoded allergen phrases/words

    Returns:
        List of decoded allergen names (lowercased for matching)
    """
    try:
        with AllergiesGetter() as getter:
            # Use words_to_allergies to decode the database words into allergen names
            allergens = getter.words_to_allergies(phrases)
            if allergens is None:
                print(f"Warning: Could not decode phrases: {phrases}")
                return []
            
            # Print the decoded allergens
            print(f"Decoded allergens: {allergens}")
            
            # Now we have the allergen names, we need to expand them to include
            # all their ingredients/related terms for matching in menu text
            all_blocked_terms = set()
            
            # For each decoded allergen, add the allergen name itself (lowercased)
            for allergen in allergens:
                allergen_lower = allergen.lower()
                all_blocked_terms.add(allergen_lower)
                
                # Also add common variations/ingredients
                # You might want to expand this based on your allergen definitions
                # allergen_mapping = {
                #     'peanuts': ['peanut', 'peanuts', 'groundnut'],
                #     'tree nuts': ['almond', 'cashew', 'walnut', 'pecan', 'pistachio', 'hazelnut', 'macadamia', 'pine nut'],
                #     'milk': ['milk', 'dairy', 'cream', 'cheese', 'butter', 'yogurt', 'lactose'],
                #     'eggs': ['egg', 'eggs', 'mayonnaise'],
                #     'fish': ['fish', 'salmon', 'tuna', 'cod', 'haddock', 'anchovy'],
                #     'shellfish': ['shellfish', 'shrimp', 'crab', 'lobster', 'prawn', 'crayfish'],
                #     'soy': ['soy', 'soya', 'tofu', 'edamame'],
                #     'wheat': ['wheat', 'flour', 'bread', 'pasta'],
                #     'sesame': ['sesame', 'tahini'],
                # }
                
                # Check if this allergen has a mapping
                # for key, terms in allergen_mapping.items():
                #     if key in allergen_lower:
                #         all_blocked_terms.update(terms)
            
            print(f"Expanded to blocked terms: {sorted(all_blocked_terms)}")
            return list(all_blocked_terms)
    except Exception as e:
        print(f"Error decoding allergen phrases: {e}")
        return []


def split_into_meals(ocr_text: str) -> List[str]:
    lines = [ln.strip() for ln in ocr_text.splitlines()]
    lines = [ln for ln in lines if ln]

    meals: List[str] = []
    for ln in lines:
        # Skip price-only lines
        if re.fullmatch(r"[£$€]?\s*\d+(\.\d{2})?\s*", ln):
            continue

        # Merge likely description lines into previous meal
        if meals and (ln.startswith(("-", "•")) or ln[:1].islower()):
            meals[-1] = f"{meals[-1]} {ln.lstrip('-• ').strip()}"
        else:
            meals.append(ln)

    # Remove exact duplicates
    cleaned = []
    seen = set()
    for m in meals:
        key = m.lower()
        if key not in seen:
            seen.add(key)
            cleaned.append(m)

    return cleaned


def analyse_meals(meals: List[str], blocked_words: List[str]) -> List[Dict[str, Any]]:
    results = []
    for meal in meals:
        meal_lc = meal.lower()
        found = [w for w in blocked_words if w in meal_lc]

        if found:
            results.append({
                "meal": meal,
                "allowed": False,
                "status": "NOT ALLOWED",
                "matched_words": found,
                "reason": f"Contains: {', '.join(found)}"
            })
        else:
            results.append({
                "meal": meal,
                "allowed": True,
                "status": "CHECK",
                "matched_words": [],
                "reason": "No blocked words found in the menu text (still confirm with staff)."
            })
    return results


def filter_meals(allergen_phrases: Optional[List[str]] = None, outputs_dir: str = "outputs") -> Dict[str, Any]:
    """
    Filter meals from OCR text files based on allergen phrases.
    
    Args:
        allergen_phrases: List of encoded allergen phrases to decode and use for filtering.
                         If None, will use interactive mode.
        outputs_dir: Directory containing OCR output text files (default: "outputs")
    
    Returns:
        Dictionary containing:
            - "all_results": List of results for each text file
            - "output_path": Path to the JSON results file
            - "blocked_words": List of allergens that were blocked
    """
    # Decode allergen phrases or use interactive mode
    if allergen_phrases:
        print(f"\nDecoding allergen phrases: {allergen_phrases}")
        blocked_words = decode_allergen_phrases(allergen_phrases)
        
        if not blocked_words:
            raise ValueError("Could not decode any allergens from provided phrases.")
        
        print(f"Decoded allergens to block: {blocked_words}")
    else:
        # Interactive mode - prompt user
        print("\nEnter allergy words to block (comma-separated).")
        print("Example: milk, nuts, sesame")
        raw = input("Allergies/blocked words: ").strip()
        while not raw:
            raw = input("Please enter at least one word: ").strip()
        blocked_words = normalise_words(raw)

    # Where OCR text files are saved by your OCR script
    outputs_path = Path(outputs_dir)

    if not outputs_path.exists() or not outputs_path.is_dir():
        raise FileNotFoundError(f"Missing {outputs_dir} folder. Run OCR first: uv run python -u run_ocr_folder.py")

    txt_files = sorted(outputs_path.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in {outputs_dir}. Run OCR first: uv run python -u run_ocr_folder.py")

    all_results = []

    for txt in txt_files:
        raw = txt.read_text(encoding="utf-8", errors="ignore")
        meals = split_into_meals(raw)
        analysed = analyse_meals(meals, blocked_words)

        all_results.append({
            "source_text_file": txt.name,
            "blocked_words": blocked_words,
            "results": analysed
        })

        # Terminal summary
        not_allowed = sum(1 for r in analysed if not r["allowed"])
        print(f"\n=== {txt.name} ===")
        print(f"Meals found: {len(meals)} | NOT ALLOWED: {not_allowed} | CHECK: {len(meals) - not_allowed}")

        # Show up to first 12 lines so you can see it working
        for r in analysed[:12]:
            mark = "❌" if not r["allowed"] else "✅"
            print(f"{mark} {r['meal']}  -> {r['status']} ({r['reason']})")

    out_path = outputs_path / "filtered_results.json"
    out_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\n✅ Wrote full JSON results to: {out_path.resolve()}")
    
    return {
        "all_results": all_results,
        "output_path": str(out_path.resolve()),
        "blocked_words": blocked_words
    }


def main():
    """Command-line entry point - uses interactive mode."""
    filter_list = ["too", "harry", "dumb"]
    filter_meals(allergen_phrases=filter_list)


if __name__ == "__main__":
    main()
