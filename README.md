# AllergyAlly - Standard Allergen Encoding

A system for encoding allergen information into memorable word codes that can be easily shared and decoded.

## 🚀 Quick Start (No PostgreSQL Required!)

The app works out of the box using a pre-built database dump file. Just run:

```bash
# Clone the repository
git clone <your-repo-url>
cd standard_allergen_encoding

# Install dependencies
pip install -r requirements.txt
# Or with uv (recommended - faster!)
uv sync

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Run the Flask app
flask --app flaskr run --debug
```

**Open in browser:** `http://localhost:5000`

That's it! No database setup required - the app uses a pre-built dump file committed to git.

---

## 📋 Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
  - [Quick Setup (No PostgreSQL)](#quick-setup-no-postgresql)
  - [Full Setup (With PostgreSQL)](#full-setup-with-postgresql)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Deployment](#deployment)

---

## ✨ Features

- ✅ **Zero setup required** - Uses pre-built database dump
- ✅ **Automatic fallback** - Works without PostgreSQL installation
- ✅ **Encode allergens** to memorable word codes
- ✅ **Decode codes** back to allergens
- ✅ **Group codes** for multiple people dining together
- ✅ **Menu scanner** to check food safety
- ✅ **QR code generation** for easy sharing
- ✅ **Cross-platform** - Works on Windows, macOS, Linux

---

## 🔧 How It Works

### Database Modes

The system automatically uses the best available option:

1. **PostgreSQL (preferred)** - Full database with all features
2. **Dump File (fallback)** - Pre-built word mapping from `data/database/word_mapping.pkl`

The dump file is committed to git, so **everyone can run the app immediately** without any database setup!

### Encoding System

Allergens are encoded into memorable words using:

- **Main allergens** (e.g., peanuts, milk, eggs) → Binary encoding
- **Secondary allergens** (specific types) → Grouped binary encoding
- **Word mapping** → Each encoded number maps to a dictionary word

Example:

```
Input:  ['peanuts', 'milk', 'eggs']
Encode: [25, 0] → Binary numbers
Map:    ['ocean', 'maple'] → Dictionary words
Output: "ocean maple" → Shareable code
```

---

## 📦 Installation

### Quick Setup (No PostgreSQL)

**Perfect for:** Testing, development, or if you don't want to install PostgreSQL

```bash
# 1. Clone repository
git clone <your-repo-url>
cd standard_allergen_encoding

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
# Or with uv (faster):
# pip install uv
# uv sync

# 5. Run the app
flask --app flaskr run --debug
```

**That's it!** Open `http://localhost:5000` in your browser.

---

### Full Setup (With PostgreSQL)

**Perfect for:** Production deployment or if you want to modify the database

#### Step 1: Install PostgreSQL

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS (with Homebrew):**

```bash
brew install postgresql@14
brew services start postgresql@14
```

**Windows:**

1. Download installer from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Run installer and follow wizard
3. Remember the password you set for `postgres` user
4. Add PostgreSQL bin directory to PATH (usually `C:\Program Files\PostgreSQL\14\bin`)

**Verify Installation:**

```bash
psql --version
# Should output: psql (PostgreSQL) 14.x
```

#### Step 2: Create Database User (Optional but Recommended)

```bash
# Switch to postgres user (Linux/macOS)
sudo -u postgres psql

# Or connect directly (Windows/macOS with Homebrew)
psql postgres
```

In PostgreSQL shell:

```sql
-- Create a user for the app
CREATE USER allergyally WITH PASSWORD 'your_secure_password';

-- Grant privileges
ALTER USER allergyally CREATEDB;

-- Exit
\q
```

#### Step 3: Configure Database Connection (Optional)

If using custom credentials, create `.env` file:

```bash
# In project root
cat > .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=allergen_db
DB_USER=allergyally
DB_PASSWORD=your_secure_password
EOF
```

If not using `.env`, the app will use default PostgreSQL settings.

#### Step 4: Clone and Install

```bash
# Clone repository
git clone <your-repo-url>
cd standard_allergen_encoding

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 5: Initialize Database

**Option A: Use Existing Dump (Fastest)**

```bash
cd src
python reset_database.py
# This loads the pre-built dump file
```

**Option B: Build From Scratch**

```bash
cd src
python db_manager.py
# This generates the word mapping from scratch (takes a few seconds)
```

#### Step 6: Run the App

```bash
# From project root
flask --app flaskr run --debug
```

Open `http://localhost:5000` in your browser.

---

## 🎯 Usage

### Web Interface

1. **Individual Code Page** (`/product/individual.html`)
   - Select your allergens from dropdown
   - Generate your personal allergen code
   - Get QR code for easy sharing
   - Decode others' codes

2. **Group Code Page** (`/product/group.html`)
   - Add multiple people with their codes
   - Generate combined code for group dining
   - Covers everyone's allergens

3. **Menu Scanner** (`/product/menu.html`)
   - Enter your allergen code
   - See which menu items are safe
   - Avoid items with your allergens

### Command Line

**Encode allergens:**

```bash
cd src
python allergies_getter.py
# Follow interactive prompts
```

**Process menu images:**

```bash
# 1. OCR menu images
python run_ocr_folder.py menu_photos/

# 2. Analyze with your allergen code
python run_filter_meals.py
```

---

## 📡 API Documentation

Base URL: `http://localhost:5000/api`

### Get All Allergens

```http
GET /api/allergens
```

**Response:**

```json
{
  "allergens": ["milk", "eggs", "peanuts", ...]
}
```

### Encode Allergens

```http
POST /api/encode
Content-Type: application/json

{
  "allergens": ["peanuts", "milk", "eggs"]
}
```

**Response:**

```json
{
  "success": true,
  "code": "ocean maple",
  "words": ["ocean", "maple"],
  "allergens": ["peanuts", "milk", "eggs"]
}
```

### Decode Code

```http
POST /api/decode
Content-Type: application/json

{
  "code": "ocean maple"
}
```

**Response:**

```json
{
  "success": true,
  "code": "ocean maple",
  "words": ["ocean", "maple"],
  "allergens": ["peanuts", "milk", "eggs"]
}
```

### Combine Codes (Group)

```http
POST /api/combine-codes
Content-Type: application/json

{
  "codes": ["ocean maple", "river dawn"]
}
```

**Response:**

```json
{
  "success": true,
  "combined_code": "thunder valley crystal",
  "combined_allergens": ["eggs", "milk", "peanuts", "sesame"],
  "individual_allergens": [
    { "code": "ocean maple", "allergens": ["peanuts", "milk"] },
    { "code": "river dawn", "allergens": ["eggs", "sesame"] }
  ]
}
```

### Analyze Menu

```http
POST /api/analyze-menu
Content-Type: application/json

{
  "allergen_phrases": ["ocean", "maple"]
}
```

**Response:**

```json
{
  "success": true,
  "results": [...],
  "user_allergens": ["peanuts", "milk", "eggs"],
  "stats": {
    "total": 10,
    "safe": 7,
    "avoid": 3
  }
}
```

---

## 📁 Project Structure

```
standard_allergen_encoding/
├── data/
│   ├── allergens/              # Allergen CSV files
│   │   ├── main_allergens.csv  # UK top 14 allergens
│   │   └── secondary_allergens.csv  # Specific types
│   ├── database/               # Database exports
│   │   └── word_mapping.pkl    # ⭐ Pre-built dump (committed!)
│   └── words/                  # Word lists for encoding
│       └── words.txt
├── src/                        # Core logic
│   ├── allergies_encoder.py   # Binary encoding system
│   ├── allergies_getter.py    # Database interface (auto-fallback)
│   ├── db_manager.py           # PostgreSQL manager
│   └── reset_database.py      # Reset/export database
├── flaskr/                     # Flask API
│   └── __init__.py             # API routes
├── frontend/                   # Web interface
│   ├── product/
│   │   ├── individual.html     # Personal code page
│   │   ├── group.html          # Group code page
│   │   └── menu.html           # Menu scanner
│   ├── individual-script.js
│   ├── group-script.js
│   ├── menu-script.js
│   └── styles.css
├── run_ocr_folder.py           # OCR for menu images
├── run_filter_meals.py         # Menu analysis
├── requirements.txt            # Python dependencies
├── pyproject.toml              # UV/pip metadata
└── README.md                   # This file!
```

---

## 🔨 Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_encoder.py

# With coverage
pytest --cov=src
```

### Modifying Allergens

1. Edit CSV files in `data/allergens/`
2. Regenerate database:
   ```bash
   cd src
   python reset_database.py
   ```
3. Commit the updated `word_mapping.pkl`:
   ```bash
   git add data/database/word_mapping.pkl
   git commit -m "Update allergen database"
   ```

### Creating New Database Dump

```bash
cd src
python reset_database.py
# This creates data/database/word_mapping.pkl
# Commit this file so others can use it!
```

### Code Style

```bash
# Format code
black src/ flaskr/

# Lint
flake8 src/ flaskr/

# Type check
mypy src/
```

---

## 🐛 Troubleshooting

### "Cannot load database dump file"

**Solution 1:** Make sure `data/database/word_mapping.pkl` exists

```bash
# Check if file exists
ls -la data/database/word_mapping.pkl

# If missing, regenerate it
cd src
python reset_database.py
```

**Solution 2:** If you have PostgreSQL, it will create the file automatically

---

### "connection to server at 'localhost' port 5432 failed"

This means PostgreSQL isn't running. **You have two options:**

**Option 1: Use Dump File (No PostgreSQL needed)**

- The app automatically falls back to using `data/database/word_mapping.pkl`
- No action needed - it should work!

**Option 2: Install PostgreSQL**

- See [Full Setup (With PostgreSQL)](#full-setup-with-postgresql) section above

---

### "Tesseract OCR is not installed"

OCR is only needed for menu scanning feature.

**Install Tesseract:**

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

---

### "Module not found" errors

```bash
# Make sure virtual environment is activated
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Port 5000 already in use

```bash
# Use a different port
flask --app flaskr run --port 5001

# Or kill the process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9
```

---

## 🚀 Deployment

### Production Setup

1. **Use PostgreSQL for better performance**
2. **Set environment variables:**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=<random-secure-key>
   export DB_HOST=<your-db-host>
   export DB_PASSWORD=<secure-password>
   ```
3. **Use a production server (not Flask dev server):**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 'flaskr:create_app()'
   ```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["flask", "--app", "flaskr", "run", "--host=0.0.0.0"]
```

Build and run:

```bash
docker build -t allergyally .
docker run -p 5000:5000 allergyally
```

---

## 📄 License

MIT

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📞 Support

- **Issues:** [GitHub Issues](your-repo-url/issues)
- **Documentation:** This README
- **Email:** your-email@example.com

---

**Made with ❤️ for food allergy awareness**
