import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('p')  # Modify this to target relevant sections
        
        return content.text if content else "No relevant content found."
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return "Error occurred"

def search_bing(query):
    # Placeholder for Bing API integration
    print(f"Using Bing API as fallback for: {query}")
    return "Bing search results here."

def fetch_information(query, sources):
    results = {}
    for site, url in sources.items():
        content = scrape_website(url)
        if content == "Error occurred":
            content = search_bing(query)
        results[site] = content
    return results

# Example queries and sources
queries = {
    "how to manage anxiety": {
        "Mayo Clinic": "https://www.mayoclinic.org/diseases-conditions/anxiety/symptoms-causes/syc-20350961",
        "WebMD": "https://www.webmd.com/anxiety-panic/guide/anxiety-disorders",
        "Healthline": "https://www.healthline.com/health/anxiety"
    },
    "best ways to handle depression": {
        "Mayo Clinic": "https://www.mayoclinic.org/diseases-conditions/depression/symptoms-causes/syc-20356007",
        "WebMD": "https://www.webmd.com/depression/guide/depression-symptoms-and-types",
        "Healthline": "https://www.healthline.com/health/depression"
    }
}

for query, sources in queries.items():
    print(f"\nResults for: {query}")
    results = fetch_information(query, sources)
    for site, summary in results.items():
        print(f"\nSite: {site}\nSummary: {summary}")
