from bs4 import BeautifulSoup
import pandas as pd

path = "molecule_filter_TOC/frequency_filter.html"

data = []

# Get table header
list_header = []  # creates an empty array
with open(path, encoding="utf-8") as file:  # open with utf-8 encoding. In my PC this is needed because otherwise the character "Σ" cannot be read
    soup = BeautifulSoup(file, 'html.parser')  # parses through the html file
header = soup.find_all("table")[1].find("tr")  # gets the first table from the HTML file, and searches for all rows skipping the first one
for items in header:
    list_header.append(items.get_text())  # loops over the elements of the first row of the table and adds them to list_header
# BeautifulSoup includes all elements inside the <tr> or <th> tag, including newline characters ("\n"). One has to remove them
headers = [list_header[i] for i in [1, 3, 5, 7, 9, 11, 13]]  # checks the elements in list_header and only extracts the ones in positions 1,3,5 ...

# Get table data
HTML_data = soup.find_all("table")[1].find_all("tr")[1:]  # gets the first table from the HTML file, and searches for all rows skipping the first one
for element in HTML_data:  # loops over each row on the table
    sub_data = []  # creates an empty array
    # loops over each element in the selected row
    for sub_element in element:
        sub_data.append(sub_element.get_text())  # adds each element of the row in the sub_data array
    data.append(sub_data)  # adds the sub_data array to the data array to merge it with the header
# BeautifulSoup includes all elements inside the <tr> or <th> tag, including newline characters ("\n"). One has to remove them
data = list(map(lambda x: [x[1], x[3], x[5], x[7], x[9], x[11], x[13]], data))  # extracts uneven elements of the rows present in data and overwrites data with them

# Filter out ions and high symmetry groups
data_clean = []  # makes an empty array
# loops over each row in data
for item in data:
    # filters for anions, cations, radicals, dimers, trimers, tetramers and based on symmetry
    if not ("anion" in item[1] or "cation" in item[1] or "radical" in item[1] or "dimer" in item[1] or "trimer" in item[1] or "tetramer" in item[1] or "diatomic" in item[1] or "-" in item[2] or "+" in item[2]):  # checks if any of these elements are present in the 2nd column of data and the symmetry in the 4th column
        data_clean.append(item)  # in case they are not, the corresponding row is stored

df = pd.DataFrame(data_clean, columns=headers, index=pd.RangeIndex(start=1, stop=len(data_clean) + 1, name='Candidate #'))

# Write the CSV with 'utf-8-sig' encoding to ensure proper symbol handling
output_path = "molecule_filter_TOC/filter1_properties_no_symmetry.csv"
df.to_csv(output_path, encoding="utf-8-sig") # This is also needed because otherwise excel does not recognise the utf-8-sig encoding and thus does not read "Σ"
