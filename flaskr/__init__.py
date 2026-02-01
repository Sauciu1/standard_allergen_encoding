import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path


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
    
    @app.route('/product/<path:filename>')
    def serve_product(filename):
        """Serve product pages"""
        product_folder = os.path.join(frontend_folder, 'product')
        return send_from_directory(product_folder, filename)
    
    @app.route('/<path:filename>')
    def serve_static_files(filename):
        """Serve other static files (CSS, JS, images)"""
        return send_from_directory(frontend_folder, filename)
    
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
            "user_allergens": [...],  # Decoded allergen names
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
            decoded_allergens = result.get('decoded_allergens', [])
            
            # Calculate stats
            total = len(menu_results)
            avoid = sum(1 for r in menu_results if not r['allowed'])
            safe = total - avoid
            
            return jsonify({
                "success": True,
                "results": menu_results,
                "user_allergen_phrases": allergen_phrases,
                "user_allergens": decoded_allergens,  # Add decoded allergens
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
    
    return app
