from numpy import isin
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
            self.encoder._encode_main(allergies)
    def test_empty_allergy_list(self):
        """Test encoding and decoding an empty allergy list."""
        allergies = []
        encoded = self.encoder._encode_main(allergies)
        decoded = self.encoder._decode_main(encoded)
        assert decoded == allergies
        assert encoded == 0

    def test_cereals_encoding(self):
        """Test encoding and decoding an allergy list with 'cereals containing gluten'."""
        allergies = ['cereals containing gluten']
        encoded = self.encoder._encode_main(allergies)
        decoded = self.encoder._decode_main(encoded)
        assert decoded == allergies
        assert encoded == 1 << self.encoder.lists['main'].index('cereals containing gluten')

    def test_multiple_allergies(self):
        """Test encoding and decoding multiple allergies."""
        allergies = ['cereals containing gluten', 'crustaceans']
        encoded = self.encoder._encode_main(allergies)
        decoded = self.encoder._decode_main(encoded)
        assert set(decoded) == set(allergies)
        expected_encoding = (1 << self.encoder.lists['main'].index('cereals containing gluten')|
                             1 << self.encoder.lists['main'].index('crustaceans'))
        assert encoded == expected_encoding


class TestSecondaryAllergenEncoding():
    def setup_method(self):
        self.encoder = AllergiesEncoder()
        
    def test_secondary_group_encoding_decoding(self):
        allergies = [ 'mackerel', 'salmon']
        encoded = self.encoder._encode_secondary_group(allergies)
        decoded = self.encoder._decode_secondary_group(encoded)
        assert set(decoded) == set(allergies)

    def test_ignore_encoding(self):
        allergies = ['eggs', 'milk']
        encoded = self.encoder._encode_secondary_group(allergies)
        decoded = self.encoder._decode_secondary_group(encoded)
        assert set(decoded) == set()

    def test_secondary_group_no_allergies(self):
        allergies = []
        encoded = self.encoder._encode_secondary_group(allergies)
        decoded = self.encoder._decode_secondary_group(encoded)
        assert decoded == allergies


class TestAllergiesEncoderAll():   
    def setup_method(self):
        self.encoder = AllergiesEncoder()
    def test_full_encoding_decoding(self):
        allergies = ['cereals containing gluten', 'crustaceans', 'mackerel']
        encoded = self.encoder.encode_all(allergies)
        decoded = self.encoder.decode_all(encoded)
        assert isinstance(encoded, list)
        assert set(decoded) == set(allergies)
    def test_full_encoding_decoding_no_allergies(self):
        allergies = []
        encoded = self.encoder.encode_all(allergies)
        decoded = self.encoder.decode_all(encoded)
        assert decoded == allergies

    def test_full_encoding_decoding_ignore(self):
        allergies = ['eggs', 'milk']
        encoded = self.encoder.encode_all(allergies)
        decoded = self.encoder.decode_all(encoded)
        assert decoded == self.encoder._decode_main(encoded[0])
        assert decoded ==['eggs', 'milk']
