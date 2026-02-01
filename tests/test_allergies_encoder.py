import pytest
from src.allergies_encoder import AllergiesEncoder

def test_initialize_main_set():
    encoder = AllergiesEncoder()
    assert 'cereals containing gluten' in encoder.lists['main']

class TestAllergiesEncoder:
    def setup_method(self):
        self.encoder = AllergiesEncoder()
        
    def test_nonexistent_allergy(self):
        allergies = ['nonexistent allergy']
        with pytest.raises(ValueError):
            self.encoder.encode_allergy(allergies)
    def test_empty_allergy_list(self):
        """Test encoding and decoding an empty allergy list."""
        allergies = []
        encoded = self.encoder.encode_allergy(allergies)
        decoded = self.encoder.decode_allergy(encoded)
        assert decoded == allergies
        assert encoded == 0

    def test_cereals_encoding(self):
        """Test encoding and decoding an allergy list with 'cereals containing gluten'."""
        allergies = ['cereals containing gluten']
        encoded = self.encoder.encode_allergy(allergies)
        decoded = self.encoder.decode_allergy(encoded)
        assert decoded == allergies
        assert encoded == 1 << self.encoder.lists['main'].index('cereals containing gluten')

    def test_multiple_allergies(self):
        """Test encoding and decoding multiple allergies."""
        allergies = ['cereals containing gluten', 'crustaceans']
        encoded = self.encoder.encode_allergy(allergies)
        decoded = self.encoder.decode_allergy(encoded)
        assert set(decoded) == set(allergies)
        expected_encoding = (1 << self.encoder.lists['main'].index('cereals containing gluten')|
                             1 << self.encoder.lists['main'].index('crustaceans'))
        assert encoded == expected_encoding
        