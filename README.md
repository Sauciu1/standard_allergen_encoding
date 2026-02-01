# AllergyAlly - Standard Allergen Encoding

A system for encoding allergen information into memorable word codes that can be easily shared and decoded.

##  Quick Start (requires Postgres SQL)

The app works out of the box using a pre-built database dump file. Just run:

```bash
git clone https://github.com/Sauciu1/standard_allergen_encoding
cd standard_allergen_encoding
uv sync
```

Activate virtual environment for Windows or macOS/Linux
```bash
.venv\Scripts\activate
source .venv/bin/activate
```
```bash
flask --app flaskr run --debug
```

**Open in browser:** `http://127.0.0.1:5000/`


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

## Features


- **Encode allergens** to memorable word codes
- **Decode codes** back to allergens
- **Group codes** for multiple people dining together
- **Menu scanner** to check food safety
- **QR code generation** for easy sharing


---

## How It Works

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

#### Database setup

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


# Usage

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

---

##  API Documentation

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

## Project Structure

```
standard_allergen_encoding/
├── data/
│   ├── allergens/              # Allergen CSV files
│   │   ├── main_allergens.csv  # UK top 14 allergens
│   │   └── secondary_allergens.csv  # Specific types
│   └── word_mapping.dump
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