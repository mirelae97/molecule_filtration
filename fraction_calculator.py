import pandas as pd
import numpy as np

def calculate_fraction(input_csv, output_csv):
    # Load the input CSV file
    df = pd.read_csv(input_csv)

    # Initialize new columns for Stark values
    df["Stark 1"] = np.nan
    df["Stark 2"] = np.nan
    df["Stark 3"] = np.nan

    for index, row in df.iterrows():
        try:
            dipole_moment = row.iloc[13]
            rotational_constant_1 = row.iloc[9]
            rotational_constant_2 = row.iloc[10]
            rotational_constant_3 = row.iloc[11]
            molecule_name = row.iloc[1]

            # Check and compute each Stark value if possible
            if pd.notna(rotational_constant_1) and rotational_constant_1 != 0:
                df.at[index, "Stark 1"] = dipole_moment**2 / rotational_constant_1
            else:
                print(f"{molecule_name} does not have a valid rotational constant 1")

            if pd.notna(rotational_constant_2) and rotational_constant_2 != 0:
                df.at[index, "Stark 2"] = dipole_moment**2 / rotational_constant_2
            else:
                print(f"{molecule_name} does not have a valid rotational constant 2")

            if pd.notna(rotational_constant_3) and rotational_constant_3 != 0:
                df.at[index, "Stark 3"] = dipole_moment**2 / rotational_constant_3
            else:
                print(f"{molecule_name} does not have a valid rotational constant 3")
        
        except Exception as e:
            print(f"Error processing row {index} ({molecule_name}): {e}")

    # Save the modified DataFrame to output CSV
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")
    print(f"Total molecules processed: {len(df)}")


input_csv = "molecule_filter_TOC/2025_05_13_change_order/5_dipole_moment.csv"
output_csv = "molecule_filter_TOC/2025_05_13_change_order/5_fraction.csv"
potato = calculate_fraction(input_csv, output_csv)
