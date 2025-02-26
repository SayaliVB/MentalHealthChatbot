import requests
import re
import asyncio
import aiohttp

# Replace with your actual Bing Search API key
BING_API_KEY = "YOUR_BING_API_KEY"
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"

# Cached results to avoid redundant API calls
cache = {}

def clean_text(text):
    """Removes unnecessary characters and formats extracted content."""
    return re.sub(r'\s+', ' ', re.sub(r'\[.*?\]', '', text)).strip()

async def fetch_results_async(session, query):
    """Asynchronously fetch web search results from Bing API."""
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 5}  # Fetch only top 5 results for efficiency

    async with session.get(BING_SEARCH_URL, headers=headers, params=params) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("webPages", {}).get("value", [])
        return []

async def fetch_web_results(query, sites=None):
    """
    Fetches web search results asynchronously from Bing API with site-specific filtering.
    
    Parameters:
    - query (str): Search query
    - sites (list): List of specific websites to search from (optional)

    Returns:
    - List of cleaned search results
    """
    global cache
    
    # Check cache to avoid redundant API calls
    if query in cache:
        return cache[query]

    # Modify query for site-specific search
    if sites:
        site_query = " OR ".join([f"site:{site}" for site in sites])
        query = f"{query} ({site_query})"

    async with aiohttp.ClientSession() as session:
        results = await fetch_results_async(session, query)
    
    # Extract relevant information
    search_results = [
        {"title": res["name"], "url": res["url"], "snippet": clean_text(res.get("snippet", ""))}
        for res in results
    ]

    # Cache results
    cache[query] = search_results

    return search_results if search_results else [{"error": "No relevant data found."}]

async def run_tests():
    """Runs test cases to verify API functionality."""
    test_cases = [
        ("Latest research on anxiety treatment", ["mayoclinic.org", "nih.gov", "webmd.com"]),
        ("Best exercises for back pain", ["who.int", "nih.gov"]),
        ("Mental health support resources", None),
        ("Benefits of intermittent fasting", ["healthline.com", "medicalnewstoday.com"]),
    ]

    for query, sites in test_cases:
        print(f"\n **Searching for:** {query}")
        if sites:
            print(f" **Specific Sites:** {', '.join(sites)}")

        results = await fetch_web_results(query, sites)
        
        for res in results:
            if "error" in res:
                print(f" {res['error']}")
            else:
                print(f"{res['title']} ({res['url']})\n{res['snippet']}\n")

async def main():
    """Main function to run search and test cases."""
    print(" Running Bing Search API tests...\n")
    await run_tests()

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
