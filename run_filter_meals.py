import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path to import AllergiesGetter
sys.path.insert(0, str(Path(__file__).parent / "src"))
from allergies_getter import AllergiesGetter


# Hardcoded menu with allergen phrases for each item
HARDCODED_MENU = [
    {
        "meal": "Margherita Pizza",
        "allergen_phrases": ["cheese", "wheat", "tomato"]  # Database words representing allergens
    },
    {
        "meal": "Caesar Salad",
        "allergen_phrases": ["anchovy", "egg", "cheese"]
    },
    {
        "meal": "Peanut Butter Sandwich",
        "allergen_phrases": ["peanut", "wheat"]
    },
    {
        "meal": "Grilled Salmon",
        "allergen_phrases": ["fish", "lemon"]
    },
    {
        "meal": "Chicken Tikka Masala",
        "allergen_phrases": ["milk", "butter"]
    },
    {
        "meal": "Vegetable Stir Fry",
        "allergen_phrases": ["soy", "sesame"]
    },
    {
        "meal": "French Fries",
        "allergen_phrases": []  # No allergens
    },
    {
        "meal": "Chocolate Cake",
        "allergen_phrases": ["egg", "milk", "wheat"]
    },
    {
        "meal": "Shrimp Scampi",
        "allergen_phrases": ["shellfish", "butter", "wheat"]
    },
    {
        "meal": "Garden Salad",
        "allergen_phrases": []  # No allergens
    }
]


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
            
            # Return lowercased allergen names for matching
            return [a.lower() for a in allergens]
    except Exception as e:
        print(f"Error decoding allergen phrases: {e}")
        return []


def check_menu_item_allergens(item_allergen_phrases: List[str], user_allergens: List[str]) -> Dict[str, Any]:
    """
    Check if a menu item's allergen phrases match any of the user's allergens.
    
    Args:
        item_allergen_phrases: Database words representing the item's allergens
        user_allergens: User's decoded allergen names (lowercased)
        
    Returns:
        Dictionary with match information
    """
    if not item_allergen_phrases:
        return {
            "has_match": False,
            "matched_allergens": [],
            "item_allergens": []
        }
    
    # Decode the menu item's allergen phrases
    item_allergens = decode_allergen_phrases(item_allergen_phrases)
    
    # Find matches (case-insensitive)
    matched = [allergen for allergen in item_allergens if allergen in user_allergens]
    
    return {
        "has_match": len(matched) > 0,
        "matched_allergens": matched,
        "item_allergens": item_allergens
    }


def analyse_hardcoded_menu(user_allergen_phrases: List[str]) -> List[Dict[str, Any]]:
    """
    Analyse hardcoded menu against user's allergen phrases.
    
    Args:
        user_allergen_phrases: List of encoded allergen phrases from user
        
    Returns:
        List of analysis results for each menu item
    """
    # Decode user's allergen phrases
    print(f"\n=== Decoding User's Allergen Phrases ===")
    user_allergens = decode_allergen_phrases(user_allergen_phrases)
    
    if not user_allergens:
        raise ValueError("Could not decode user's allergen phrases")
    
    print(f"User's allergens to avoid: {user_allergens}")
    
    results = []
    
    print(f"\n=== Analyzing Menu Items ===")
    for item in HARDCODED_MENU:
        print(f"\nChecking: {item['meal']}")
        
        match_info = check_menu_item_allergens(item['allergen_phrases'], user_allergens)
        
        if match_info['has_match']:
            status = "NOT ALLOWED"
            allowed = False
            reason = f"Contains allergens: {', '.join(match_info['matched_allergens'])}"
        else:
            status = "SAFE"
            allowed = True
            if match_info['item_allergens']:
                reason = f"Contains other allergens ({', '.join(match_info['item_allergens'])}) but not in your list"
            else:
                reason = "No allergens detected"
        
        result = {
            "meal": item['meal'],
            "allowed": allowed,
            "status": status,
            "item_allergens": match_info['item_allergens'],
            "matched_allergens": match_info['matched_allergens'],
            "reason": reason
        }
        
        results.append(result)
        
        mark = "✅" if allowed else "❌"
        print(f"{mark} {status}: {reason}")
    
    return results


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


def filter_meals(allergen_phrases: Optional[List[str]] = None, outputs_dir: str = "outputs", use_hardcoded_menu: bool = False) -> Dict[str, Any]:
    """
    Filter meals from OCR text files or hardcoded menu based on allergen phrases.
    
    Args:
        allergen_phrases: List of encoded allergen phrases to decode and use for filtering.
                         If None, will use interactive mode.
        outputs_dir: Directory containing OCR output text files (default: "outputs")
        use_hardcoded_menu: If True, use hardcoded menu instead of OCR files
    
    Returns:
        Dictionary containing:
            - "all_results": List of results for each text file or hardcoded menu
            - "output_path": Path to the JSON results file (if applicable)
            - "user_allergen_phrases": List of user's encoded phrases
            - "decoded_allergens": List of decoded allergen names
    """
    # Get allergen phrases
    if allergen_phrases:
        print(f"\nUser provided allergen phrases: {allergen_phrases}")
    else:
        # Interactive mode - prompt user
        print("\nEnter allergen database words (comma-separated).")
        print("Example: cheese, peanut, fish")
        raw = input("Allergen phrases: ").strip()
        while not raw:
            raw = input("Please enter at least one word: ").strip()
        allergen_phrases = [w.strip() for w in raw.split(",") if w.strip()]

    # Use hardcoded menu
    if use_hardcoded_menu:
        print("\n" + "=" * 60)
        print("USING HARDCODED MENU")
        print("=" * 60)
        
        # Decode user's allergens first to get the decoded names
        user_allergens = decode_allergen_phrases(allergen_phrases)
        
        analysed = analyse_hardcoded_menu(allergen_phrases)
        
        # Summary
        not_allowed = sum(1 for r in analysed if not r["allowed"])
        safe = len(analysed) - not_allowed
        
        print(f"\n" + "=" * 60)
        print(f"SUMMARY: Total items: {len(analysed)} | NOT ALLOWED: {not_allowed} | SAFE: {safe}")
        print("=" * 60)
        
        # Save results
        output_dir = Path(outputs_dir)
        output_dir.mkdir(exist_ok=True)
        out_path = output_dir / "hardcoded_menu_results.json"
        
        result_data = {
            "source": "hardcoded_menu",
            "user_allergen_phrases": allergen_phrases,
            "decoded_allergens": user_allergens,
            "results": analysed
        }
        
        out_path.write_text(json.dumps(result_data, indent=2), encoding="utf-8")
        print(f"\n✅ Wrote results to: {out_path.resolve()}")
        
        return {
            "all_results": [result_data],
            "output_path": str(out_path.resolve()),
            "user_allergen_phrases": allergen_phrases,
            "decoded_allergens": user_allergens
        }
    
    # Original OCR-based filtering
    else:
        # Decode allergen phrases
        print(f"\nDecoding allergen phrases: {allergen_phrases}")
        blocked_words = decode_allergen_phrases(allergen_phrases)
        
        if not blocked_words:
            raise ValueError("Could not decode any allergens from provided phrases.")
        
        print(f"Decoded allergens to block: {blocked_words}")

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
            "blocked_words": blocked_words,
            "decoded_allergens": blocked_words
        }


def main():
    """Command-line entry point - uses hardcoded menu for testing."""
    # Example: User has allergies to items encoded as these database words
    user_allergen_phrases = ["too", "harry", "dumb"]  # These are database words
    
    # Use hardcoded menu for testing
    filter_meals(allergen_phrases=user_allergen_phrases, use_hardcoded_menu=True)


if __name__ == "__main__":
    main()
