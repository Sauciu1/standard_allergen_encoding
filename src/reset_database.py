"""Reset the database - drop and recreate with all words."""

from db_manager import DatabaseManager

if __name__ == "__main__":
    db = DatabaseManager()
    
    print("Dropping existing database...")
    db.drop_database()
    
    print("Creating new database with ALL available words...")
    db.initialize()
    
    # Export using both formats
    print("\nExporting database...")
    # db.export_to_sql()      # SQL format (human-readable, for git)
    db.export_to_dump()     # Binary format (efficient, industry standard)
    
    print(f"\nTotal words: {db.get_total_words()}")
