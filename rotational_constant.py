# import necessary libraries
import pandas as pd
import time

# This function scrapes the CCCBDB database to get the rotational constants
# from the cell with class "num bordered"
def get_rotational_constants(formula, name=None, max_retries=3, retry_delay=2):
    import time
    import requests
    from bs4 import BeautifulSoup
    
    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt}/{max_retries} for {formula}" + (f" with name: {name}" if name else ""))
        
        try:
            base_url = 'https://cccbdb.nist.gov'
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'en-US,en;q=0.7',
                'cache-control': 'max-age=0',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://cccbdb.nist.gov',
                'referer': 'https://cccbdb.nist.gov/rotcalc1x.asp',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            }
            
            # Prepare session
            session = requests.Session()
            
            # Initial page visit
            session.get('https://cccbdb.nist.gov/rotcalc1x.asp')
            
            # Post the form data to search for the formula
            response = session.post(
                f'{base_url}/getformx.asp',
                headers=headers,
                data={'formula': formula, 'submit1': 'Submit'},
                allow_redirects=True,
                timeout=30
            )
            
            # Check if the page shows no results
            if "No entries found" in response.text:
                print(f"No entries found for {formula} on attempt {attempt}")
                if attempt < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
            
            # Check which page we landed on
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if we're on the selection page
            selection_table = soup.find('table', {'border': '1'})
            selection_form = soup.find('form', {'action': 'gotonex.asp'})
            
            # Check if we're already on the rotational constants data page
            rotational_table = soup.find('table', id='table2')
            
            # Determine current page
            if selection_table and selection_form:
                print("Landed on selection page with multiple options")
                
                # Find all radio buttons in the table
                ground_min_options = []
                radio_buttons = selection_table.find_all('input', type='radio', attrs={'name': 'which'})
                
                for radio in radio_buttons:
                    row = radio.find_parent('tr')
                    row_text = row.get_text().lower()
                    
                    if 'ground' in row_text and 'minimum' in row_text:
                        which_value = radio.get('value')
                        
                        # Extract molecule name
                        cells = row.find_all('td')
                        molecule_formula = ""
                        molecule_name = ""
                        
                        # Try to identify formula and name cells
                        for i, cell in enumerate(cells):
                            if i == 1 and cell.has_attr('rowspan'):  # Usually formula cell
                                molecule_formula = cell.text.strip()
                            elif i == 2 and cell.has_attr('rowspan'):  # Usually name cell
                                molecule_name = cell.text.strip()
                        
                        # If we still don't have a name, try another approach
                        if not molecule_name:
                            for cell in cells:
                                cell_text = cell.text.strip()
                                if len(cell_text) > 3 and cell_text.lower() not in ['ground', 'minimum']:
                                    if not molecule_formula:
                                        molecule_formula = cell_text
                                    else:
                                        molecule_name = cell_text
                                        break
                        
                        ground_min_options.append({
                            'value': which_value,
                            'formula': molecule_formula,
                            'name': molecule_name,
                            'row_text': row_text
                        })
                
                if not ground_min_options:
                    print(f"No ground/minimum options found on attempt {attempt}")
                    if attempt < max_retries:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return None
                
                selected_option = None
                
                # If we have multiple options
                if len(ground_min_options) > 1:
                    if name:
                        # Try to find the option matching the specified name
                        for option in ground_min_options:
                            if option['name'] and name.lower() in option['name'].lower():
                                selected_option = option
                                break
                    
                    # If no name specified or no match found, use the first option
                    if not selected_option:
                        selected_option = ground_min_options[0]
                else:
                    # Only one option found
                    selected_option = ground_min_options[0]
                
                which_value = selected_option['value']
                print(f"Selected option: {selected_option['name']} with value: {which_value}")
                
                # Update the referer header
                headers['referer'] = response.url
                
                # Submit the selection form
                response = session.post(
                    f'{base_url}/gotonex.asp',
                    headers=headers,
                    data={'which': which_value},
                    allow_redirects=True,
                    timeout=30
                )
                
                # Now we should be at the rotational constants page
                soup = BeautifulSoup(response.text, 'html.parser')
                
            elif rotational_table:
                print("Directly landed on rotational constants data page")
                # We're already on the rotational constants page, so no selection needed
                pass
            else:
                print(f"Landed on unrecognized page on attempt {attempt}")
                if attempt < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
            
            # At this point, we should be on the rotational constants page
            # Find table2 (in case we just refreshed the soup)
            table2 = soup.find('table', id='table2')
            
            if not table2:
                print(f"Could not find rotational constants table on attempt {attempt}")
                if attempt < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
            
            # Look for the cell with class "num bordered"
            bordered_cell = table2.find('td', class_='num bordered')
            
            if not bordered_cell:
                print(f"Could not find cell with class 'num bordered' on attempt {attempt}")
                if attempt < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
            
            # Extract the values from the cell
            # The values are separated by <BR> tags
            if bordered_cell:
                try:
                    # Get the text content and split by line breaks
                    cell_content = bordered_cell.get_text(separator='<BR>', strip=True)
                    rotational_constants = cell_content.split('<BR>')
                    
                    # Convert to float values
                    rot_constants = [float(val.strip()) for val in rotational_constants]
                    
                    molecule_name = "unknown" if not 'selected_option' in locals() else selected_option['name']
                    print(f"Rotational constants for {formula} ({molecule_name}): {rot_constants}")
                    return rot_constants
                except ValueError:
                    print(f"Could not convert {bordered_cell.text} to float values for {formula}")
            else:
                print(f"Could not find bordered cell for {formula}")
            
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                return None
                
        except Exception as e:
            print(f"An error occurred for {formula} on attempt {attempt}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                return None
    
    return None

def extract_rotational_constants_to_csv(input_csv, output_csv, delay=1):
    """
    Extract rotational constants for molecules in the input CSV and save to output CSV.
    
    Parameters:
    input_csv (str): Path to input CSV file containing molecule information
    output_csv (str): Path to output CSV file to save the results
    delay (int): Delay in seconds between requests to avoid overwhelming the server
    """
    # Read the input CSV
    df = pd.read_csv(input_csv)
    
    # Create new columns for rotational constants
    df['Rotational Constant 1'] = None
    df['Rotational Constant 2'] = None
    df['Rotational Constant 3'] = None
    
    # Iterate through the rows of the CSV file
    for index, row in df.iterrows():
        formula = row.iloc[3]  # Gets the formula present in the 4th column
        name = row.iloc[2]     # Gets the name from the 3rd column
        
        try:
            # Get rotational constants for this molecule
            rotational_constants = get_rotational_constants(formula, name)
            
            if rotational_constants is not None:
                # Store rotational constants in the DataFrame
                df.at[index, 'Rotational Constant 1'] = rotational_constants[0]
                df.at[index, 'Rotational Constant 2'] = rotational_constants[1]
                if len(rotational_constants) > 2:  # In case there are 3 constants
                    df.at[index, 'Rotational Constant 3'] = rotational_constants[2]
                
                print(f"Added rotational constants for {formula}: {rotational_constants}")
            else:
                print(f"No rotational constants found for {formula}")
            
            # Add a delay to avoid overwhelming the server
            time.sleep(delay)
            
        except Exception as e:
            print(f"Error processing {formula}: {e}")
    
    # Save the results to CSV
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")
    print(f"Total molecules processed: {len(df)}")
    print(f"Molecules with rotational constants: {df['Rotational Constant 1'].notna().sum()}")


extract_rotational_constants_to_csv(
    "molecule_filter_TOC/2025_05_13_change_order/4_filtered_with_point_group.csv",
    "molecule_filter_TOC/2025_05_13_change_order/5_rotational_constants.csv"
)