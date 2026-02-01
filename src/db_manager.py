import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Optional, List, Tuple
import logging
from dotenv import load_dotenv
import subprocess

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages PostgreSQL database for standard allergen encoding."""
    
    # Word length constraints
    MIN_WORD_LENGTH = 3
    MAX_WORD_LENGTH = 7
    
    def __init__(
        self,
        db_name: str = "allergen_encoding",
        host: str = None,
        port: str = None,
        user: str = None,
        password: str = None
    ):
        """
        Initialize DatabaseManager with connection parameters.
        
        Args:
            db_name: Name of the database
            host: Database host (defaults to env var DB_HOST or 'localhost')
            port: Database port (defaults to env var DB_PORT or '5432')
            user: Database user (defaults to env var DB_USER or 'postgres')
            password: Database password (defaults to env var DB_PASSWORD)
        """
        self.db_name = db_name
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or os.getenv('DB_PORT', '5432')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD')
        
        if not self.password:
            raise ValueError(
                "Database password not provided. Set DB_PASSWORD environment variable "
                "or create a .env file with DB_PASSWORD=your_password"
            )
        
        self.connection: Optional[psycopg2.extensions.connection] = None
    
    def _get_connection(self, database: str = 'postgres') -> psycopg2.extensions.connection:
        """Create a database connection."""
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=database
        )
    
    def database_exists(self) -> bool:
        """Check if the database exists."""
        conn = self._get_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_name,)
            )
            exists = cursor.fetchone() is not None
            return exists
        finally:
            cursor.close()
            conn.close()
    
    def create_database(self):
        """Create the database if it doesn't exist."""
        if self.database_exists():
            logger.info(f"Database '{self.db_name}' already exists.")
            return
        
        conn = self._get_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(self.db_name)
            ))
            logger.info(f"Database '{self.db_name}' created successfully.")
        finally:
            cursor.close()
            conn.close()
    
    def drop_database(self):
        """Delete the entire database."""
        if not self.database_exists():
            logger.info(f"Database '{self.db_name}' does not exist.")
            return
        
        # Close any existing connections
        if self.connection and not self.connection.closed:
            self.connection.close()
        
        conn = self._get_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        try:
            # Terminate other connections to the database
            cursor.execute(sql.SQL("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                AND pid <> pg_backend_pid()
            """), (self.db_name,))
            
            # Drop the database
            cursor.execute(sql.SQL("DROP DATABASE {}").format(
                sql.Identifier(self.db_name)
            ))
            logger.info(f"Database '{self.db_name}' deleted successfully.")
            print(f"Database '{self.db_name}' deleted")
        finally:
            cursor.close()
            conn.close()
    
    def connect(self):
        """Connect to the database."""
        if self.connection is None or self.connection.closed:
            self.connection = self._get_connection(self.db_name)
            logger.info(f"Connected to database '{self.db_name}'.")
    
    def close(self):
        """Close the database connection."""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("Database connection closed.")
    
    def create_word_mapping_table(self):
        """Create the word mapping table if it doesn't exist."""
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS word_mapping (
                    id SERIAL PRIMARY KEY,
                    number INTEGER UNIQUE NOT NULL,
                    word VARCHAR({self.MAX_WORD_LENGTH}) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
            logger.info("Word mapping table created/verified.")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error creating table: {e}")
            raise
        finally:
            cursor.close()
    
    def get_dictionary_words(self, max_words: int = None) -> List[str]:
        """
        Get English dictionary words between 3-6 letters.
        Uses nltk words corpus with frequency data, falls back to system dictionary.
        
        Args:
            max_words: Maximum number of most common words to return (None = all words)
        """
        # Try using nltk with word frequency first (most portable)
        try:
            import nltk
            
            # Try to get Brown corpus for frequency data
            try:
                from nltk.corpus import brown
                brown.words()  # Test if it's available
            except LookupError:
                logger.info("Downloading nltk brown corpus...")
                nltk.download('brown', quiet=False)
                from nltk.corpus import brown
            
            # Get word frequencies from Brown corpus
            word_freq = {}
            for word in brown.words():
                word_lower = word.lower()
                if word_lower.isalpha() and self.MIN_WORD_LENGTH <= len(word_lower) <= self.MAX_WORD_LENGTH:
                    word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            
            # Sort by frequency and take most common (or all if max_words is None)
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            if max_words:
                filtered_words = [word for word, freq in sorted_words[:max_words]]
            else:
                filtered_words = [word for word, freq in sorted_words]
            
            logger.info(f"Loaded {len(filtered_words)} most common words from Brown corpus")
            return filtered_words
            
        except Exception as e:
            logger.warning(f"Could not load Brown corpus: {e}")
            logger.info("Falling back to simple word list...")
            
            # Fallback: try basic words corpus without frequency
            try:
                import nltk
                try:
                    from nltk.corpus import words
                    words.words()  # Test if available
                except LookupError:
                    logger.info("Downloading nltk words corpus...")
                    nltk.download('words', quiet=False)
                    from nltk.corpus import words
                
                # Filter words without frequency data
                all_words = set()
                for word in words.words():
                    if word.islower() and word.isalpha() and self.MIN_WORD_LENGTH <= len(word) <= self.MAX_WORD_LENGTH:
                        all_words.add(word.lower())
                
                filtered_words = sorted(list(all_words))
                logger.info(f"Loaded {len(filtered_words)} words from nltk words corpus")
                return filtered_words[:max_words] if max_words else filtered_words
                
            except Exception as e2:
                logger.warning(f"Could not load words corpus: {e2}")
        
        # Fallback to system dictionary
        logger.info("Trying system dictionary...")
        dict_paths = [
            '/usr/share/dict/words',
            '/usr/dict/words',
            '/usr/share/dict/american-english'
        ]
        
        for path in dict_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    words = []
                    for word in f:
                        word = word.strip()
                        if word.islower() and word.isalpha() and self.MIN_WORD_LENGTH <= len(word) <= self.MAX_WORD_LENGTH:
                            words.append(word)
                logger.info(f"Loaded {len(words)} words from {path}")
                return words[:max_words] if max_words else words
        
        # Final fallback to a small sample if no dictionary found
        logger.warning("No dictionary found, using fallback words.")
        return ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her']
    
    def populate_word_mapping(self):
        """Populate the word mapping table with dictionary words."""
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            # Check if table already has data
            cursor.execute("SELECT COUNT(*) FROM word_mapping")
            count = cursor.fetchone()[0]
            
            if count > 0:
                logger.info(f"Word mapping table already contains {count} entries.")
                return
            
            # Get dictionary words
            words = self.get_dictionary_words()
            
            # Insert words with sequential numbers
            insert_query = """
                INSERT INTO word_mapping (number, word)
                VALUES (%s, %s)
                ON CONFLICT (word) DO NOTHING
            """
            
            data = [(i, word) for i, word in enumerate(words, start=1)]
            cursor.executemany(insert_query, data)
            self.connection.commit()
            
            logger.info(f"Inserted {cursor.rowcount} words into word_mapping table.")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error populating word mapping: {e}")
            raise
        finally:
            cursor.close()
    
    def initialize(self):
        """Initialize the database and populate with data."""
        try:
            self.create_database()
            self.connect()
            self.create_word_mapping_table()
            self.populate_word_mapping()
            logger.info("Database initialization complete.")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def get_word_by_number(self, number: int) -> Optional[str]:
        """Get word for a given number."""
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("SELECT word FROM word_mapping WHERE number = %s", (number,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
    
    def get_number_by_word(self, word: str) -> Optional[int]:
        """Get number for a given word."""
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("SELECT number FROM word_mapping WHERE word = %s", (word.lower(),))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
    
    def view_database_sample(self, limit: int = 20) -> List[Tuple[int, str]]:
        """
        View a sample of entries from the database.
        
        Args:
            limit: Number of entries to retrieve
            
        Returns:
            List of (number, word) tuples
        """
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            cursor.execute(
                "SELECT number, word FROM word_mapping ORDER BY number LIMIT %s",
                (limit,)
            )
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()
    
    def get_total_words(self) -> int:
        """Get total count of words in database."""
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM word_mapping")
            return cursor.fetchone()[0]
        finally:
            cursor.close()
    
    def search_words(self, pattern: str) -> List[Tuple[int, str]]:
        """
        Search for words matching a pattern.
        
        Args:
            pattern: SQL LIKE pattern (use % for wildcard)
            
        Returns:
            List of (number, word) tuples
        """
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            cursor.execute(
                "SELECT number, word FROM word_mapping WHERE word LIKE %s ORDER BY word LIMIT 50",
                (pattern,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def export_to_sql(self, output_file: str = "data/word_mapping.sql"):
        """
        Export database to SQL file that can be shared and imported.
        
        Args:
            output_file: Path to output SQL file
        """
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Get all data
            cursor.execute("SELECT number, word FROM word_mapping ORDER BY number")
            rows = cursor.fetchall()
            
            # Write SQL file
            with open(output_file, 'w') as f:
                f.write("-- Word Mapping Database Export\n")
                f.write("-- Generated by DatabaseManager\n\n")
                f.write("CREATE TABLE IF NOT EXISTS word_mapping (\n")
                f.write("    id SERIAL PRIMARY KEY,\n")
                f.write("    number INTEGER UNIQUE NOT NULL,\n")
                f.write(f"    word VARCHAR({self.MAX_WORD_LENGTH}) UNIQUE NOT NULL,\n")
                f.write("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n")
                f.write(");\n\n")
                f.write("INSERT INTO word_mapping (number, word) VALUES\n")
                
                for i, (number, word) in enumerate(rows):
                    comma = "," if i < len(rows) - 1 else ";"
                    f.write(f"    ({number}, '{word}'){comma}\n")
                
                f.write("\n-- End of export\n")
            
            logger.info(f"Database exported to {output_file} ({len(rows)} words)")
            print(f"Exported {len(rows)} words to {output_file}")
        finally:
            cursor.close()
    
    def import_from_sql(self, input_file: str = "data/word_mapping.sql"):
        """
        Import database from SQL file.
        
        Args:
            input_file: Path to input SQL file
        """
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            with open(input_file, 'r') as f:
                sql_content = f.read()
            
            cursor.execute(sql_content)
            self.connection.commit()
            
            logger.info(f"Database imported from {input_file}")
            print(f"✓ Imported database from {input_file}")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error importing database: {e}")
            raise
        finally:
            cursor.close()

    def export_to_dump(self, output_file: str = "data/word_mapping.dump"):
        """
        Export database to binary dump file using pg_dump (industry standard).
        This is more efficient than SQL text files.
        
        Args:
            output_file: Path to output dump file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Build pg_dump command
            cmd = [
                'pg_dump',
                '-h', self.host,
                '-p', str(self.port),
                '-U', self.user,
                '-F', 'c',  # Custom format (compressed)
                '-f', output_file,
                self.db_name
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.password
            
            # Run pg_dump
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                file_size = os.path.getsize(output_file)
                size_mb = file_size / (1024 * 1024)
                logger.info(f"Database exported to {output_file} ({size_mb:.2f} MB)")
                print(f"Exported database to {output_file} ({size_mb:.2f} MB)")
            else:
                raise Exception(f"pg_dump failed: {result.stderr}")
                
        except FileNotFoundError:
            raise Exception(
                "pg_dump not found. Make sure PostgreSQL client tools are installed.\n"
                "Install with: sudo apt-get install postgresql-client"
            )
        except Exception as e:
            logger.error(f"Error exporting database: {e}")
            raise
    
    def import_from_dump(self, input_file: str = "data/word_mapping.dump"):
        """
        Import database from binary dump file using pg_restore (industry standard).
        
        Args:
            input_file: Path to input dump file
        """
        try:
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"Dump file not found: {input_file}")
            
            # Create database if it doesn't exist
            self.create_database()
            
            # Build pg_restore command
            cmd = [
                'pg_restore',
                '-h', self.host,
                '-p', str(self.port),
                '-U', self.user,
                '-d', self.db_name,
                '--clean',  # Clean (drop) database objects before recreating
                '--if-exists',  # Don't error if objects don't exist
                input_file
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.password
            
            # Run pg_restore
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            # pg_restore can have non-zero exit code with warnings, check stderr
            if result.returncode != 0 and "ERROR" in result.stderr:
                raise Exception(f"pg_restore failed: {result.stderr}")
            
            logger.info(f"Database imported from {input_file}")
            print(f"✓ Imported database from {input_file}")
            
        except FileNotFoundError as e:
            if 'pg_restore' in str(e):
                raise Exception(
                    "pg_restore not found. Make sure PostgreSQL client tools are installed.\n"
                    "Install with: sudo apt-get install postgresql-client"
                )
            raise
        except Exception as e:
            logger.error(f"Error importing database: {e}")
            raise

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Usage example
if __name__ == "__main__":
    db = DatabaseManager()
    db.initialize()
    
    # Export database to SQL file for sharing
    # db.export_to_sql()
    db.export_to_dump()
    # Show database info
    print(f"\nTotal words in database: {db.get_total_words()}")
    
    # View first 20 entries
    print("\nFirst 20 words:")
    for number, word in db.view_database_sample(20):
        print(f"{number}: {word}")
    
    # Search for words starting with 'cat'
    print("\nWords starting with 'cat':")
    for number, word in db.search_words('cat%'):
        print(f"{number}: {word}")
    
    # Example queries
    with db:
        word = db.get_word_by_number(1)
        print(f"\nWord for number 1: {word}")
        
        number = db.get_number_by_word("cat")
        print(f"Number for word 'cat': {number}")
