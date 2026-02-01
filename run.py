#!/usr/bin/env python3
"""
Run the AllergyAlly Flask application locally.

Usage:
    python run.py

Then open http://localhost:5000 in your browser.
"""

from flaskr import create_app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("  AllergyAlly is running!")
    print("  Open http://localhost:5000 in your browser")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
