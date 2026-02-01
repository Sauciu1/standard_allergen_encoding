from typing import List, Optional
import logging
import pickle
from pathlib import Path

from allergies_encoder import AllergiesEncoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AllergiesGetter:
    """Converts between allergies and database words using encoding."""
    
    def __init__(self, auto_init_db: bool = True):
        """
        Initialize AllergiesGetter with encoder and database connection.
        Automatically falls back to dump file if PostgreSQL is unavailable.
        
        Args:
            auto_init_db: Whether to automatically initialize database if needed
        """
        self.encoder = AllergiesEncoder()
        self.db = None
        self.use_dump = False
        self.word_mapping = {}  # For dump file fallback
        
        # Try PostgreSQL first
        try:
            from db_manager import DatabaseManager
            self.db = DatabaseManager()
            
            # Initialize database if it doesn't exist or is empty
            if auto_init_db:
                try:
                    if not self.db.database_exists():
                        logger.info("Database doesn't exist, trying to load from dump...")
                        if not self._load_from_dump():
                            logger.info("Initializing new database...")
                            self.db.initialize()
                    else:
                        total_words = self.db.get_total_words()
                        if total_words == 0:
                            logger.info("Database is empty, trying to load from dump...")
                            if not self._load_from_dump():
                                logger.info("Populating database...")
                                self.db.populate_word_mapping()
                        else:
                            logger.info(f"Database ready with {total_words} words")
                except Exception as e:
                    logger.warning(f"Could not initialize database: {e}")
                    logger.info("Trying to use dump file instead...")
                    if not self._load_from_dump():
                        raise RuntimeError("Cannot initialize database or load dump file")
                    
        except ImportError as e:
            logger.warning(f"PostgreSQL not available: {e}")
            logger.info("Using database dump file instead...")
            if not self._load_from_dump():
                raise RuntimeError("Cannot load database dump file. Please ensure data/database/word_mapping.pkl exists")
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            logger.info("Falling back to database dump file...")
            if not self._load_from_dump():
                raise RuntimeError("Cannot connect to database or load dump file")
        
        if self.use_dump:
            logger.info(f"Using dump file with {len(self.word_mapping)} words")
        else:
            logger.info("Using PostgreSQL database")
    
    def _load_from_dump(self) -> bool:
        """
        Load word mapping from pickle dump file.
        
        Returns:
            True if successful, False otherwise
        """
        dump_path = Path(__file__).parent.parent / "data" / "database" / "word_mapping.pkl"
        
        if not dump_path.exists():
            logger.error(f"Dump file not found at {dump_path}")
            return False
        
        try:
            with open(dump_path, 'rb') as f:
                self.word_mapping = pickle.load(f)
            
            self.use_dump = True
            # Close any database connection
            if self.db:
                try:
                    self.db.close()
                except:
                    pass
                self.db = None
            
            logger.info(f"Loaded {len(self.word_mapping)} words from dump file")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load dump file: {e}")
            return False
    
    def get_total_words(self) -> int:
        """Get total number of words in the database or dump."""
        if self.use_dump:
            return len(self.word_mapping)
        else:
            return self.db.get_total_words()
    
    def get_word_by_number(self, number: int) -> Optional[str]:
        """Get word by its number."""
        if self.use_dump:
            return self.word_mapping.get(number)
        else:
            return self.db.get_word_by_number(number)
    
    def get_number_by_word(self, word: str) -> Optional[int]:
        """Get number by word."""
        if self.use_dump:
            # Reverse lookup in dictionary
            for num, w in self.word_mapping.items():
                if w == word:
                    return num
            return None
        else:
            return self.db.get_number_by_word(word)
    
    def allergies_to_words(self, allergens: List[str]) -> List[Optional[str]]:
        """
        Convert list of allergens to database words.
        
        Args:
            allergens: List of allergen names
            
        Returns:
            List of words from database representing the encoded allergies
        """
        # Encode allergens to list of numbers
        encoded_numbers = self.encoder.encode_all(allergens)
        
        # Check if any encoding exceeds database range
        total_words = self.get_total_words()
        words = []
        
        for i, encoded_number in enumerate(encoded_numbers):
            if encoded_number > total_words:
                logger.warning(
                    f"Encoded number {encoded_number} at index {i} exceeds database size ({total_words} words). "
                    f"This allergen combination cannot be represented."
                )
                words.append(None)
            else:
                word = self.get_word_by_number(encoded_number)
                if not word:
                    logger.warning(
                        f"No word found for number {encoded_number} at index {i}. "
                        f"Database may need to be reinitialized."
                    )
                words.append(word)
        
        return words
    
    def words_to_allergies(self, words: List[str]) -> Optional[List[str]]:
        """
        Convert list of database words to allergens.
        
        Args:
            words: List of words from database
            
        Returns:
            List of allergen names, or None if any word not found
        """
        # Get numbers from database
        numbers = []
        for word in words:
            number = self.get_number_by_word(word)
            if number is None:
                logger.warning(f"Word '{word}' not found in database")
                return None
            numbers.append(number)
        
        # Decode numbers to allergens
        allergens = self.encoder.decode_all(numbers)
        
        return allergens
    
    def phrases_list_to_combined_encoding(self, phrases_list: List[List[str]], method: str ='union')->Optional[List[int]]:
        """
        Combine multiple lists of allergen phrases into a single encoding.
        
        Args:
            phrases_list: List of lists of allergen phrases
            method: 'union' or 'intersection' to combine encodings
            
        Returns:
            Combined encoding as list of integers, or None if any error
        """
        encodings = []
        for phrases in phrases_list:
            try:
                encoding = self.encoder.encode_all(phrases)
                encodings.append(encoding)
            except ValueError as e:
                logger.warning(f"Error encoding phrases {phrases}: {e}")
                return None
        
        combined_encoding = self.encoder.combine_lists_of_encodings(encodings, method=method)
        return combined_encoding
    
    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Usage examples
if __name__ == "__main__":
    # Example 1: Convert allergens to words
    print("=" * 50)
    print("Example 1: Allergens to Words")
    print("=" * 50)
    
    with AllergiesGetter() as getter:
        test_allergens = ['Peanuts', 'Eggs', 'Milk', 'Pine nut', 'Tuna']
        print(f"\nAllergens: {test_allergens}")
        
        words = getter.allergies_to_words(test_allergens)
        print(f"Encoded to words: {words}")
    
    print("\n" + "=" * 50)
    print("Example 2: Words to Allergens")
    print("=" * 50)
    
    with AllergiesGetter() as getter:
        if words and all(w is not None for w in words):
            print(f"\nWords: {words}")
            allergens = getter.words_to_allergies(words)
            print(f"Decoded to allergens: {allergens}")
    
    print("\n" + "=" * 50)
    print("Example 3: Empty allergen list (should be 'none')")
    print("=" * 50)
    
    with AllergiesGetter() as getter:
        empty_allergens = []
        words = getter.allergies_to_words(empty_allergens)
        print(f"\nEmpty allergens -> words: {words}")
        print(f"First word is 'none': {words[0] == 'none'}")
    
    # example 4: list of phrases to combined encoding
    print("\n" + "=" * 50)
    print("Example 4: Combine multiple allergen phrase lists")
    print("=" * 50)

    #test adding allergies together from different lists
    with AllergiesGetter() as getter:
        phrases_list = [
            ['Peanuts', 'Eggs'],
            ['Milk', 'Pine nut'],
            ['Tuna', 'Fish']
        ]

        all_phrases = set()
        for phrases in phrases_list:
            all_phrases.update(phrases)
        all_phrases = list(all_phrases)
        direct_encoding = getter.encoder.encode_all(all_phrases)
        print(f"\nDirect Encoding of all phrases: {direct_encoding}")

        #additional check using phrases of different sizes
        phrases_list_varied = [
            ['Peanuts', 'Eggs', 'Milk'],
            ['Pine nut'],
            ['Tuna', 'Fish', 'Celery']
        ]

        all_phrases_varied = set()
        for phrases in phrases_list_varied:
            all_phrases_varied.update(phrases)
        all_phrases_varied = list(all_phrases_varied)
        direct_encoding_varied = getter.encoder.encode_all(all_phrases_varied)
        print(f"\nDirect Encoding of varied phrases: {direct_encoding_varied}")
        # show the decoded allergens from direct encoding
        decoded_direct = getter.encoder.decode_all(direct_encoding_varied)
        print(f"Decoded from direct encoding: {decoded_direct}")
