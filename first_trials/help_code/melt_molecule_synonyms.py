import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

# This function searches the NIST Chemistry WebBook for a given chemical name
# and returns up to 4 alternative names (synonyms) listed under "Other names:"
def search_molecule_names_nist(chem_name):
    # Base URL for NIST chemical name search
    nist_name_search_url = "https://webbook.nist.gov/cgi/cbook.cgi"
    
    # Parameters used for the search query
    params_nist_syno = {
        "Name": chem_name,   # chemical name to search
        "Units": "SI",       # use SI units
        "Action": "Search"   # perform a search action
    }

    retries = 3  # number of retry attempts in case of network failure

    for i in range(retries):
        try:
            # Send GET request to NIST with search parameters
            response_nist_syno = requests.get(nist_name_search_url, params=params_nist_syno, timeout=30)
            response_nist_syno.raise_for_status()  # raise exception if HTTP request returned an error

            # Parse the HTML content of the response using BeautifulSoup
            soup_nist_syno = BeautifulSoup(response_nist_syno.text, 'html.parser')
            
            # Check if "Other names:" is mentioned in the page text
            if "Other names:" in soup_nist_syno.text:
                # Loop through all list items in the HTML
                for li in soup_nist_syno.find_all("li"):
                    strong_word = li.find("strong")  # Look for <strong> tags within each <li>
                    
                    # Check if the <strong> tag exists and contains "Other names:"
                    if strong_word and "Other names:" in strong_word.text:
                        # Get the full text content of the <li> tag, with whitespace stripped
                        full_text = li.get_text(separator=" ", strip=True)
                        
                        # Remove the "Other names:" label from the full text to isolate the name list
                        other_names_text = full_text.replace(strong_word.text, "").strip()
                        
                        # Split the names by semicolon and clean up whitespace
                        other_names = [name.strip() for name in other_names_text.split(';') if name.strip()]
                        
                        # Return the first 4 alternative names found
                        return other_names[:4]
            if "Name Not Found" in soup_nist_syno.text:
                return (f"No synonyms can be extracted because {chem_name} is not in NIST")

        except requests.exceptions.RequestException as e:
            # If the request fails, print an error message and wait before retrying
            print(f"Request failed for {chem_name}: {e}")
            time.sleep(5)
            continue

    return None  # If all retries fail or "Other names" not found

# get names from csv file 


def process_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    # Use the 3rd column (index 2) for chemical names
    chem_col = df.columns[2]
    synonyms = []
    for name in df[chem_col]:
        print (f"checking {name}")
        result = search_molecule_names_nist(name)
        if isinstance(result,list):
            synonyms.append(",".join(result))
        else:
            synonyms.append(result)
    
    df["NIST Synonyms"] = synonyms

    df.to_csv(output_csv, index = False)    
    print ("Saved results")

process_csv("molecule_filter_TOC/filter1_properties_no_symmetry_no_duplicates.csv","molecule_filter_TOC/test_addition_synonyms")

    