# AllergyAlly - Standard Allergen Encoding

A system for encoding allergen information into memorable word codes that can be easily shared and decoded.

## Quick Start (No Setup Required!)

The app works out of the box using a pre-built database dump file. Just run:

```bash
# Install dependencies
pip install -r requirements.txt

# Or with uv (recommended)
uv sync

# Run the Flask app
flask --app flaskr run --debug
```

Open: `http://localhost:5000`

## How It Works

### Database Modes

The system automatically uses the best available option:

1. **PostgreSQL (preferred)** - Full database with all features
2. **Dump File (fallback)** - Pre-built word mapping from `data/database/word_mapping.pkl`

The dump file is committed to git, so everyone can run the app immediately without any database setup!

### For Developers

If you want to modify the database:

#### Option 1: Use PostgreSQL Locally

```bash
# Install PostgreSQL
# Ubuntu/Debian: sudo apt-get install postgresql
# macOS: brew install postgresql

# Initialize the database
cd src
python db_manager.py

# Run the app
flask --app flaskr run --debug
```

#### Option 2: Regenerate the Dump File

If you modify allergen data:

```bash
# Reset and export database
cd src
python reset_database.py

# This creates/updates data/database/word_mapping.pkl
# Commit this file so others can use it!
```

## Project Structure

```
standard_allergen_encoding/
├── data/
│   ├── allergens/          # Allergen CSV files
│   │   ├── main_allergens.csv
│   │   └── secondary_allergens.csv
│   ├── database/           # Database exports
│   │   └── word_mapping.pkl  # ⭐ Committed to git!
│   └── words/              # Word list for encoding
├── src/                    # Core logic
│   ├── allergies_encoder.py
│   ├── allergies_getter.py   # Auto-fallback logic
│   └── db_manager.py
├── flaskr/                 # Flask API
└── frontend/               # Web interface
```

## Features

- ✅ **Zero setup required** - Uses pre-built database dump
- ✅ **Automatic fallback** - Works without PostgreSQL
- ✅ **Encode allergens** to memorable codes
- ✅ **Decode codes** back to allergens
- ✅ **Group codes** for multiple people
- ✅ **Menu scanner** to check food safety
- ✅ **Cross-platform** - Works on any OS

## API Endpoints

- `GET /api/allergens` - List all allergens
- `POST /api/encode` - Encode allergens to code
- `POST /api/decode` - Decode code to allergens
- `POST /api/combine-codes` - Combine multiple codes
- `POST /api/analyze-menu` - Check menu safety

## Development

```bash
# Install dependencies
uv sync

# Run tests
pytest

# Run Flask in debug mode
flask --app flaskr run --debug

# Reset database (optional)
cd src
python reset_database.py
```

## Deployment

The dump file (`word_mapping.pkl`) is committed to git, so deployment is simple:

```bash
git clone <repo>
pip install -r requirements.txt
flask --app flaskr run
```

No database setup needed!

## Troubleshooting

### "Cannot load database dump file"

Make sure `data/database/word_mapping.pkl` exists. If not:

```bash
cd src
python reset_database.py
```

This will create the dump file.

### Want to use PostgreSQL?

1. Install PostgreSQL for your OS
2. The app will automatically detect and use it
3. Falls back to dump file if PostgreSQL isn't available

## License

MIT
