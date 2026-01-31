import numpy
import pandas as pd

class AllergiesEncoder:
    def __init__(self):
        allergy_df = pd.read_csv('data/allergies.csv')
        self.allergen_list = allergy_df['allergen'].tolist()

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
    
    def encode_allergies_batch(self, allergies_batch:list[list[str]])->numpy.ndarray: