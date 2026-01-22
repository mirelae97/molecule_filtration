import pandas as pd
import numpy as np
import os

def analyze_molecular_shapes(file_path):
    """
    Analyzes molecular shapes based on values in columns 9, 10, and 11.
    - If two equal values are smaller than the third value: prolate
    - If two equal values are larger than the third value: oblate
    - If two values are 0 (or nearly 0) and one is non-zero: linear
    
    Args:
        file_path: Path to the Excel file
    
    Returns:
        Three dataframes: prolates, oblates, and linears
    """
    # Try to detect file extension to handle both Excel and CSV files
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    elif file_extension.lower() == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")
    
    # Get the actual column names or indices
    if len(df.columns) >= 12:  # Make sure we have enough columns
        # Use direct 0-based indices as specified
        col1 = 9   # 10th column (0-indexed)
        col2 = 10  # 11th column (0-indexed)
        col3 = 11  # 12th column (0-indexed)
    else:
        raise ValueError(f"The file does not have enough columns. It has {len(df.columns)} columns, but we need at least 12.")
    
    # Create empty lists to store results
    prolates = []
    oblates = []
    linears = []
    
    # Define a small threshold for considering values as nearly equal or nearly zero
    epsilon = 1e-10
    
    # Analyze each row
    for index, row in df.iterrows():
        # Get the three values
        val1 = row[col1]
        val2 = row[col2]
        val3 = row[col3]
        
        # Check for linear molecules (only column 9 has a value, columns 10 and 11 are empty or NaN)
        if pd.notna(val1) and (pd.isna(val2) or val2 == '') and (pd.isna(val3) or val3 == ''):
            linears.append(row)
            continue
        
        # For non-linear molecules, ensure all values are valid numbers
        if pd.isna(val1) or pd.isna(val2) or pd.isna(val3):
            continue
            
        # Check if any two values are equal
        if abs(val1 - val2) < epsilon:
            equal_value = val1
            third_value = val3
        elif abs(val1 - val3) < epsilon:
            equal_value = val1
            third_value = val2
        elif abs(val2 - val3) < epsilon:
            equal_value = val2
            third_value = val1
        else:
            # If all values are different, skip this row or handle differently
            continue
        
        # Determine shape based on comparison
        if equal_value < third_value:
            prolates.append(row)
        else:  # equal_value > third_value
            oblates.append(row)
    
    # Convert lists to dataframes
    prolates_df = pd.DataFrame(prolates)
    oblates_df = pd.DataFrame(oblates)
    linears_df = pd.DataFrame(linears)
    
    return prolates_df, oblates_df, linears_df

def save_results(prolates_df, oblates_df, linears_df):
    """
    Saves the results to CSV files
    
    Args:
        prolates_df: DataFrame containing prolate molecules
        oblates_df: DataFrame containing oblate molecules
        linears_df: DataFrame containing linear molecules
        output_dir: Directory to save the output files
    """
    # Create the output directory if it doesn't exist
    
    # Define file paths
    prolates_path = "molecule_filter_TOC/2025_05_13_change_order/5_prolate.csv"
    oblates_path = "molecule_filter_TOC/2025_05_13_change_order/5_oblate.csv"
    linears_path = "molecule_filter_TOC/2025_05_13_change_order/5_linear.csv"
    prolate_linear_path = "molecule_filter_TOC/2025_05_13_change_order/5_prolate_and_linear.csv"
    
    # Save individual files
    prolates_df.to_csv(prolates_path, index=False)
    oblates_df.to_csv(oblates_path, index=False)
    linears_df.to_csv(linears_path, index=False)
    
    # Combine prolates and linears
    prolate_linear_df = pd.concat([prolates_df, linears_df])
    prolate_linear_df.to_csv(prolate_linear_path, index=False)
    
    print(f"Saved prolate molecules to: {prolates_path}")
    print(f"Saved oblate molecules to: {oblates_path}")
    print(f"Saved linear molecules to: {linears_path}")
    print(f"Saved prolate and linear molecules to: {prolate_linear_path}")
    print(f"Found {len(prolates_df)} prolate molecules, {len(oblates_df)} oblate molecules, and {len(linears_df)} linear molecules.")

def main(file_path):
    
    try:
        prolates_df, oblates_df, linears_df = analyze_molecular_shapes(file_path)
        
        # Save results
        save_results(prolates_df, oblates_df, linears_df)
        
        print("\nAnalysis complete!")
        
    except Exception as e:
        print(f"An error occurred: {e}")



file_path = "molecule_filter_TOC/2025_05_13_change_order/5_rotational_constants_with_average.csv"
main(file_path)