from typing import List, Optional
import logging
from allergies_encoder import AllergiesEncoder
from db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AllergiesGetter:
    """Converts between allergies and database words using encoding."""
    
    def __init__(self, auto_init_db: bool = True):
        """
        Initialize AllergiesGetter with encoder and database connection.
        Uses the 'main' allergen set only.
        
        Args:
            auto_init_db: Whether to automatically initialize database if needed
        """
        self.encoder = AllergiesEncoder('main')
        self.db = DatabaseManager()
        
        # Initialize database if it doesn't exist or is empty
        if auto_init_db:
            try:
                # Check if database has data
                if not self.db.database_exists():
                    logger.info("Database doesn't exist, initializing...")
                    self.db.initialize()
                else:
                    # Database exists, but check if it has data
                    total_words = self.db.get_total_words()
                    if total_words == 0:
                        logger.info("Database is empty, populating...")
                        self.db.populate_word_mapping()
                    else:
                        logger.info(f"Database ready with {total_words} words")
            except Exception as e:
                logger.warning(f"Could not auto-initialize database: {e}")
                logger.warning("You may need to run: uv run src/db_manager.py")
        
        logger.info("AllergiesGetter initialized with 'main' allergen set")
    
    def allergies_to_word(self, allergens: List[str]) -> Optional[str]:
        """
        Convert list of allergens to a database word.
        
        Args:
            allergens: List of allergen names
            
        Returns:
            Word from database representing the encoded allergies, or None if not found
        """
        # Encode allergens to number
        encoded_number = self.encoder._encode_main(allergens)
        
        # Check if encoding is within database range
        total_words = self.db.get_total_words()
        if encoded_number > total_words:
            logger.warning(
                f"Encoded number {encoded_number} exceeds database size ({total_words} words). "
                f"This allergen combination cannot be represented."
            )
            return None
        
        # Get word from database
        word = self.db.get_word_by_number(encoded_number)
        
        if not word:
            logger.warning(
                f"No word found for number {encoded_number}. "
                f"Database may need to be reinitialized."
            )
        
        return word
    
    def word_to_allergies(self, word: str) -> Optional[List[str]]:
        """
        Convert database word to list of allergens.
        
        Args:
            word: Word from database
            
        Returns:
            List of allergen names, or None if word not found
        """
        # Get number from database
        number = self.db.get_number_by_word(word)
        
        if number is None:
            # logger.warning(f"Word '{word}' not found in database")
            return None
        
        # logger.info(f"Mapped word '{word}' to number: {number}")
        
        # Decode number to allergens
        allergens = self.encoder._decode_allergy(number)
        # logger.info(f"Decoded number {number} to allergens: {allergens}")
        
        return allergens
    
    def get_word_for_encoding(self, encoding: int) -> Optional[str]:
        """
        Get database word directly from an encoding number.
        
        Args:
            encoding: Pre-encoded allergen number
            
        Returns:
            Word from database, or None if not found
        """
        return self.db.get_word_by_number(encoding)
    
    def get_encoding_for_word(self, word: str) -> Optional[int]:
        """
        Get encoding number directly from a database word.
        
        Args:
            word: Word from database
            
        Returns:
            Encoded allergen number, or None if not found
        """
        return self.db.get_number_by_word(word)
    
    def close(self):
        """Close database connection."""
        self.db.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Usage examples
if __name__ == "__main__":
    # Example 1: Convert allergens to word
    print("=" * 50)
    print("Example 1: Allergens to Word")
    print("=" * 50)
    
    with AllergiesGetter() as getter:
        test_allergens = ['Peanuts', 'Eggs', 'Milk']
        print(f"\nAllergens: {test_allergens}")
        
        word = getter.allergies_to_word(test_allergens)
        print(f"Encoded to word: {word}")
    
    print("\n" + "=" * 50)
    print("Example 2: Word to Allergens")
    print("=" * 50)
    
    with AllergiesGetter() as getter:
        # Use the word we just got (or any word from database)
        if word:
            print(f"\nWord: {word}")
            allergens = getter.word_to_allergies(word)
            print(f"Decoded to allergens: {allergens}")
        else:
            # Try with a common word
            test_word = "the"
            print(f"\nWord: {test_word}")
            allergens = getter.word_to_allergies(test_word)
            print(f"Decoded to allergens: {allergens}")
    
    print("\n" + "=" * 50)
    print("Example 3: Direct encoding conversion")
    print("=" * 50)
    
    with AllergiesGetter() as getter:
        # Directly convert encoding to word
        encoding = 42
        word = getter.get_word_for_encoding(encoding)
        print(f"\nEncoding {encoding} -> Word: {word}")
        
        # Convert back
        if word:
            number = getter.get_encoding_for_word(word)
            print(f"Word '{word}' -> Encoding: {number}")
    
    print("\n" + "=" * 50)
    print("Example 4: Multiple allergen combinations")
    print("=" * 50)
    
    with AllergiesGetter() as getter:
        test_cases = [
            ['Peanuts'],
            ['Peanuts', 'nuts'],
            ['Milk', 'Eggs'],
            ['Fish', 'crustaceans', 'Soybeans'],
        ]
        
        for allergens in test_cases:
            word = getter.allergies_to_word(allergens)
            print(f"\n{allergens} -> {word}")
            if word:
                decoded = getter.word_to_allergies(word)
                print(f"  Roundtrip: {decoded}")
