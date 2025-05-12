"""
Simple test scraper to verify your setup works correctly
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def simple_scraper():
    """
    A very simple scraper to verify everything is working
    """
    print("Simple Scraper Test")
    print("===================")
    
    # Target a simple, scraping-friendly website
    url = "http://quotes.toscrape.com/"
    print(f"Fetching data from: {url}")
    
    # Send HTTP request
    response = requests.get(url)
    
    if response.status_code == 200:
        print("Connection successful!")
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract quotes
        quotes = []
        for quote in soup.select(".quote"):
            text = quote.select_one(".text").get_text()
            author = quote.select_one(".author").get_text()
            tags = [tag.get_text() for tag in quote.select(".tag")]
            
            quotes.append({
                "text": text,
                "author": author,
                "tags": ", ".join(tags)
            })
        
        # Convert to DataFrame
        df = pd.DataFrame(quotes)
        
        # Print results
        print(f"\nSuccessfully extracted {len(quotes)} quotes.")
        print("\nSample data:")
        print(df.head(3))
        
        # Export to CSV
        filename = f"scraped_data/quotes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"\nData exported to {filename}")
        
        return df
    else:
        print(f"Error: Received status code {response.status_code}")
        return None

if __name__ == "__main__":
    simple_scraper()