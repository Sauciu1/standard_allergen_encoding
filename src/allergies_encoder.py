import numpy
import pandas as pd
from typing import Literal

class AllergiesEncoder:
    def __init__(self, which_set:Literal['main', 'extended']='main'):
        if which_set == 'main':
            allergy_df = pd.read_csv('data/main_allergies.csv')
        elif which_set == 'extended':
            allergy_df = pd.read_csv('data/extended_allergies.csv')
        else:
            raise ValueError("which_set must be either 'main' or 'extended'")
        
        self.allergen_list = allergy_df['allergen'].tolist()

    @staticmethod
    def lowercase_list(items:list[str])->list[str]:
        return [item.lower() for item in items]

    def encode_allergy(self, allergies:list[str])->int:
        encoding = 0
        for allergy in allergies:
            index = self.allergen_list.index(allergy)
            encoding |= (1 << index)

        return encoding
    
    def decode_allergy(self, encoding:int)->list[str]:
        allergies = []
        for index, allergen in enumerate(self.allergen_list):
            if encoding & (1 << index):
                allergies.append(allergen)
        
        return allergies
    

if __name__ == "__main__":
    encoder = AllergiesEncoder()
    test_allergies = ['cereals containing gluten']
    encoded = encoder.encode_allergy(test_allergies)
    print(f"Encoded: {encoded}")
    decoded = encoder.decode_allergy(encoded)
    print(f"Decoded: {decoded}")
    

