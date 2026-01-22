MOLECULE FILTRATION



Python scripts for filtering and analysing molecular datasets. 

The workflow processes vibrational data and selects molecules based on symmetry, dipole, and quadrupole moments.



---------------------------------------------------------------

SCRIPTS OVERVIEW



Script                               Purpose

------                               -------

html\_to\_csv.py                        Converts raw vibrational data from HTML to CSV.

filter\_for\_ions\_and\_radicals.py       Removes ions, radicals, dimers, and trimers. 

&nbsp;                                     Assumes a column exists indicating charge or ionic nature 

&nbsp;                                     and checks molecule names for "dimer" or "trimer".

remove\_doubled\_formulas.py            Keeps only one vibration per molecule by checking chemical formulas 

&nbsp;                                     and retaining the first occurrence.

get\_point\_group\_from\_cccbdb.py        Parses the NIST CCCBDB website to obtain the point group 

&nbsp;                                     of molecules listed in an input CSV file.

filter\_point\_group.py                 Filters molecules in a CSV file based on their point group.

rotational\_constant.py                Parses the NIST CCCBDB website to obtain rotational constants 

&nbsp;                                     of molecules in an input CSV file.

prolate\_oblate\_check.py               Classifies molecules as prolate, oblate, or linear based on the 

&nbsp;                                     number and values of their rotational constants.

filter\_dipole.py                      Parses the NIST CCCBDB website to obtain dipole moments 

&nbsp;                                     and filters molecules based on dipole values.

fraction\_calculator.py                Calculates the fraction (dipole^2 / rotational constant) 

&nbsp;                                     for molecules that have both values.

filter\_quadrupole.py                  Parses the NIST CCCBDB website to obtain quadrupole moments 

&nbsp;                                     and filters molecules based on quadrupole values.



---------------------------------------------------------------

REQUIREMENTS



Python: 3.9+ recommended

Ensure pip is installed



Python Libraries:



Library                Purpose                                  Install

-------                -------                                  -------

pandas                 Reading/writing CSV files, DataFrame     pip install pandas

&nbsp;                      operations

numpy                  Numerical computations                   pip install numpy

requests               Sending HTTP requests for web scraping  pip install requests

beautifulsoup4         Parsing HTML pages                       pip install beautifulsoup4

lxml / html5lib        Recommended HTML parser for BeautifulSoup pip install lxml html5lib

re                     Regular expressions (built-in)          -

time                   Delays between requests (built-in)      -

csv                    Reading/writing CSV files (built-in)    -

os                     File system path handling (built-in)    -



---------------------------------------------------------------

NOTES



\- All web scraping scripts rely on CCCBDB/NIST database pages. Internet access is required.



