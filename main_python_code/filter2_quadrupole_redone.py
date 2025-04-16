# import necessary libraries
import requests # this is a library that allows to send HTTP requests to websites. Simulates what a browser does when fetching web content
from bs4 import BeautifulSoup # from the bs4 module imports the class beautifulsoup. This is used to parse HTML or XML content and extract information from it
import pandas as pd # this imports the pandas library and it is giving it the alias pd that is used for data manipulation and analaysis
import time # this imports the time module which is used to measure how long things run or to pause an execution


# This function makes scraping to the CCCBDB database in order to get
# the calculated quadrupole moment values
def get_quadrupole_moment(formula, name=None, max_retries=3, retry_delay=2):
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
                'referer': 'https://cccbdb.nist.gov/quadrupole1x.asp',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            }
            
            # Prepare session
            session = requests.Session()
            
            # Initial page visit
            session.get('https://cccbdb.nist.gov/quadrupole1x.asp')
            
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
            
            # Check if we're already on the quadrupole data page
            quadrupole_table = soup.find('table', id='table2')
            
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
                
                # Now we should be at quadrupole2x.asp
                soup = BeautifulSoup(response.text, 'html.parser')
                
            elif quadrupole_table:
                print("Directly landed on quadrupole data page")
                # We're already on the quadrupole data page, so no selection needed
                pass
            else:
                print(f"Landed on unrecognized page on attempt {attempt}")
                if attempt < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None
            
            # At this point, we should be on the quadrupole data page
            # Get the quadrupole data
            quadrupole_response = session.get(f'{base_url}/quadrupole2x.asp', headers=headers)
            soup = BeautifulSoup(quadrupole_response.text, 'html.parser')
            
            # Find table2 (in case we just refreshed the soup)
            table2 = soup.find('table', id='table2')
            
            if not table2:
                print(f"Could not find quadrupole data table on attempt {attempt}")
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
                    print(f"Quadrupole moment for {formula} ({molecule_name}): {value}")
                    return value
                except ValueError:
                    print(f"Could not convert {hf_td.a.text} to float for {formula}")
            else:
                print(f"Could not find quadrupole value for {formula}")
            
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
    

def filter_molecules_by_quadrupole(input_csv, output_csv_good, output_csv_no_value, output_csv_discarted, output_csv_joined, delay=1): # function definition
   
    # read the input CSV
    df = pd.read_csv(input_csv)
    
    # create arrays where to store the resulting molecules 
    filtered_molecules_good = [] # here the molecules that pass the filter are stored
    filtered_molecules_no_value = [] # here the molecules whose value could not be find are stored
    filtered_molecules_discarted = [] # here the molecules that did not pass the filter are stored
    filtered_molecules_joined = [] # here the combination of the molecules that passed the filter and whose value could not be find

    # the csv I pass has multiple columns. Out of these the 4th contains the formulas 
    for index, row in df.iterrows(): # iterate through the rows of the csv file
        formula = row.iloc[3]  # gets the formula present in the 4th column
        name = row.iloc[2]
        
        try: # it may not be possible to get the quadrupole moment from the server so we use "try"

            quadrupole_moment = get_quadrupole_moment(formula, name) # call the get_quadrupole_moment function
            
            # check if quadrupole moment is above 0.5
            if quadrupole_moment is None: # if the output of the quadrupole search is None
                filtered_molecules_no_value.append(row) # append the row that was read to the now value array
                filtered_molecules_joined.append(row) # appens the row that was read to the joined array
                print(f"{formula}: Quadrupole Moment = {quadrupole_moment} - NONE PASSED") # notify the user that the molecule has passed the filter with NONE value
            if quadrupole_moment is not None and abs(quadrupole_moment) >= 0.5: #  if the output value is bigger than 0.5
                print(f"{formula}: Quadrupole Moment = {quadrupole_moment} - PASSED") # notify the user that the molecule has passed the filter
                row_with_quadrupole = row.copy() # copies the current row
                row_with_quadrupole["Quadrupole Moment"] = quadrupole_moment # adds the quadrupole moment value to the row
                filtered_molecules_joined.append(row_with_quadrupole) # append the row that was read to the joined array
                filtered_molecules_good.append(row_with_quadrupole) # append the row that was read to the good array
            if quadrupole_moment is not None and abs(quadrupole_moment) < 0.5: # if the output value is not bigger than 0.5
                row_with_quadrupole = row.copy() # copies the current row
                row_with_quadrupole["Quadrupole Moment"] = quadrupole_moment # appends the quadrupole moment value to the new row
                print(f"{formula}: Quadrupole Moment = {quadrupole_moment} - FILTERED OUT") # notifify the user that the molecule has not passed the filter
                filtered_molecules_discarted.append(row_with_quadrupole) # append the row to the discarted array
            # add a delay to avoid overwhelming the server
            time.sleep(delay)
        
        # in case it is not possible to call the function or if there is a network problem
        except Exception as e:
            print(f"Error processing {formula}: {e}")
    
    # create a new DataFrame with filtered molecules for each array
    filtered_df_good = pd.DataFrame(filtered_molecules_good)
    filtered_df_no_value = pd.DataFrame(filtered_molecules_no_value)
    filtered_df_discarted = pd.DataFrame(filtered_molecules_discarted)
    filtered_df_joined = pd.DataFrame(filtered_molecules_joined)
    
    # converts the dataframe to a csv false
    # by default pandas assigns an integer index to each row when creating a dataframe which produces an extra column. Since we do not want that we set index to false
    filtered_df_good.to_csv(output_csv_good, index=False) # by default pandas assigns an integer index to each row when creating a dataframe which produces an extra column. Since we do not want that we set index to false
    filtered_df_no_value.to_csv(output_csv_no_value, index=False)
    filtered_df_discarted.to_csv(output_csv_discarted, index=False)
    filtered_df_joined.to_csv(output_csv_joined, index=False)
    
    # user notification
    print(f"Total molecules processed: {len(df)}")
    print(f"Molecules passing filter: {len(filtered_molecules_good)}")
    print(f"Molecules NOT passing filter: {len(filtered_molecules_discarted)}")
    print(f"Molecules with no quadrupole moment found: {len(filtered_molecules_no_value)}")

# calling the filter_molecules_by_quadrupole function
filter_molecules_by_quadrupole("molecule_filter_TOC/no_symmetry_restriction/csv_files/filter2_again_no_values.csv", 'molecule_filter_TOC/no_symmetry_restriction/csv_files/filter2_again_good2.csv', 'molecule_filter_TOC/no_symmetry_restriction/csv_files/filter2_again_no_values_2.csv', 'molecule_filter_TOC/no_symmetry_restriction/csv_files/filter2_again_discarted2.csv', 'molecule_filter_TOC/no_symmetry_restriction/csv_files/filter2_again_joined2.csv')