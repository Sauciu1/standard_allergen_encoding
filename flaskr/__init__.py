import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS


# Allergen data
ALLERGENS = [
    {"id": "milk", "name": "Milk", "emoji": "🥛"},
    {"id": "eggs", "name": "Eggs", "emoji": "🥚"},
    {"id": "peanuts", "name": "Peanuts", "emoji": "🥜"},
    {"id": "tree-nuts", "name": "Tree Nuts", "emoji": "🌰"},
    {"id": "wheat", "name": "Wheat", "emoji": "🌾"},
    {"id": "soy", "name": "Soy", "emoji": "🫘"},
    {"id": "fish", "name": "Fish", "emoji": "🐟"},
    {"id": "shellfish", "name": "Shellfish", "emoji": "🦐"},
    {"id": "sesame", "name": "Sesame", "emoji": "🫘"},
    {"id": "mustard", "name": "Mustard", "emoji": "🟡"},
    {"id": "celery", "name": "Celery", "emoji": "🥬"},
    {"id": "lupin", "name": "Lupin", "emoji": "🌸"},
    {"id": "molluscs", "name": "Molluscs", "emoji": "🦪"},
    {"id": "sulphites", "name": "Sulphites", "emoji": "🍷"},
]

WORD_POOL = [
    "ocean", "maple", "thunder", "crystal", "velvet", "ember", "frost", "coral",
    "meadow", "storm", "willow", "sage", "river", "breeze", "dawn", "dusk",
    "summit", "valley", "canyon", "ridge", "harbor", "beacon", "anchor", "compass",
    "cedar", "birch", "oak", "pine", "fern", "moss", "ivy", "bloom",
]

# Store encoded codes for decoding (in production, use a database)
code_storage = {}


def encode_allergens(allergen_ids):
    """Encode allergen IDs into a three-word code."""
    if not allergen_ids:
        return ""

    sorted_ids = sorted(allergen_ids)
    hash_string = "-".join(sorted_ids)
    hash_num = 0

    for char in hash_string:
        hash_num = ((hash_num << 5) - hash_num) + ord(char)
        hash_num = hash_num & 0xFFFFFFFF  # Keep it 32-bit
    hash_num = abs(hash_num)

    word1 = WORD_POOL[hash_num % len(WORD_POOL)]
    word2 = WORD_POOL[(hash_num * 7) % len(WORD_POOL)]
    word3 = WORD_POOL[(hash_num * 13) % len(WORD_POOL)]

    code = f"{word1}.{word2}.{word3}"

    # Store for later decoding
    code_storage[code] = sorted_ids

    return code


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
    # Get the path to the frontend folder
    frontend_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

    # Create and configure the app
    app = Flask(__name__,
                static_folder=frontend_folder,
                static_url_path='')

    # Enable CORS for API routes
    CORS(app)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    # ==========================================
    # STATIC FILE ROUTES (Serve Frontend)
    # ==========================================

    @app.route('/')
    def index():
        """Serve the main index.html"""
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
        return jsonify({"allergens": ALLERGENS})

    @app.route('/api/encode', methods=['POST'])
    def api_encode():
        """Encode allergens into a three-word code."""
        data = request.get_json()
        allergen_ids = data.get('allergens', [])

        if not allergen_ids:
            return jsonify({"error": "No allergens provided"}), 400

        code = encode_allergens(allergen_ids)

        return jsonify({
            "code": code,
            "allergens": allergen_ids
        })

    @app.route('/api/decode', methods=['POST'])
    def api_decode():
        """Decode a three-word code back to allergens."""
        data = request.get_json()
        code = data.get('code', '')

        if not code:
            return jsonify({"error": "No code provided"}), 400

        allergen_ids = decode_code(code)

        # Get full allergen info
        allergens = []
        for aid in allergen_ids:
            allergen = next((a for a in ALLERGENS if a['id'] == aid), None)
            if allergen:
                allergens.append(allergen)

        return jsonify({
            "code": code,
            "allergen_ids": allergen_ids,
            "allergens": allergens
        })

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "ok", "message": "AllergyAlly API is running"})

    return app
