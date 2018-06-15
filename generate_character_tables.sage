# Run this in Sage. Tested with version 8.1.
from __future__ import print_function
import csv
import re

class CharacterTableFetcher:
    def __init__(self, n_max=10):
        config = open("generate_character_tables.cfg", "r")
        line = config.read()
        config.close()
        m = re.match( r'n_max\s*[=]\s*(\d+)', line)
        self.n_max = int(m.group(int(1))) # The weird int(1) is required here because Sage will otherwise convert it to a non-int Sage-specific numerical type
        print("Calculating up to S"+str(self.n_max)+".", end=" ")
        self.precompute_character_tables()

    def precompute_character_tables(self):
        self.all_tables = {}  # Using dictionary instead of list allows indexing by correct value of n (n=0, n=1 not used)
        for i in range(2, self.n_max+1):
            self.all_tables[i]=self.get_character_table(i)
            print("S"+str(i), end=" ")
        print("")
        self.write_tables()

    def get_character_table(self, n):
        '''
        Fetches character table and some information about conjugacy classes of the symmetric group Sn.
        '''
        G=SymmetricGroup(n)

        # Sage objects
        sagecclasses = G.conjugacy_classes()
        sagereps = G.conjugacy_classes_representatives()
        sagetable = G.character_table()

        # Portable versions
        conjugacy_class_sizes = [str( cc.cardinality() ) for cc in sagecclasses]
        conjugacy_class_representatives = [self.simplify_permutation_string(str(rep)) for rep in sagereps]
        character_values = [[int(val) for val in row] for row in sagetable]

        return [conjugacy_class_sizes, conjugacy_class_representatives, character_values]

    def simplify_permutation_string(self, repstring):
        '''
        Replaces comma with nothing.
        '''
        return re.sub(r',', r'', repstring)

    def write_tables(self):
        for i in range(2, self.n_max+1):
            [conjugacy_class_sizes, conjugacy_class_representatives, character_values]= self.all_tables[i]

            with open("character_tables/characters_s"+str(i)+".csv", 'w') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(conjugacy_class_sizes)
                writer.writerow(conjugacy_class_representatives)

                for row in character_values:
                    writer.writerow([str(val) for val in row])
        print("Saved to character_tables/characters_s...csv")

ctf = CharacterTableFetcher(n_max = 10) # Change n_max for more tables, higher Sn
