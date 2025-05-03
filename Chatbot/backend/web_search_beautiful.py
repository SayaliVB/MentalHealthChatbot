import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join(p.get_text(strip=True) for p in paragraphs[:10])  # Limit to top 10 paragraphs

        return content if content else "No relevant content found."

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return "Error occurred while scraping website."


def fetch_top_result_duckduckgo(query):
    print(f"🔍 Searching DuckDuckGo for: {query}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if results:
            print(f"✅ Found URL: {results[0]['href']}")
            return results[0]['href']
        else:
            print("❌ No search results found.")
            return None
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return None

def web_search(query):
    top_url = fetch_top_result_duckduckgo(query)
    if not top_url:
        return "No search results found."

    return scrape_website(top_url)


def main():
    query = input("Enter your query: ").strip()
    response = web_search(query)
    print("\n📄 Response:\n")
    print(response)


if __name__ == "__main__":
    main()