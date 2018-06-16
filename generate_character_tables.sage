# To be run in Sage. Tested with version 8.1.
import csv
import re
from subprocess import call

class CharacterTableFetcher:
    def __init__(self):
        sage.repl.load.load("generate_character_tables_config.py",globals())
        self.n = current_n
        print("Calculating S"+str(self.n)+" characters.")
        self.precompute_character_table()

    def precompute_character_table(self):
        self.current_table = self.get_character_table(self.n)
        self.write_table()

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
        Replaces comma with space.
        '''
        return re.sub(r',', r' ', repstring)

    def write_table(self):
        [conjugacy_class_sizes, conjugacy_class_representatives, character_values] = self.current_table

        with open("character_tables/s"+str(self.n)+".csv", 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(conjugacy_class_sizes)
            writer.writerow(conjugacy_class_representatives)

            for row in character_values:
                writer.writerow([str(val) for val in row])
        print("Saved to character_tables/s"+ str(self.n)+".csv")

ctf = CharacterTableFetcher()



