# import necessary libraries
import requests # this is a library that allows to send HTTP requests to websites. Simulates what a browser does when fetching web content
from bs4 import BeautifulSoup # from the bs4 module imports the class beautifulsoup. This is used to parse HTML or XML content and extract information from it
import csv # this imports the csv module. It is used to read and write CSV files
import pandas as pd # this imports the pandas library and it is giving it the alias pd that is used for data manipulation and analaysis
import time # this imports the time module which is used to measure how long things run or to pause an execution


def get_dipole_moment(formula, name=None, max_retries=3, retry_delay=2):
    """
    Get dipole moment for a molecule from CCCBDB.
    
    Args:
        formula (str): Molecular formula to search for
        name (str, optional): Specific molecule name to select if multiple options are found
        max_retries (int): Maximum number of retry attempts if the search fails
        retry_delay (int): Delay in seconds between retry attempts
        
    Returns:
        float or None: Dipole moment value if found, None otherwise
    """
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
                'referer': 'https://cccbdb.nist.gov/dipole1x.asp',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            }
            
            # Prepare session
            session = requests.Session()
            
            # Initial page visit
            session.get('https://cccbdb.nist.gov/dipole1x.asp')
            
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
            
            # Check if we're already on the dipole data page
            dipole_table = soup.find('table', id='table2')
            
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
                
                # Now we should be at dipole2x.asp
                soup = BeautifulSoup(response.text, 'html.parser')
                
            elif dipole_table:
                print("Directly landed on dipole data page")
                # We're already on the dipole data page, so no selection needed
                pass
            else:
                print(f"Landed on unrecognized page on attempt {attempt}")
                if attempt < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
            
            # At this point, we should be on the dipole data page
            # Find table2 (in case we just refreshed the soup)
            table2 = soup.find('table', id='table2')
            
            if not table2:
                print(f"Could not find dipole data table on attempt {attempt}")
                if attempt < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
            
            # Look for HF method
            hf_th = table2.find('th', class_='nowrap', string=lambda text: text and 'HF' in text)
            
            if not hf_th:
                print(f"Could not find HF method row on attempt {attempt}")
                if attempt < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
            
            # Find the value cell
            hf_td = hf_th.find_next('td', class_='num bordered')
            
            if hf_td and hf_td.a:
                try:
                    value = float(hf_td.a.text.strip())
                    molecule_name = "unknown" if not 'selected_option' in locals() else selected_option['name']
                    print(f"Dipole moment for {formula} ({molecule_name}): {value}")
                    return value
                except ValueError:
                    print(f"Could not convert {hf_td.a.text} to float for {formula}")
            else:
                print(f"Could not find dipole value for {formula}")
            
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
    
potato = get_dipole_moment("NCN", "Cyanoimidogen")