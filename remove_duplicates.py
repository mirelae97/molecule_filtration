import pandas as pd
import csv
import sys

def compare_csv_files(file1_path, file2_path, output_path, file1_col_idx=0, file2_col_idx=1):
    """
    Compare specific columns from two CSV files and create a new CSV file with terms
    that are not common to both files, indicating the source file for each term.
    
    Args:
        file1_path (str): Path to the first CSV file
        file2_path (str): Path to the second CSV file
        output_path (str): Path to save the output CSV file
        file1_col_idx (int): Column index to compare from first file (0-based)
        file2_col_idx (int): Column index to compare from second file (0-based)
    """
    try:
        # Read the specified column from each file
        df1 = pd.read_csv(file1_path, usecols=[file1_col_idx], header=None)
        df2 = pd.read_csv(file2_path, usecols=[file2_col_idx], header=None)
        
        # Get column names
        col_name1 = file1_col_idx if len(df1.columns) > 0 else 0
        col_name2 = file2_col_idx if len(df2.columns) > 0 else 0
        
        # Extract the values as sets for easier comparison
        terms1 = set(df1[col_name1].astype(str))
        terms2 = set(df2[col_name2].astype(str))
        
        # Find terms unique to each file
        unique_to_file1 = terms1 - terms2
        unique_to_file2 = terms2 - terms1
        
        # Create a new DataFrame for the output
        result_data = []
        
        # Add terms unique to file 1
        for term in unique_to_file1:
            result_data.append([term, "File 1", "Not present"])
            
        # Add terms unique to file 2
        for term in unique_to_file2:
            result_data.append([term, "Not present", "File 2"])
        
        # Sort results alphabetically by term
        result_data.sort(key=lambda x: x[0])
        
        # Create the result DataFrame
        result_df = pd.DataFrame(result_data, columns=["Term", "Present in File 1", "Present in File 2"])
        
        # Write to the output file
        result_df.to_csv(output_path, index=False)
        
        print(f"Comparison complete. Results saved to {output_path}")
        print(f"Found {len(unique_to_file1)} terms unique to file 1 and {len(unique_to_file2)} terms unique to file 2.")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

# Hardcoded file paths for your specific case
file1_path = "molecule_filter_TOC/2025_05_13_change_order/6_quadrupole_good_passed.csv"
file2_path = "molecule_filter_TOC/2025_05_13_change_order/old_7_filter_by_fraction.csv"
output_path = "molecule_filter_TOC/2025_05_13_change_order/6_comparison_with_before.csv"

# Compare column 0 (first column) from file1 with column 1 (second column) from file2
compare_csv_files(file1_path, file2_path, output_path, file1_col_idx=2, file2_col_idx=1)