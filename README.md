# Molecule Filtration

Python scripts for filtering and analyzing molecular datasets.  
The workflow processes vibrational data and selects molecules based on symmetry, dipole, and quadrupole moments.

---

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `html_to_csv.py` | Converts raw vibrational data from HTML to CSV. |
| `filter_for_ions_and_radicals.py` | Removes ions, radicals, dimers, and trimers. Assumes a column indicates charge or ionic nature and checks molecule names for "dimer" or "trimer". |
| `remove_doubled_formulas.py` | Keeps only one vibration per molecule by checking chemical formulas and retaining the first occurrence. |
| `get_point_group_from_cccbdb.py` | Parses the NIST CCCBDB website to obtain the point group of molecules listed in an input CSV file. |
| `filter_point_group.py` | Filters molecules in a CSV file based on their point group. |
| `rotational_constant.py` | Parses the NIST CCCBDB website to obtain rotational constants of molecules in an input CSV file. |
| `prolate_oblate_check.py` | Classifies molecules as prolate, oblate, or linear based on the number and values of their rotational constants. |
| `filter_dipole.py` | Parses the NIST CCCBDB website to obtain dipole moments and filters molecules based on dipole values. |
| `fraction_calculator.py` | Calculates the fraction (dipole² / rotational constant) for molecules that have both values. |
| `filter_quadrupole.py` | Parses the NIST CCCBDB website to obtain quadrupole moments and filters molecules based on quadrupole values. |

---

## Requirements

**Python:** 3.9+ recommended  
Ensure `pip` is installed.

### Python Libraries

| Library | Purpose | Install |
|---------|--------|--------|
| pandas | Reading/writing CSV files, DataFrame operations | `pip install pandas` |
| numpy | Numerical computations | `pip install numpy` |
| requests | Sending HTTP requests for web scraping | `pip install requests` |
| beautifulsoup4 | Parsing HTML pages | `pip install beautifulsoup4` |
| lxml / html5lib | Recommended HTML parser for BeautifulSoup | `pip install lxml html5lib` |
| re | Regular expressions (built-in) | - |
| time | Delays between requests (built-in) | - |
| csv | Reading/writing CSV files (built-in) | - |
| os | File system path handling (built-in) | - |

---

## Notes

- All web scraping scripts rely on CCCBDB/NIST database pages. Internet access is required.
