import csv
import re

def search_point_group(input_file, input_database, output_csv):
    
    # Read input file (input data)
    with open(input_file, "r", newline="", encoding="utf-8-sig") as input:
        reader_input = csv.reader(input, delimiter=",")
        input_rows = list(reader_input)  # Read all input rows into a list
    
    # Read database file (point group data)
    with open(input_database, "r", newline="", encoding="utf-8-sig") as input_database:
        reader_database = csv.reader(input_database, delimiter=",")
        database_rows = list(reader_database)  # Read all database rows into a list
    
    # Create a dictionary for point groups based on molecule
    point_group_dict = {}
    # Skip header row of database
    for row_database in database_rows[1:]:
        molecule_database = row_database[2]  # Neutral Name is at index 2
        point_group = row_database[0] # Point group is at index 0 
        point_group_dict[molecule_database] = point_group
    
    # Prepare output rows with point groups
    output_rows = []
    
    # Handle header row separately
    header_row = input_rows[0] + ["Point Group"]  # Add proper column name
    output_rows.append(header_row)
    
    # Process data rows and filter based on point group requirements
    for row_input in input_rows[1:]:  # Skip header row
        molecule_input = row_input[2]  # Assuming the molecule name is in column 2 (index 2)
        
        # Find the corresponding point group in the database
        point_group = point_group_dict.get(molecule_input, "No Point Group Found")
        
        # Only include molecules with qualifying point groups
        if is_qualifying_point_group(point_group):
            row_with_point_group = row_input.copy()  # Create a copy to avoid modifying the original
            row_with_point_group.append(point_group)
            output_rows.append(row_with_point_group)
    
    # Write output to CSV
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as output:
        writer_output = csv.writer(output)
        writer_output.writerows(output_rows)

def is_qualifying_point_group(point_group):
    """
    Check if the point group qualifies for the filter:
    - C3 or higher (C3, C4, C5, ...)
    - C3v or higher (C3v, C4v, C5v, ...)
    - C∞ (C-infinity)
    - C∞v (C-infinity-v)
    """
    try:
        # Default to False if point group is None or not a string
        if not point_group or not isinstance(point_group, str):
            return False
            
        # Normalize point group string
        pg = point_group.strip()
        
        # Check for C3 or higher
        cn_match = re.match(r'^C(\d+)$', pg)
        if cn_match and int(cn_match.group(1)) >= 3:
            return True
            
        # Check for C3v or higher
        cnv_match = re.match(r'^C(\d+)v$', pg)
        if cnv_match and int(cnv_match.group(1)) >= 3:
            return True
            
        # Check for C∞ variants
        if pg == "C∞" or pg.lower() == "cinf" or pg.lower() == "cinfty" or pg.lower() == "c_inf":
            return True
            
        # Check for C∞v variants
        if pg == "C∞v" or pg.lower() == "cinfv" or pg.lower() == "cinftyv" or pg.lower() == "c_inf_v":
            return True
            
        # Check for any other infinity notation
        if pg.startswith("C") and ("inf" in pg.lower() or "∞" in pg):
            if pg.endswith("v") or "v" in pg.lower()[-2:]:  # C∞v case
                return True
            else:  # C∞ case
                return True
                
        return False
        
    except Exception:
        # If any error occurs, default to False
        return False

if __name__ == "__main__":
    input_file_name = "molecule_filter_TOC/2025_05_13_change_order/2_filtered_for_duplicated_vibrations.csv"
    input_database_file_name = "molecule_filter_TOC/2025_05_13_change_order/point_groups_from_cccbdb.csv"
    output_file_name = "molecule_filter_TOC/2025_05_13_change_order/3_filtered_with_point_group.csv"
    search_point_group(input_file_name, input_database_file_name, output_file_name)