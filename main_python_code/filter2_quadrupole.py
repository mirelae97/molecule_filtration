# import necessary libraries
import requests # this is a library that allows to send HTTP requests to websites. Simulates what a browser does when fetching web content
from bs4 import BeautifulSoup # from the bs4 module imports the class beautifulsoup. This is used to parse HTML or XML content and extract information from it
# import csv # this imports the csv module. It is used to read and write CSV files
import pandas as pd # this imports the pandas library and it is giving it the alias pd that is used for data manipulation and analaysis
import time # this imports the time module which is used to measure how long things run or to pause an execution

# this function searches for the quadrupole moment in the cccbdb webpage. the calculated quadrupole value we choose is calculated with the hartree fock method with the 6-31G* basis set
# the function inputs the chemical formula of the compound 
# the function outputs the quadrupole moment as a float if found and "None" if the quadrupole moment is not found
def get_quadrupole_moment (formula): 
    
    print(f"Checking quadrupole moment for molecule: {formula}")

    base_url = 'https://cccbdb.nist.gov' # url of the cccbdb webpage

    # define the headers: this is information that will be sent when making an HTTP request. If they are not properly defined the request to the server will likely fail
    # the header info I got from the developer tools in the network section from the first asp
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', # tells the server what type of content we want, in this case: HTML,XHTML and XML
        'accept-language': 'en-US,en;q=0.7', # specifies the prefered language for the content in our case english
        'cache-control': 'max-age=0', #  defines how caching should work, in this case we do not cache the response
        'content-type': 'application/x-www-form-urlencoded', # defines what type of data is being sent: in our case URL enconded data   
        'origin': 'https://cccbdb.nist.gov', # specifies the origin of the requesting page
        'referer': 'https://cccbdb.nist.gov/quadrupole1x.asp', # specifies the full URL from which the request is being made
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36' # identifies the client making the request. 
    }

    # prepare session and cookies
    session = requests.Session() # allows to mantain parameters of the search. In our case is important to keep the headers the same

    try: # the server info request may fail, the try allows to handle the cases where it works and the exceptions allow to handle cases when it does not work
        
        session.get('https://cccbdb.nist.gov/quadrupole1x.asp') # request information to the quadrupole calculation page of the cccbdb
        
        # we make a post request: HTTP request to submit data to a server
        response = session.post(
            f'{base_url}/getformx.asp', # this is the URL to which the request is being sent. This I got by checking the network developer tools when doing the search request in the browser
            headers=headers, # adds the headers we defined before to the request, specifiying exactly what info we want
            data={'formula': formula, 'submit1': 'Submit'}, # this is the data we are sending with the request: the formula and the submit option
            allow_redirects=True # the server may redirect our request. this allows for the redirects
        )
        
        # we get the data that the server returns to us
        quadrupole_response = session.get(f'{base_url}/quadrupole2x.asp', headers=headers) # here the url from which the data want to be get and the headers we used for the initial request
        
        # Parse the HTML to be able to search in it
        soup = BeautifulSoup(quadrupole_response.text, 'html.parser') # we parse the text (. text) of the info that the server sent us with the get
        
        # the quadrupole information we want is stored in the so called "table2". this I checked by doing a search in the browser and then viewing the page source 
        table2 = soup.find('table', id='table2') # this command searches in the soup table 2
        
        # it may be possible that for some molecules table 2 does not exist
        if table2: # if table 2 exists
            # the info we want is stored in a row which has given settings you can find my viewing the page source
            hf_th = table2.find('th', class_='nowrap', string=lambda text: text and 'HF' in text) 
            
            # there is a possibility to not find the desired info
            if hf_th: # in case a we find it
                # now that we have found the header, one has to search for table data cell that contains our info
                hf_td = hf_th.find_next('td', class_='num bordered') # this searches for the next table data cell after hf_th that belongs to a class 'num bordered'
                
                # in case that table data cell is found and also contains an <a> tag then we extract the value
                if hf_td and hf_td.a:
                    # it may not be possible to convert the value into a float so we use the function "try"
                    try:
                        value = float(hf_td.a.text.strip()) # extracts the text that is linked to the <a> tag, removes any leading and trailing whitespace and tries to convert it into a float
                        print(f"Quadrupole moment for {formula}: {value}") # prints the output of the quadrupole moment
                        return value # returns the value
                    except ValueError: # in case it cannot convert the value into a float:
                        print(f"Could not convert {hf_td.a.text} to float for {formula}")
                        return None
                # in case the table data cell is not found:
                else:
                    print(f"Could not find value for {formula}")
            # in case the HF method is not found: 
            else:
                print(f"Could not find HF method row for {formula}")
        # in case Table 2 is not found:
        else:
            print(f"Could not find table2 for {formula}")
        
        return None
    
    # in case the request to the server fails
    except Exception as e:
        print(f"An error occurred for {formula}: {e}")
        return None


# this function loops over all the formulas present in the csv file with the initially filtered molecules and applies to all of them the get_quadrupole_moment function to retrieve their quadrupole moments
# if the quadrupole moment is bigger than 0.2 then the molecule is kept if the quadrupole moment is smaller than 0.2 then the molecule is discarted
# the function needs 3 inputs, the csv file where the molcular formulas are stored, the name and path where to store the filtered csv file and the delay time one should wait between processing two consecutive molecules to avoid overwhelming the server
def filter_molecules_by_quadrupole(input_csv, output_csv_good, output_csv_no_value, output_csv_discarted, output_csv_joined, delay=1): # function definition
   
    # read the input CSV
    df = pd.read_csv(input_csv)
    
    # create a list to store molecules that pass the filter
    filtered_molecules_good = [] # here the molecules that pass the filter are stored
    filtered_molecules_no_value = [] # here the molecules whose value could not be find are stored
    filtered_molecules_discarted = [] # here the molecules that did not pass the filter are stored
    filtered_molecules_joined = [] # here the combination of the molecules that passed the filter and whose value could not be find

    # the csv I pass has multiple columns. Out of these the 4th contains the formulas 
    for index, row in df.iterrows(): # iterate through the rows of the csv file
        formula = row.iloc[3]  # gets the formula present in the 4th column
        
        try: # it may not be possible to get the Quadrupole moment from the server so we use "try"

            quadrupole_moment = get_quadrupole_moment(formula) # call the get_quadrupole_moment function
            
            # check if Quadrupole moment is above 0.5
            if quadrupole_moment is None: # if the output of the quadrupole search is None
                filtered_molecules_no_value.append(row) # append the row that was read to the now value array
                filtered_molecules_joined.append(row) # appens the row that was read to the joined array
                print(f"{formula}: Quadrupole moment = {quadrupole_moment} - NONE PASSED") # notify the user that the molecule has passed the filter with NONE value
            if quadrupole_moment is not None and abs(quadrupole_moment) >= 0.5: #  if the output value is bigger than 0.5
                print(f"{formula}: Quadrupole moment = {quadrupole_moment} - PASSED") # notify the user that the molecule has passed the filter
                row_with_quadrupole = row.copy() # copies the current row
                row_with_quadrupole["Quadrupole moment"] = quadrupole_moment # adds the Quadrupole moment value to the row
                filtered_molecules_joined.append(row_with_quadrupole) # append the row that was read to the joined array
                filtered_molecules_good.append(row_with_quadrupole) # append the row that was read to the good array
            if quadrupole_moment is not None and abs(quadrupole_moment) <0.5: # if the output value is not bigger than 0.5
                row_with_quadrupole = row.copy() # copies the current row
                row_with_quadrupole["Quadrupole moment"] = quadrupole_moment
                print(f"{formula}: Quadrupole moment = {quadrupole_moment} - FILTERED OUT") # notifify the user that the molecule has not passed the filter
                filtered_molecules_discarted.append(row_with_quadrupole) # append the row that was read to the discarted array
            # add a delay to avoid overwhelming the server
            time.sleep(delay)
        
        # in case it is not possible to call the function or if there is a network problem
        except Exception as e:
            print(f"Error processing {formula}: {e}")
    
    # create a new DataFrame with filtered molecules
    filtered_df_good = pd.DataFrame(filtered_molecules_good)
    filtered_df_no_value = pd.DataFrame(filtered_molecules_no_value)
    filtered_df_discarted = pd.DataFrame(filtered_molecules_discarted)
    filtered_df_joined = pd.DataFrame(filtered_molecules_joined)
    
    # converts the dataframe to a csv false
    # by default pandas assigns an integer index to each row when creating a dataframe which produces an extra column. Since we do not want that we set index to false
    filtered_df_good.to_csv(output_csv_good, index=False) 
    filtered_df_no_value.to_csv(output_csv_no_value, index=False)
    filtered_df_discarted.to_csv(output_csv_discarted, index=False)
    filtered_df_joined.to_csv(output_csv_joined, index=False)
    
    # user notification
    print(f"Total molecules processed: {len(df)}")
    print(f"Molecules passing filter: {len(filtered_molecules_good)}")
    print(f"Molecules NOT passing filter: {len(filtered_molecules_discarted)}")
    print(f"Molecules with no Quadrupole moment found: {len(filtered_molecules_no_value)}")

# calling the filter_molecules_by_quadrupole function
filter_molecules_by_quadrupole("molecule_filter_TOC/no_symmetry_restriction/filter_1_quadrupole_no_values_v2.csv", 'molecule_filter_TOC/no_symmetry_restriction/filter_1_quadrupole_good_v3.csv', 'molecule_filter_TOC/no_symmetry_restriction/filter_1_quadrupole_no_values_v3.csv', 'molecule_filter_TOC/no_symmetry_restriction/filter_1_quadrupole_discarted_v3.csv', 'molecule_filter_TOC/no_symmetry_restriction/filter_1_quadrupole_joined_v3.csv')