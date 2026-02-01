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
        Uses all allergen sets (main + secondary groups).
        
        Args:
            auto_init_db: Whether to automatically initialize database if needed
        """
        self.encoder = AllergiesEncoder()  # Now uses all allergens
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
        
        logger.info("AllergiesGetter initialized with all allergen sets")
    
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
        total_words = self.db.get_total_words()
        words = []
        
        for i, encoded_number in enumerate(encoded_numbers):
            if encoded_number > total_words:
                logger.warning(
                    f"Encoded number {encoded_number} at index {i} exceeds database size ({total_words} words). "
                    f"This allergen combination cannot be represented."
                )
                words.append(None)
            else:
                word = self.db.get_word_by_number(encoded_number)
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
            number = self.db.get_number_by_word(word)
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
