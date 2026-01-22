import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re

def get_fus_point(chemical_name):
    base_search_url = "https://webbook.nist.gov/cgi/cbook.cgi"
    
    params = {
        "Name": chemical_name,
        "Units": "SI",
        "cTG": "on",  # Thermodynamic data
        "cTC": "on",  # Thermochemistry data
    }

    retries = 3

    for i in range(retries):
        try:
            response = requests.get(base_search_url, params=params, timeout=30)
            response.raise_for_status()  # This will raise an HTTPError if there's a problem with the request
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if "Name Not Found" in soup.text:
                print(f"The molecule '{chemical_name}' could not be found in NIST.")
                return None

            phase_change_link = None
            for a in soup.find_all('a', href=True):
                if "Phase change data" in a.text: 
                    phase_change_link = base_search_url + a['href']
                    break

            if not phase_change_link:
                print(f"No phase change data for {chemical_name}")
                return None
    
            response_phase_change = requests.get(phase_change_link)
            response_phase_change.raise_for_status()
            soup_phase = BeautifulSoup(response_phase_change.text, 'html.parser')
    
            table = soup_phase.find("table")
            if not table: 
                print(f"No data table for {chemical_name}") 
                return None
    
            t_fus_values = []

            if "fus" in soup_phase.text:
                for row in table.find_all("tr"):
                    cols = row.find_all("td")
                    row_text = row.get_text().lower()
                    if "fus" in row_text:
                        t_fus = cols[1].text.strip()
                        if "±" in t_fus:
                            t_fus = re.sub(r'\s*±.*', '', t_fus)
                        if " to" in t_fus:
                            t_fus = re.sub(r'\s*to.*', '', t_fus)
                        
                        try:
                            t_fus_values.append(float(t_fus))
                        except ValueError:
                            print(f"Invalid fus value for {chemical_name}: {t_fus}")
                            continue
    
            if t_fus_values: 
                average_t_fus = sum(t_fus_values) / len(t_fus_values)
                return average_t_fus
            else:
                print(f"No T_fus value for {chemical_name}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request failed for {chemical_name}: {e}")
            time.sleep(5)
            continue

    print(f"Giving up on {chemical_name} after {retries} retries.")
    return None


def process_csv(input_csv, output_csv_good, output_csv_no_values, output_csv_discarted, delay=1):
    df = pd.read_csv(input_csv)

    filtered_molecules_good = []
    filtered_molecules_no_values = []
    filtered_molecules_discarted = []

    for index, row in df.iterrows():
        chem_name = row.iloc[2]
        print(f"Checking melting temperature for {chem_name}")
        
        try:

            melt_temp = get_fus_point(chem_name)

            if melt_temp is None: # if the output of the melt temperature search is None
                filtered_molecules_no_values.append(row) # append the row that was read to the array with no values
                print(f"{chem_name}: Melting Temperature = {melt_temp} - NONE PASSED") # notify the user that the molecule has passed the filter with NONE value
            if melt_temp is not None and melt_temp <= 298: #  if the output value is bigger than 25ºC
                print(f"{chem_name}: Melting Temperature = {melt_temp} - PASSED") # notify the user that the molecule has passed the filter
                row_with_melt_temp = row.copy() # copies the current row
                row_with_melt_temp["Melting Temperature [K]"] = melt_temp # adds the melting temperature value to the row
                filtered_molecules_good.append(row_with_melt_temp) # append the row that was read to the new array
            if melt_temp is not None and melt_temp > 298: # if the output value is not bigger than 25ºC
                filtered_molecules_discarted.append(row)
                print(f"{chem_name}: Melting Temperature = {melt_temp} - FILTERED OUT") # notifify the user that the molecule has not passed the filter
                
                # add a delay to avoid overwhelming the server
                time.sleep(delay)
        
        # in case it is not possible to call the function or if there is a network problem
        except Exception as e:
            print(f"Error processing {chem_name}: {e}")
    
    # create a new DataFrame with filtered molecules
    filtered_df_discarted = pd.DataFrame(filtered_molecules_discarted)
    filtered_df_no_values = pd.DataFrame(filtered_molecules_no_values)
    filtered_df_good = pd.DataFrame(filtered_molecules_good)
    
    # converts the dataframe to a csv false
    filtered_df_discarted.to_csv(output_csv_discarted, index=False) # by default pandas assigns an integer index to each row when creating a dataframe which produces an extra column. Since we do not want that we set index to false
    filtered_df_no_values.to_csv(output_csv_no_values, index=False) # by default pandas assigns an integer index to each row when creating a dataframe which produces an extra column. Since we do not want that we set index to false
    filtered_df_good.to_csv(output_csv_good, index=False) # by default pandas assigns an integer index to each row when creating a dataframe which produces an extra column. Since we do not want that we set index to false

    # user notification
    print(f"Total molecules processed: {len(df)}")
    print(f"Molecules passing filter: {len(filtered_molecules_good)}")
    print(f"Molecules not passing filter: {len(filtered_molecules_discarted)}")
    print(f"Molecules with not found values: {len(filtered_molecules_no_values)}")



# Example usage
process_csv("molecule_filter_TOC/no_symmetry_restriction/filter_melt_temp_no_values.csv", 'molecule_filter_TOC/no_symmetry_restriction/filter_melt_temp_good_nist.csv', "molecule_filter_TOC/no_symmetry_restriction/filter_melt_temp_no_values_nist.csv","molecule_filter_TOC/no_symmetry_restriction/filter_melt_temp_discarted_nist.csv")