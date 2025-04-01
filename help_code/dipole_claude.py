import requests

def search_nist_database(formula='H2O'):
    # Base URL
    base_url = 'https://cccbdb.nist.gov'
    
    # Detailed headers to mimic the browser request
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.7',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',  # Changed from 'text/html'
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
        
        # Check if request was successful
        if response.status_code in [200, 302]:
            # Attempt to get the dipole page
            dipole_response = session.get(f'{base_url}/dipole2x.asp', headers=headers)
            
            # Save the response to a file
            with open('dipole_results.html', 'w', encoding='utf-8') as f:
                f.write(dipole_response.text)
            
            print(f"Search for {formula} completed. Results saved to dipole_results.html")
            return dipole_response.text
        else:
            print(f"Request failed. Status code: {response.status_code}")
            return None
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Execute the search for H2O
results = search_nist_database('H2O')