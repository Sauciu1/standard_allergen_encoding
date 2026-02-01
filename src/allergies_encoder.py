import numpy
import pandas as pd
from typing import Literal

class AllergiesEncoder:
    def __init__(self, which_set:Literal['main', 'secondary']='main') -> None:
        main_path= 'data/allergens/main_allergens.csv'
        secondary_path = 'data/allergens/secondary_allergens.csv'

        if which_set == 'main':
            allergy_df = pd.read_csv(main_path).sort_values('id')
        elif which_set == 'secondary':
            allergy_df = pd.read_csv(secondary_path).sort_values('id')
        else:
            raise ValueError("which_set must be either 'main' or 'secondary'")
        
        self.allergen_list = self.lowercase_list(allergy_df['allergen'].tolist())

    @staticmethod
    def lowercase_list(items:list[str])->list[str]:
        return [item.lower() for item in items]

    def encode_allergy(self, allergens:list[str])->int:
        allergens = self.lowercase_list(allergens)
        encoding = 0
        for allergen in allergens:
            index = self.allergen_list.index(allergen)
            encoding |= (1 << index)
        return encoding
    
    def decode_allergy(self, encoding:int)->list[str]:
        allergens = []
        for index, allergen in enumerate(self.allergen_list):
            if encoding & (1 << index):
                allergens.append(allergen)
        return allergens
    

if __name__ == "__main__":
    encoder = AllergiesEncoder('secondary')
    test_allergens = ['Pine nut', 'Egg', 'Milk']
    encoded = encoder.encode_allergy(test_allergens)
    print(f"Encoded: {encoded}")
    decoded = encoder.decode_allergy(encoded)
    print(f"Decoded: {decoded}")
    

