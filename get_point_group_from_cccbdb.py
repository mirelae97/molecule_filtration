import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import csv

def clean_html(input_string):
    """Remove HTML tags from input string."""
    # Ensure the input is a string (in case it's a BeautifulSoup Tag object)
    if not isinstance(input_string, str):
        input_string = str(input_string)
    
    # Remove all HTML tags using regular expression
    cleaned_text = re.sub(r'<[^>]*>', '', input_string)
    return cleaned_text


def get_point_groups():
    """Fetch the point groups from the given URL and store them in a CSV."""
    url = 'https://cccbdb.nist.gov/pglistx.asp'  # URL of the webpage containing the table

    # Fetch the webpage content
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        html_content = response.text
        print(f"Successfully fetched webpage: {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {e}")
        exit(1)

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialize a list to store our data
    molecules_data = []

    # Process each row in the table
    rows = soup.find_all('tr', class_=["palegreenback", "whiteback"])
    for row in rows:
        cells = row.find_all('td')
        if not cells:  # Skip header or empty rows
            continue
        size = len(cells)

        # Extracting Point Group, Formula, Name (Neutral)
        point_group_cell = cells[0]
        formula = cells[1]
        clean_formula = clean_html(formula)
        name = cells[2]
        clean_name = clean_html(name)

        # Initialize variables for anion and cation
        clean_formula_anion = clean_name_anion = None
        clean_formula_cation = clean_name_cation = None

        # Handle cases where formula contains "+" or "-"
        if clean_formula and "+" in clean_formula:
            clean_formula_cation = clean_formula
            clean_formula = None
            clean_name_cation = clean_name
            clean_name = None
        
        if clean_formula and "-" in clean_formula:
            clean_formula_anion = clean_formula
            clean_formula = None
            clean_name_anion = clean_name
            clean_name = None

        # Handling the special format for C∞v
        if point_group_cell.find('sub') and '&infin;' in point_group_cell.find('sub').text:
            point_group = "C∞v"
        else:
            point_group = point_group_cell.get_text(strip=True)

        # Handling Anion (if present)
        if size > 3 and size <= 5:
            formula_anion = cells[3]
            clean_formula_anion = clean_html(formula_anion)
            name_anion = cells[4]
            clean_name_anion = clean_html(name_anion)

        # Handling Cation (if present)
        if size > 5:
            formula_cation = cells[5]
            clean_formula_cation = clean_html(formula_cation)
            name_cation = cells[6]
            clean_name_cation = clean_html(name_cation)

        # Add the collected data to the list
        molecules_data.append({
            'Point Group': point_group,
            'Neutral Formula': clean_formula,
            'Neutral Name': clean_name,
            'Formula Anion': clean_formula_anion,
            'Name Anion': clean_name_anion,
            'Formula Cation': clean_formula_cation,
            'Name Cation': clean_name_cation,
        })

        

    # Create a DataFrame
    df = pd.DataFrame(molecules_data)

    # Save to CSV with utf-8-sig encoding
    csv_filename = 'molecule_filter_TOC/no_symmetry_restriction/csv_files/all_point_groups.csv'
    with open(csv_filename, "w", newline="", encoding="utf-8-sig") as output:
        df.to_csv(output, index=False)

    print(f"Data saved to {csv_filename}")
    print(df.head())  # Print first few rows as a preview


if __name__ == "__main__":
    get_point_groups()
