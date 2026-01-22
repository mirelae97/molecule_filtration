import csv

# Path to the CSV file
csv_path = "C:/Users/mirela_en/Desktop/python/molecule_filter/nist_data_extraction_after_misha/vibrational_frequencies.csv"
output_path = "C:/Users/mirela_en/Desktop/python/molecule_filter/nist_data_extraction_after_misha/filtered_vibrational_frequencies.csv"

# Reading the CSV file and filtering the data
with open(csv_path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # Get the header row
    filtered_data = []
    
    for row in reader:
        # Apply the filter conditions
        # Check if the second column doesn't contain "anion", "cation", "radical", "-" or "+" in the third column,
        # and if the fifth column contains "Σ", and if the sixth column is not "0"
        if (not ("anion" in row[1] or "cation" in row[1] or "radical" in row[1] or "-" in row[2] or "+" in row[2])) \
           and ("Σ" in row[4]): 
            filtered_data.append(row)

# Write the filtered data to a new CSV file
with open(output_path, mode='w', newline='', encoding='utf-8') as f_out:
    writer = csv.writer(f_out)
    writer.writerow(header)  # Write the header row
    writer.writerows(filtered_data)  # Write the filtered data rows

print(f"Filtered data has been saved to {output_path}")
