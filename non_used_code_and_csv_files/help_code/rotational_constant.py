# import necessary libraries
import requests # this is a library that allows to send HTTP requests to websites. Simulates what a browser does when fetching web content
from bs4 import BeautifulSoup # from the bs4 module imports the class beautifulsoup. This is used to parse HTML or XML content and extract information from it
import csv # this imports the csv module. It is used to read and write CSV files
import pandas as pd # this imports the pandas library and it is giving it the alias pd that is used for data manipulation and analaysis
import time # this imports the time module which is used to measure how long things run or to pause an execution
import re # import the re module used to work with regular expressions (regex) used for stringmatching, extracting and replacing patterns


# this function searches for the rotational consatn in the cccbdb webpage
# the function needs as an input the chemical formula of the compound 
# the function outputs the rotational constant if found and "None" if the rotational constant is not found
def get_rotational_constant(formula): # define the function

    print(f"Checking rotational constant for molecule: {formula}") # the cccbdb webpage is quite slow. This allows to track the search process when dealing with multiple moelcular formulas
    
    
    base_url = 'https://cccbdb.nist.gov' # url of the cccbdb webpage
    
    # define the headers: this is information that will be sent when making an HTTP request. If they are not properly defined the request to the server will likely fail. 
    # the header info I got from the developer tools in the network section from the first asp
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', # tells the server what type of content we want, in this case: HTML,XHTML and XML
        'accept-language': 'en-US,en;q=0.7', # specifies the prefered language for the content in our case english
        'cache-control': 'max-age=0', #  defines how caching should work, in this case we do not cache the response
        'content-type': 'application/x-www-form-urlencoded', # defines what type of data is being sent: in our case URL enconded data   
        'origin': 'https://cccbdb.nist.gov', # specifies the origin of the requesting page
        'referer': 'https://cccbdb.nist.gov/exp1x.asp', # specifies the full URL from which the request is being made. When extracting data from cccbdb this is the paramter to change
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36' # identifies the client making the request. 
    }
    
    # Prepare session and cookies
    session = requests.Session() # allows to mantain parameters of the search. In our case is important to keep the headers the same
    
    try: # the server info request may fail, the try allows to handle the cases where it works and the exceptions allow to handle cases when it does not work
        
        session.get('https://cccbdb.nist.gov/exp1x.asp') # request information to the dipole calculation page of the cccbdb
        
        # we make a post request: HTTP request to submit data to a server
        response = session.post(
            f'{base_url}/getformx.asp', # this is the URL to which the request is being sent. This I got by checking the network developer tools when doing the search request in the browser
            headers=headers, # adds the headers we defined before to the request, specifiying exactly what info we want
            data={'formula': formula, 'submit1': 'Submit'}, # this is the data we are sending with the request: the formula and the submit option
            allow_redirects=True # the server may redirect our request. this allows for the redirects
        )
        
        # we get the data that the server returns to us
        rot_constant_response = session.get(f'{base_url}/exp2x.asp', headers=headers) # here the url from which the data want to be get and the headers we used for the initial request. this I got from the second asp in the developer tools in the network section
        
        # parse the HTML to be able to search in it
        soup = BeautifulSoup(rot_constant_response.text, 'html.parser') # we parse the text (. text) of the info that the server sent us with the get
        
        # when looking at the source page one can see that the rotational constant is present in a div container of a class box that has the tittle "Rotational Constants"
        div = soup.find('div', class_ = 'box', title = "Rotational Constants") # this searches for the container where the rotational value is

        # if the rotational value is found
        if div: 
            text_div = div.get_text() # convert in text everything that is contained in the div container
            # searches for a given pattern in the text of the div container. 
            # r: raw string (treats backslashes as literal characters)
            # \b: word boundary anchor which indicates where the word starts and ends
            # \d+ finds the digits before the decimal point 
            # \. finds the decimal point 
            # \d+ finds the digits after the decimal point
            match = re.search(r'\b\d+\.\d+\b', text_div) 
        
            if match:#checks if there is a value that matches the conditions of match
                value = match.group(0) # extracts the text of the match object and stores it into the variable "value"
                # try to convert the value into a float
                try:
                    value_float = float(value) # converts the value into a float
                    print (f"The rotational constant for {formula} is {value_float}")
                    return value_float
                # in case it is not possible to convert it in a float:
                except ValueError: 
                    print (f"It was not possible to convert the value of {formula} into a float")
                    return None
            else:
                print (f"No value was found for the rotational constant of {formula}")

    # in case the request to the server fails
    except Exception as e:
        print(f"An error occurred for {formula}: {e}")
        return None


# this function loops over all the formulas present in the csv file with the initially filtered molecules and applies to all of them the get_rotational_constant function to retrieve their rotational constants
# the function needs 3 inputs, the csv file where the molcular formulas are stored, the name and path where to store the filtered csv file and the delay time one should wait between processing two consecutive molecules to avoid overwhelming the server
def filter_molecules_by_dipole(input_csv, output_csv, delay=1): # function definition
   
    # read the input CSV
    df = pd.read_csv(input_csv)
    
    # create a list to store molecules that pass the filter
    filtered_molecules = []

    # the csv I pass has multiple columns. Out of these the 4th contains the formulas 
    for index, row in df.iterrows(): # iterate through the rows of the csv file
        formula = row.iloc[2]  # gets the formula present in the 4th column
        
        try: # it may not be possible to get the dipole moment from the server so we use "try"

            rot_constant = get_rotational_constant(formula) # call the get_dipole_moment function
            if rot_constant:
                 filtered_molecules.append(row) # append the row that was read to the new array
            time.sleep(delay)
        
        # in case it is not possible to call the function or if there is a network problem
        except Exception as e:
            print(f"Error processing {formula}: {e}")
    
    # create a new DataFrame with filtered molecules
    filtered_df = pd.DataFrame(filtered_molecules)
    
    # converts the dataframe to a csv false
    filtered_df.to_csv(output_csv, index=False) # by default pandas assigns an integer index to each row when creating a dataframe which produces an extra column. Since we do not want that we set index to false
    
    # user notification
    print(f"\nFiltered CSV saved to {output_csv}")
    print(f"Total molecules processed: {len(df)}")
    print(f"Molecules passing filter: {len(filtered_molecules)}")

# calling the filter_molecules_by_dipole function
filter_molecules_by_dipole('molecule_filter_TOC/no_symmetry_restriction/filter1_properties_no_symmetry_no_duplicates.csv', 'molecule_filter_TOC/no_symmetry_restriction/calc_rotational_constant')