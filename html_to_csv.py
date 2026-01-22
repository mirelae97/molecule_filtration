import os
import pandas as pd
from bs4 import BeautifulSoup

# Path to the saved HTML file
html_file = "C:/Users/mirela_en/Desktop/python/molecule_filter/nist_data_extraction_after_misha/saved_page.html.html"  # Ensure you save the webpage as 'saved_page.html'

if not os.path.exists(html_file):
    print(f"Error: {html_file} not found. Please save the webpage and try again.")
    exit()

# Read the HTML content
with open(html_file, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Find the table
table = soup.find("table", {"border": "1"})

# Extract table headers
headers = [header.get_text(strip=True) for header in table.find_all("th")]

# Extract table rows
rows = []
for row in table.find_all("tr"):
    cols = row.find_all("td")
    if cols:  # Only process non-empty rows
        cols = [col.get_text(strip=True) if not col.find("a") else col.find("a").get_text(strip=True) for col in cols]
        rows.append(cols)

# Create a DataFrame
df = pd.DataFrame(rows, columns=headers)

# Remove any empty rows if necessary
df = df.dropna(how='all')

# Display the first few rows
print(df.head())

# Save to CSV
output_filename = "vibrational_frequencies.csv"
df.to_csv(output_filename, index=False)
print(f"Data saved to {output_filename}")