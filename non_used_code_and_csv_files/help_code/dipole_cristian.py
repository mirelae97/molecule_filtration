import requests

def get_dipole_cccbdb(chem_name):
    # Form action endpoint (not the form page itself)
    url_cccbdb = "https://cccbdb.nist.gov/getformx.asp"

    # Data to use for the search
    data = {
        "formula": chem_name,
        "submit1": "Submit"
    }

    # Headers
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://cccbdb.nist.gov",
        "Referer": "https://cccbdb.nist.gov/dipole2x.asp",
        "Sec-Ch-Ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Sec-Gpc": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }

    # Optional: Set cookies (from your session or browser if needed)
    cookies = {
        "ASPSESSIONIDCCRRDQBT": "NGMIACMCDKJPDADNEEHCINFM",
        "__cf_bm": "R5Fqf3KwisdyQZI2dB6KwUarNywO41FySgRlSH_nTfY-1743106449-1.0.1.1-u4tWBZZ2iHUobNG4PGmVz6EBAH0.m_uZ0O3lF4VzTYUXgWkG4e8vAAhXwva2Hn69ZogR6XIqcgHyGUs.aetTRMGdg3EOlj2Oo0lemO99X60"
    }

    # Make the request
    response = requests.post(url_cccbdb, headers=headers, cookies=cookies, data=data)

    # Save the response content to a file
    with open("tabla.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    return response.text

# Example usage
banana = get_dipole_cccbdb("H2O")
print("HTML response saved to tabla.html") 