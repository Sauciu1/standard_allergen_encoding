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

        self.all_list = self.lowercase_list(list(numpy.concatenate(list(self.lists.values()))))
        
    @staticmethod
    def lowercase_list(items:list[str])->list[str]:
        return [item.lower() for item in items]
    

    def __encode(self, active_list, ref_list)->int:
        encoding = 0
        for allergen in active_list:
            if allergen not in ref_list:
                continue

            index = ref_list.index(allergen)
            encoding |= (1 << index)
        return encoding

    def _encode_main(self, allergens:list[str])->int:
        allergens = self.lowercase_list(allergens)
        return self.__encode(allergens, self.lists['main'])

    def __decode_main(self, encoding:int, ref_list):
        output_list = []
        for index, allergen in enumerate(ref_list):
            if encoding & (1 << index):
                output_list.append(allergen)
        return output_list
    
    def _decode_main(self, encoding:int)->list[str]:
        return self.__decode_main(encoding, self.lists['main'])
    

    def _encode_secondary_group(self, allergens:list[str])->list[int]:
        allergens = self.lowercase_list(allergens)
        allergen_subgroups = {}
        for group, allergen_list in self.lists.items():
            if group == 'main':
                continue
            for allergen in allergens:
                if allergen in allergen_list:
                    allergen_subgroups[group] = allergen_subgroups.get(group,set())| {allergen}
  

        ref_list =[0,1,2,3,4,5]
        map_encode = self.__encode(list(allergen_subgroups.keys()), ref_list)
        group_5 = allergen_subgroups.pop(5, None)
        if group_5:
            map_encode |= (self.__encode(list(group_5), self.lists[5]) << 6)
        subgroup_encodes = [self.__encode(list(allergen_subgroups[group]), self.lists[group]) for group in allergen_subgroups]
        return [map_encode, *subgroup_encodes]
    

    def _decode_secondary_group(self, encodings:list[int])->list[str]:
        ref_list = [0, 1, 2, 3, 4, 5]

        map_encode = encodings[0]
        group_5_encoding = map_encode >> 6
        map_encode_lower = map_encode & 0b11111  # Keep only lower 5 bits

        group_map = self.__decode_main(map_encode_lower, ref_list)
        decoded_allergens = []
        
        for i, group in enumerate(group_map):
            subgroup_encoding = encodings[i + 1]
            decoded_allergens.extend(self.__decode_main(subgroup_encoding, self.lists[group]))
        
        # Decode group 5 from upper bits if present
        if group_5_encoding:
            decoded_allergens.extend(self.__decode_main(group_5_encoding, self.lists[5]))
        
        return decoded_allergens
    

    def encode_all(self, allergens:list[str])->list[int]:
        allergens = self.lowercase_list(allergens)
        for allergen in allergens:
            if allergen not in self.all_list:
                raise ValueError(f"Allergen '{allergen}' not recognized.")

        main=  self._encode_main(allergens)
        secondary = self._encode_secondary_group(allergens)
        return [main, *secondary]
    
    def decode_all(self, encodings:list[int])->list[str]:
        main = self._decode_main(encodings[0])
        secondary = self._decode_secondary_group(encodings[1:])
        return [*main, *secondary]
    
       
    
if __name__ == "__main__":
    encoder = AllergiesEncoder()
    test_allergens = ['Pine nut', 'eggs', 'Milk', 'peanuts', 'tuna']
    encoded = encoder.encode_all(test_allergens)
    print("Encoded:", encoded)
    decoded = encoder.decode_all(encoded)
    print("Decoded:", decoded)



