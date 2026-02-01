import numpy
import pandas as pd
from typing import Literal

class AllergiesEncoder:
    def __init__(self) -> None:
        main_path= 'data/allergens/main_allergens.csv'
        secondary_path = 'data/allergens/secondary_allergens.csv'
        main_df = pd.read_csv(main_path).sort_values('id')
        secondary_df = pd.read_csv(secondary_path).sort_values('id')

        main_list = self.lowercase_list(main_df['allergen'].tolist())

        self.lists = {'main': main_list}
        for group in secondary_df['group_id'].unique():
            group_df = secondary_df[secondary_df['group_id'] == group]
            group_list = self.lowercase_list(group_df['allergen'].tolist())
            self.lists[group] = group_list


        
    @staticmethod
    def lowercase_list(items:list[str])->list[str]:
        return [item.lower() for item in items]
    

    def _encode(self, active_list, ref_list)->int:
        encoding = 0
        for allergen in active_list:
            index = ref_list.index(allergen)
            encoding |= (1 << index)
        return encoding

    def encode_allergy(self, allergens:list[str], list_set:Literal['main', 'secondary']='main')->int:
        allergens = self.lowercase_list(allergens)
       
        return self._encode(allergens, self.lists[list_set])

    def _decode(self, encoding:int, ref_list):
        output_list = []
        for index, allergen in enumerate(ref_list):
            if encoding & (1 << index):
                output_list.append(allergen)
        return output_list
    
    def decode_allergy(self, encoding:int, list_set:Literal['main', 'secondary']='main')->list[str]:
        return self._decode(encoding, self.lists[list_set])
    

    def encode_secondary_group(self, allergens:list[str])->list[int]:
        allergens = self.lowercase_list(allergens)
        allergen_subgroups = {}
        
        for group, allergen_list in self.lists.items():

            if group == 'main':
                continue
            for allergen in allergens:
                if allergen in allergen_list:
                    allergen_subgroups[group] = allergen_subgroups.get(group,set())| {allergen}
        print(allergen_subgroups)

        ref_list =[0,1,2,3,4,5]

        map_encode = self._encode(list(allergen_subgroups.keys()), ref_list)

        subgroup_encodes = [self._encode(list(allergen_subgroups[group]), self.lists[group]) for group in allergen_subgroups]

        return [map_encode, *subgroup_encodes]
    

    def decode_secondary_group(self, encodings:list[int])->list[str]:
        ref_list =[0,1,2,3,4,5]
        group_map = self._decode(encodings[0], ref_list)
        decoded_allergens = []
        for i, group in enumerate(group_map):
            subgroup_encoding = encodings[i+1]
            decoded_allergens.extend(self._decode(subgroup_encoding, self.lists[group]))
        return decoded_allergens
    



if __name__ == "__main__":
    encoder = AllergiesEncoder()
    test_allergens = ['Pine nut', 'eggs', 'Milk']
    encoded = encoder.encode_secondary_group(test_allergens)
    print("Encoded:", encoded)
    decoded = encoder.decode_secondary_group(encoded)
    print("Decoded:", decoded)

    

