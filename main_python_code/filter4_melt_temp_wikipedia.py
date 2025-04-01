# import necessary libraries
import requests # this is a library that allows to send HTTP requests to websites. Simulates what a browser does when fetching web content
from bs4 import BeautifulSoup # from the bs4 module imports the class beautifulsoup. This is used to parse HTML or XML content and extract information from it
import pandas as pd # this imports the pandas library and it is giving it the alias pd that is used for data manipulation and analaysis
import time # this imports the time module which is used to measure how long things run or to pause an execution
import re # this library is used for regular expressions (regex). Allows to search, extact and manipulate text

# this function extracts info from wikipedia, in this case the melting temperature of the substances
def get_wikipedia_info(name):
    
    # it may not be possible to get information from wikipedia, therefore we use "try"
    try:
        
        # when searching a chemical name in wikipedia, the spaces may lead to errors, therefore it is important to replace spaces with underscore 
        formatted_name = name.replace(' ', '_') # replace spaces by underscore
        
        wikipedia_url = f"https://en.wikipedia.org/wiki/{formatted_name}" # create the url to search in the wikipedia page

        # to prevent errors when making a request to wikipedia it is worth writing the user. This is introduced in the header and called later
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # gets the information from the wikipedia page using the headers
        response = requests.get(wikipedia_url, headers=headers)
        # determines if it was possible to make the request. If not exception is triggered
        response.raise_for_status()
        
        # in case there is no wikipedia page for the searched compound 
        if "Wikipedia does not have an article with this exact name" in response.text: # checks if there is a wikipedi page in the text of the wikipedia website
            print(f"No Wikipedia page found for {name}") # in case there is not, informs the user that there is no such wikipedia page
            return None # returns None

        soup = BeautifulSoup(response.text, 'html.parser') # if there is a wiki page gets the soup it is possible to search info in the text

        # searches for the melting point in the wikipedia page
        # when entering the page source of wikipedia one can see that in case there is a melting point follows the pattern shown below:
        melting_point_link = soup.find('a', {'href': '/wiki/Melting_point', 'title': 'Melting point'}) 
        
        if melting_point_link:# in case the melting point is found:
            # get the parent td
            parent_td = melting_point_link.find_parent('td')
            if parent_td: # in case a parent td is found
                # find the next sibling td 
                value_td = parent_td.find_next_sibling('td')
                if value_td: # in case the next sibling is found
                    value_text = value_td.get_text() # extract the text present in value td
                    # in some wikipedia entries there are errors, we want to remove them. These errors appear after plusminius values      
                    if '±' in value_text: # in case a plusminus value is found 
                        # splits into two the text present in value_text using ± as delimiter. Then takes the first part of the two
                        value_text = value_text.split('±')[0].strip() # strip removes any leading or trailing zeroes
                    
                    # use regex to find plus sign (+), standard minus (-) and unicode minus (−)
                    # r allows to interpret backslashes
                    # ([+\-−]?\d+\.?\d*) is the capturing group
                        #[+\-−]? match anyone of the characters inside
                        #\d+\ indicates the begining of a number
                        #\.? includes a possible prescence of a dec point
                        # \d* grabs the numbers after the decimal point 
                    match = re.search(r'([+\-−]?\d+\.?\d*)', value_text)
                    if match: # in case +, - , and unicode minus are found
                        melting_point_text = match.group(1) # extracts whaetever is contained in the capturing group
                        melting_point_text = melting_point_text.replace('−', '-') # replace Unicode minus sign with normal minus
                        
                        # it may not be possible to convert the melting_point into a float and this is why we use "try"
                        try: 
                            melting_point_value = float(melting_point_text) # convert the value into a float
                        # in case it is not possible to convert it to a value
                        except ValueError:
                            print(f"Not possible to convert to float for {name}") # inform the user

                    
                        print(f"Found the melting point of {name}: {melting_point_value} C°")
                        return melting_point_value

        print(f"Melting point for {name} not found.")
        return None

    # exceptions in case wikipedia page is not found
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

# function that filters the molecules according to the melting temperature
def filter_molecules_by_melting_temperature(input_csv, output_csv_good, output_csv_no_values, output_csv_discarted, delay=1): # function definition
   
    # read the input CSV
    df = pd.read_csv(input_csv)
    
    # create a list to store molecules that pass the filter
    filtered_molecules_good = [] # this array will contain the molecules that passed the filter
    filtered_molecules_no_values = [] # this array will contain the molecules whose melting temperature value was not found
    filtered_molecules_discarted = [] # this value contains the molecules that did not pass the filter

    # the csv I pass has multiple columns. Out of these the 3th contains the chemical names 
    for index, row in df.iterrows(): # iterate through the rows of the csv file
        chem_name = row.iloc[2]  # gets the chemical name present in the 3rd column
        
        try: # it may not be possible to get the melt temperature from the server so we use "try"

            melt_temp = get_wikipedia_info(chem_name) # call the get_wikipedia_info function
            
            if melt_temp is None: # if the output of the melt temperature search is None
                filtered_molecules_no_values.append(row) # append the row that was read to the array with no values
                print(f"{chem_name}: Melting Temperature = {melt_temp} - NONE PASSED") # notify the user that the molecule has passed the filter with NONE value
            if melt_temp is not None and melt_temp <= 25: #  if the output value is bigger than 25ºC
                print(f"{chem_name}: Melting Temperature = {melt_temp} - PASSED") # notify the user that the molecule has passed the filter
                row_with_melt_temp = row.copy() # copies the current row
                row_with_melt_temp["Melting Temperature [K]"] = melt_temp # adds the melting temperature value to the row
                filtered_molecules_good.append(row_with_melt_temp) # append the row that was read to the new array
            if melt_temp is not None and melt_temp > 25: # if the output value is not bigger than 25ºC
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

# calling the filter_molecules_by_dipole function
filter_molecules_by_melting_temperature("molecule_filter_TOC/no_symmetry_restriction/filter3_atoms_1_5.csv", 'molecule_filter_TOC/no_symmetry_restriction/filter_melt_temp_good.csv', "molecule_filter_TOC/no_symmetry_restriction/filter_melt_temp_no_values.csv","molecule_filter_TOC/no_symmetry_restriction/filter_melt_temp_discarted.csv")