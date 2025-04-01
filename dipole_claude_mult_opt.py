from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import time

# --- Setup Selenium WebDriver ---
# Replace with your own path to chromedriver if needed
service = Service('chromedriver')  # or give full path like '/path/to/chromedriver'
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Optional: run without opening browser window
driver = webdriver.Chrome(service=service, options=options)

# --- Load the webpage ---
url = "https://cccbdb.nist.gov/dipole1x.asp"
driver.get(url)
time.sleep(2)  # Let page load

# --- Get the table ---
table = driver.find_element(By.XPATH, '//table[1]')
rows = table.find_elements(By.TAG_NAME, 'tr')

# --- Parse data ---
data = []
headers = [th.text.strip() for th in rows[0].find_elements(By.TAG_NAME, 'th')]

for row in rows[1:]:
    cells = row.find_elements(By.TAG_NAME, 'td')
    if len(cells) == len(headers):
        values = [cell.text.strip() for cell in cells]
        data.append(dict(zip(headers, values)))

# --- Convert to DataFrame and save ---
df = pd.DataFrame(data)
df.to_csv('nist_dipole_moments.csv', index=False)
print("Saved data to nist_dipole_moments.csv")

# --- Done ---
driver.quit()
