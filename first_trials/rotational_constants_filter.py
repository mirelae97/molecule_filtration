# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import time

def get_rotational_constant(formula, name):
    print(f"Checking rotational constant for: {formula}")
    
    base_url = 'https://cccbdb.nist.gov'
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.7',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://cccbdb.nist.gov',
        'referer': 'https://cccbdb.nist.gov/exprot1x.asp',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }
    
    session = requests.Session()
    
    try:
        # Initial GET to start session
        session.get(f'{base_url}/exprot1x.asp', headers=headers)

        # POST request with formula
        session.post(
            f'{base_url}/getformx.asp',
            headers=headers,
            data={'formula': formula, 'submit1': 'Submit'},
            allow_redirects=True
        )
        
        # Final GET to fetch result
        dipole_response = session.get(f'{base_url}/exprot2x.asp', headers=headers)
        soup = BeautifulSoup(dipole_response.text, 'html.parser')
        
        tables = soup.find_all("table")
        
        if not tables:
            print(f"No tables found for {formula}")
            return None

        rot_constants = []
        
        # Track exact matches
        found_exact_match = False

        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                
                if len(cells) < 2:
                    continue
                    
                # Look for exact matches in each cell
                for cell in cells:
                    # Get the exact text content without HTML or extra whitespace
                    cell_text = cell.get_text(strip=True)
                    
                    # Check for exact match (case insensitive)
                    if cell_text.lower() == name.lower():
                        found_exact_match = True
                        print(f"Found exact match for '{name}'")
                        
                        # Get all cells with class="right" in this row
                        right_cells = row.find_all('td', class_='right')
                        for right_cell in right_cells:
                            try:
                                value = float(right_cell.get_text(strip=True))
                                rot_constants.append(value)
                            except ValueError:
                                continue
                        
                        # We found an exact match in this row, so we're done with this row
                        break
        
        # If we didn't find any exact matches using the above method, try a different approach
        if not found_exact_match:
            print(f"No exact match found for '{name}', checking alternative approach")
            
            for table in tables:
                for td in table.find_all('td'):
                    # Get text content without any HTML or extra whitespace
                    td_text = td.get_text(strip=True)
                    
                    # Check for exact match (case insensitive)
                    if td_text.lower() == name.lower():
                        found_exact_match = True
                        print(f"Found exact match for '{name}' using alternative approach")
                        
                        # Get the parent row
                        parent_row = td.find_parent('tr')
                        if parent_row:
                            # Find all right-aligned cells in this row
                            right_cells = parent_row.find_all('td', class_='right')
                            for right_cell in right_cells:
                                try:
                                    value = float(right_cell.get_text(strip=True))
                                    rot_constants.append(value)
                                except ValueError:
                                    continue
        
        if rot_constants:
            print(f"Rotational constants found for {formula} (exact match for '{name}'): {rot_constants}")
            return rot_constants
        else:
            if found_exact_match:
                print(f"Found exact match for '{name}', but couldn't extract rotational constants")
            else:
                print(f"No exact match found for '{name}'")
            return None
        
    except Exception as e:
        print(f"An error occurred for {formula}: {e}")
        return None

# Example usage
rot_const = get_rotational_constant("H2O", "water")

# This would not match "hydrogen chloride cation"
# rot_const_cation = get_rotational_constant("HCl", "hydrogen chloride cation")