import os
import sys
import csv
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
# from ..src.allergies_getter import AllergiesGetter

# Store encoded codes for decoding (in production, use a database)
code_storage = {}

def load_allergens_from_csv(file_paths):
    '''Load allergens from given CSV files and return a list of allergen dictionaries.'''
    unique_allergens = set()
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found.")
            continue
            
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row
            for row in reader:
                if len(row) >= 2:
                    # row[1] is the 'allergen' column
                    allergen_name = row[1].strip()
                    if allergen_name:
                        unique_allergens.add(allergen_name)
    
    return unique_allergens

# Define paths to your files
project_root = os.path.dirname(os.path.dirname(__file__))

csv_paths = [
    os.path.join(project_root, 'data', 'allergens', 'main_allergens.csv'),
    os.path.join(project_root, 'data', 'allergens', 'secondary_allergens.csv')
]

# Load the dynamic list
ALLERGENS = load_allergens_from_csv(csv_paths)


def decode_code(code):
    """Decode a three-word code back to allergen IDs."""
    code = code.lower().strip()

    # Check if we have this code stored
    if code in code_storage:
        return code_storage[code]

    # Fallback mock results for demo
    mock_results = {
        "ocean.maple.thunder": ["milk", "peanuts", "shellfish"],
        "crystal.velvet.ember": ["eggs", "wheat", "soy"],
        "meadow.storm.willow": ["fish", "tree-nuts"],
        "river.breeze.dawn": ["sesame", "mustard"],
    }

    return mock_results.get(code, ["milk", "eggs"])


def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Get the path to the frontend folder
    frontend_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    app = Flask(__name__, 
                static_folder=frontend_folder,
                static_url_path='',
                instance_relative_config=True)
    
    # Enable CORS
    CORS(app)
    
    # Load default config
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    
    if test_config is None:
        # Load instance config if it exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load test config
        app.config.from_mapping(test_config)
    
    # Add src to path to import modules
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    from run_filter_meals import filter_meals, HARDCODED_MENU
    
    # Serve static files from frontend
    @app.route('/')
    def serve_index():
        """Serve the main frontend page"""
        return send_from_directory(frontend_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files from frontend folder"""
        # Check if file exists
        file_path = os.path.join(frontend_folder, path)
        if os.path.isfile(file_path):
            return send_from_directory(frontend_folder, path)
        # If it's a directory, try to serve index.html from it
        if os.path.isdir(file_path):
            return send_from_directory(file_path, 'index.html')
        # Default to 404
        return "Not Found", 404

    # ==========================================
    # API ROUTES
    # ==========================================

    @app.route('/api/allergens', methods=['GET'])
    def get_allergens():
        """Get list of all allergens."""
        # Convert set to sorted list for JSON serialization
        return jsonify({"allergens": sorted(list(ALLERGENS))})

    @app.route('/api/encode', methods=['POST'])
    def api_encode():
        """Encode allergens into a three-word code."""
        data = request.get_json()
        allergen_ids = data.get('allergens', [])

        if not allergen_ids:
            return jsonify({"error": "No allergens provided"}), 400

        # TODO: Implement proper encoding
        # For now, return a placeholder response
        return jsonify({
            "code": "placeholder.code.here",
            "allergens": allergen_ids
        })

    @app.route('/api/decode', methods=['POST'])
    def api_decode():
        """Decode a three-word code back to allergens."""
        data = request.get_json()
        code = data.get('code', '')

        if not code:
            return jsonify({"error": "No code provided"}), 400

        allergen_names = decode_code(code)

        return jsonify({
            "success": True,
            "menu": HARDCODED_MENU,
            "allergens": allergen_names
        })
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "healthy"})
    
    @app.route('/api/analyze-menu', methods=['POST'])
    def analyze_menu():
        """
        Analyze menu items based on user's allergen code.
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
            decoded_allergens = result.get('decoded_allergens', [])
            
            # Calculate stats
            total = len(menu_results)
            avoid = sum(1 for r in menu_results if not r['allowed'])
            safe = total - avoid
            
            return jsonify({
                "success": True,
                "results": menu_results,
                "user_allergen_phrases": allergen_phrases,
                "user_allergens": decoded_allergens,
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
        """Get the hardcoded menu structure."""
        return jsonify({
            "success": True,
            "menu": HARDCODED_MENU
        })
    
    return app
