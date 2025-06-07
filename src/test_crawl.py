from crawl4ai import AsyncWebCrawler
import asyncio
import pandas as pd

async def scrape_news(urls):
    results = []
    async with AsyncWebCrawler() as crawler:
        for url in urls:
            try:
                result = await crawler.arun(url=url, extraction_strategy="llm")
                results.append(result)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
    return results

def process_scraped_data(scraped_data):
    # Convert scraped data to a DataFrame for rumourCheck
    data = [
        {
            "title": item.title if hasattr(item, 'title') else "",
            "text": item.extracted_content if hasattr(item, 'extracted_content') else "",
            "source": item.url if hasattr(item, 'url') else ""
        } for item in scraped_data if item
    ]
    df = pd.DataFrame(data)
    df["full_text"] = df["title"] + " " + df["text"]
    df["label"] = df["source"].apply(lambda x: 1 if "bbc" in x.lower() else 0)  # Example labeling
    return df

def main():
    urls = ["https://www.bbc.com", "https://clickhole.com"]
    scraped_data = asyncio.run(scrape_news(urls))
    if scraped_data:
        df = process_scraped_data(scraped_data)
        print("Scraped DataFrame:")
        print(df.head())
        # Optionally save to CSV for rumourCheck
        df.to_csv("../dataset/scraped_news.csv", index=False)
        print("Data saved to ../dataset/scraped_news.csv")
    else:
        print("No data scraped.")

if __name__ == "__main__":
    main()