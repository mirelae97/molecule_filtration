import pandas as pd
import time
import pandas as pd
import re

def calculate_number_of_atoms(formula):
    if not formula:
        return 0
    
    # Function to process a formula and return atom count
    def parse_formula(formula):
        if not formula:
            return 0
            
        total_atoms = 0
        i = 0
        
        while i < len(formula):
            # Handle parentheses
            if formula[i] == '(':
                # Find the matching closing parenthesis
                level = 1
                j = i + 1
                while j < len(formula) and level > 0:
                    if formula[j] == '(':
                        level += 1
                    elif formula[j] == ')':
                        level -= 1
                    j += 1
                
                if level == 0:
                    # Process the content inside parentheses
                    inner_content = formula[i+1:j-1]
                    inner_atoms = parse_formula(inner_content)
                    
                    # Look for a multiplier after the closing parenthesis
                    multiplier = 1
                    k = j
                    while k < len(formula) and (formula[k].isdigit() or formula[k] == '.'):
                        k += 1
                    
                    if k > j:
                        try:
                            multiplier = float(formula[j:k])
                        except ValueError:
                            pass
                    
                    total_atoms += inner_atoms * multiplier
                    i = k
                else:
                    # Unmatched parenthesis, skip it
                    i += 1
            
            # Handle elements (starting with uppercase letter)
            elif formula[i].isupper():
                # Look for the next non-lowercase letter or special character
                j = i + 1
                while j < len(formula) and formula[j].islower():
                    j += 1
                
                # Look for a number after the element
                multiplier = 1
                k = j
                while k < len(formula) and (formula[k].isdigit() or formula[k] == '.'):
                    k += 1
                
                if k > j:
                    try:
                        multiplier = float(formula[j:k])
                    except ValueError:
                        pass
                
                total_atoms += multiplier
                i = k if k > j else j
            else:
                # Skip other characters
                i += 1
        
        return total_atoms
    
    return parse_formula(formula)

def process_csv(input_csv, output_csv_1_5, output_csv_5_10, output_csv_10_more, delay=1):
    df = pd.read_csv(input_csv)
    
    filtered_molecules_1_5 = []
    filtered_molecules_5_10 = []
    filtered_molecules_10_more = []
    
    for index, row in df.iterrows():
        chem_name = row.iloc[3]
        print(f"Checking number of atoms for {chem_name}")
        
        try: 
            num_atoms = calculate_number_of_atoms(chem_name)
            print(f"{chem_name}: {num_atoms} atoms")
            
            if num_atoms > 0 and num_atoms < 6:
                filtered_molecules_1_5.append(row)
            if num_atoms > 5 and num_atoms < 11:
                filtered_molecules_5_10.append(row)
            if num_atoms > 10:
                filtered_molecules_10_more.append(row)
                
        except Exception as e:
            print(f"Error processing {chem_name}: {e}")
    
    # create a new DataFrame with filtered molecules
    filtered_df_1_5 = pd.DataFrame(filtered_molecules_1_5)
    filtered_df_5_10 = pd.DataFrame(filtered_molecules_5_10)
    filtered_df_10_more = pd.DataFrame(filtered_molecules_10_more)
    
    # converts the dataframe to a csv
    filtered_df_1_5.to_csv(output_csv_1_5, index=False)
    filtered_df_5_10.to_csv(output_csv_5_10, index=False)
    filtered_df_10_more.to_csv(output_csv_10_more, index=False)
    
    # user notification
    print(f"Total molecules processed: {len(df)}")
    print(f"Molecules passing with 1-5 atoms: {len(filtered_molecules_1_5)}")
    print(f"Molecules with 5-10 atoms: {len(filtered_molecules_5_10)}")
    print(f"Molecules with more than 10 atoms: {len(filtered_molecules_10_more)}")

# Test the function
test_formulas = [
    "N(CH3)3",
    "C(NH2)H2C(CH3)HCH3",
    "CH3C(OH)=NH",
    "H2O",
    "CH4"
]

for formula in test_formulas:
    atoms = calculate_number_of_atoms(formula)
    print(f"{formula}: {atoms} atoms")

# Example usage
# process_csv("molecule_filter_TOC/no_symmetry_restriction/after_quadrupole_and_dipole.csv", 
#             'molecule_filter_TOC/no_symmetry_restriction/filter3_atoms_1_5.csv', 
#             "molecule_filter_TOC/no_symmetry_restriction/filter3_atoms_5_10.csv",
#             "molecule_filter_TOC/no_symmetry_restriction/filter3_atoms_10_more.csv")



# Example usage
process_csv("molecule_filter_TOC/no_symmetry_restriction/after_quadrupole_and_dipole.csv", 'molecule_filter_TOC/no_symmetry_restriction/filter3_atoms_1_5.csv', "molecule_filter_TOC/no_symmetry_restriction/filter3_atoms_5_10.csv","molecule_filter_TOC/no_symmetry_restriction/filter3_atoms_10_more.csv")