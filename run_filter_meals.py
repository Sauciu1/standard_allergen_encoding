import json
import re
from pathlib import Path
from typing import List, Dict, Any


def normalise_words(csv: str) -> List[str]:
    return [w.strip().lower() for w in csv.split(",") if w.strip()]


def prompt_for_allergies() -> List[str]:
    """
    Prompts user to type allergies/blocked words.
    Example input: milk, nuts, sesame
    """
    print("\nEnter allergy words to block (comma-separated).")
    print("Example: milk, nuts, sesame")
    raw = input("Allergies/blocked words: ").strip()
    while not raw:
        raw = input("Please enter at least one word: ").strip()
    return normalise_words(raw)


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


def main():
    # Where OCR text files are saved by your OCR script
    outputs_dir = Path("outputs")

    if not outputs_dir.exists() or not outputs_dir.is_dir():
        raise SystemExit("Missing ./outputs folder. Run OCR first: uv run python -u run_ocr_folder.py")

    txt_files = sorted(outputs_dir.glob("*.txt"))
    if not txt_files:
        raise SystemExit("No .txt files found in ./outputs. Run OCR first: uv run python -u run_ocr_folder.py")

    blocked_words = prompt_for_allergies()

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

    out_path = outputs_dir / "filtered_results.json"
    out_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\n✅ Wrote full JSON results to: {out_path.resolve()}")


if __name__ == "__main__":
    main()
