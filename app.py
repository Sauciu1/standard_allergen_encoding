from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from run_filter_meals import filter_meals, HARDCODED_MENU
from flaskr import create_app

app = create_app()
CORS(app)  # Enable CORS for frontend requests


@app.route('/api/analyze-menu', methods=['POST'])
def analyze_menu():
    """
    Analyze menu items based on user's allergen code.
    
    Expected JSON body:
    {
        "allergen_phrases": ["word1", "word2", "word3"]
    }
    
    Returns:
    {
        "success": true,
        "results": [...],
        "user_allergen_phrases": [...],
        "stats": {
            "total": 10,
            "safe": 7,
            "avoid": 3
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'allergen_phrases' not in data:
            return jsonify({
                "success": False,
                "error": "Missing allergen_phrases in request body"
            }), 400
        
        allergen_phrases = data['allergen_phrases']
        
        if not isinstance(allergen_phrases, list) or len(allergen_phrases) == 0:
            return jsonify({
                "success": False,
                "error": "allergen_phrases must be a non-empty list"
            }), 400
        
        # Filter meals using hardcoded menu
        result = filter_meals(
            allergen_phrases=allergen_phrases,
            use_hardcoded_menu=True
        )
        
        # Extract results
        menu_results = result['all_results'][0]['results']
        
        # Calculate stats
        total = len(menu_results)
        avoid = sum(1 for r in menu_results if not r['allowed'])
        safe = total - avoid
        
        return jsonify({
            "success": True,
            "results": menu_results,
            "user_allergen_phrases": allergen_phrases,
            "stats": {
                "total": total,
                "safe": safe,
                "avoid": avoid
            }
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/api/menu', methods=['GET'])
def get_menu():
    """
    Get the hardcoded menu structure.
    
    Returns:
    {
        "success": true,
        "menu": [...]
    }
    """
    return jsonify({
        "success": True,
        "menu": HARDCODED_MENU
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    print("Starting AllergyAlly Menu Scanner API...")
    print("API will be available at http://localhost:5000")
    print("\nEndpoints:")
    print("  POST /api/analyze-menu - Analyze menu with allergen phrases")
    print("  GET  /api/menu         - Get hardcoded menu")
    print("  GET  /health           - Health check")
    app.run(debug=True, host='0.0.0.0', port=5000)
