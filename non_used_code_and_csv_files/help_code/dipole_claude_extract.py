import requests
from bs4 import BeautifulSoup

def search_and_extract_dipole(formula='H2O'):
    # Base URL
    base_url = 'https://cccbdb.nist.gov'
    
    # Headers
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.7',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://cccbdb.nist.gov',
        'referer': 'https://cccbdb.nist.gov/dipole1x.asp',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }
    
    # Prepare session and cookies
    session = requests.Session()
    
    try:
        # First, get the initial page to establish session
        session.get('https://cccbdb.nist.gov/dipole1x.asp')
        
        # POST request to getformx.asp with the formula
        response = session.post(
            f'{base_url}/getformx.asp', 
            headers=headers, 
            data={'formula': formula, 'submit1': 'Submit'},
            allow_redirects=True
        )
        
        # Get the dipole page
        dipole_response = session.get(f'{base_url}/dipole2x.asp', headers=headers)
        
        # Parse the HTML
        soup = BeautifulSoup(dipole_response.text, 'html.parser')
        
        # Find the table with id="table2"
        table2 = soup.find('table', id='table2')
        
        if table2:
            # Find the row with HF method
            hf_th = table2.find('th', class_='nowrap', string=lambda text: text and 'HF' in text)
            
            if hf_th:
                # Find the corresponding TD with the link
                hf_td = hf_th.find_next('td', class_='num bordered')
                
                if hf_td and hf_td.a:
                    # Extract the value from the link
                    value = hf_td.a.text.strip()
                    print(f"HF Dipole value for {formula}: {value}")
                    return value
                else:
                    print("Could not find the value in the TD element")
            else:
                print("Could not find HF method row")
        else:
            print("Could not find table2")
        
        return None
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Execute the search and extraction for H2O
results = search_and_extract_dipole('HCl')