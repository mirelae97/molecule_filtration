import pandas as pd  

input_path = "molecule_filter_TOC/filter1_properties_no_symmetry.csv" # path where the csv is stored
df = pd.read_csv(input_path)  # load the csv as a dataframe

df_cleaned = df.drop_duplicates(subset='Formula', keep='first')

output_path = "molecule_filter_TOC/filter1_properties_no_symmetry_no_duplicates.csv"  # Replace with the desired path for the cleaned CSV file
df_cleaned.to_csv(output_path, index=False, encoding="utf-8-sig")  # `index=False` prevents pandas from writing row numbers to the CSV

