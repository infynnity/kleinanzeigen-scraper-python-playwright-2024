import asyncio
import random
import logging
import threading
import json
from datetime import datetime
from playwright.async_api import async_playwright
import re
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("scraping.log"),
    logging.StreamHandler()
])

class Scraper:
    def __init__(self):
        self.stop_scraping = False

    def listen_for_stop(self):
        input("Press Enter to stop scraping...\n")
        self.stop_scraping = True

    def extract_page_number(self, url):
        # Extract the page number from the given URL, assuming page 1 if not found
        if "seite:" in url:
            parts = url.split('/')
            for part in parts:
                if part.startswith("seite:"):
                    return int(part.split(':')[1])
        return 1

    def generate_urls(self, first_url, second_url, num_urls):
        # Extract the base URL and search term
        base_url = first_url.split('/s-')[0] + '/s-'
        search_parts = first_url.split('/s-')[1].split('/')
        search_term = search_parts[0]

        # Extract additional search modifiers if present
        search_modifiers = []
        if len(search_parts) > 1:
            search_modifiers = search_parts[1:]

        # Extract the starting page number from the first URL
        start_page = self.extract_page_number(first_url)
        # Extract the next page number from the second URL
        next_page = self.extract_page_number(second_url)

        # Determine the starting page number based on the second URL
        if start_page == 1 and next_page > 1:
            start_page = next_page - 1

        # Generate the next URLs
        urls = []
        for i in range(next_page + 1, next_page + 1 + num_urls):
            url = f"{base_url}"
            url += f"seite:{i}/{search_term}"
            if search_modifiers:
                url += "/" + "/".join(search_modifiers)
            urls.append(url)

        return urls


    async def scrape_page(self, page, url, item_number):
        await page.goto(url, wait_until="networkidle")
        items = await page.query_selector_all('.aditem')
        data = []
        for item in items:
            try:
                title_element = await item.query_selector('.text-module-begin a')
                title_text = await title_element.inner_text() if title_element else 'No Title'
                product_link = await title_element.get_attribute('href') if title_element else 'No Link'
                product_link = f"https://www.kleinanzeigen.de{product_link}" if product_link else 'No Link'
            except Exception as e:
                logging.error(f"Error extracting title or link: {e}")
                title_text = 'No Title'
                product_link = 'No Link'
            
            try:
                price = await item.query_selector('.aditem-main--middle--price-shipping--price')
                price_text = await price.inner_text() if price else 'No Price'
            except Exception as e:
                logging.error(f"Error extracting price: {e}")
                price_text = 'No Price'
            
            try:
                location = await item.query_selector('.aditem-main--top--left')
                location_text = await location.inner_text() if location else 'No Location'
            except Exception as e:
                logging.error(f"Error extracting location: {e}")
                location_text = 'No Location'
            
            try:
                date_created = await item.query_selector('.aditem-main--top--right')
                date_created_text = await date_created.inner_text() if date_created else 'No Date'
            except Exception as e:
                logging.error(f"Error extracting date created: {e}")
                date_created_text = 'No Date'
            
            data.append({
                'item_number': item_number,
                'title': title_text,
                'link': product_link,
                'price': price_text,
                'location': location_text,
                'date_created': date_created_text
            })
            item_number += 1
        return data, item_number

    def calculate_price_stats(self, data):
        prices = []
        negotiable_prices_count = 0
        date_created_list = []
        for item in data:
            price_text = item['price']
            if '€' in price_text:
                try:
                    price = float(re.sub(r'[^\d,]', '', price_text).replace(',', '.'))
                    prices.append(price)
                    if 'VB' in price_text:
                        negotiable_prices_count += 1
                except ValueError as e:
                    logging.error(f"Error converting price: {e}")
            if item['date_created']:
                date_created_list.append(item['date_created'])
        
        if not prices:
            return 0, 0, 0, 0, 0, len(data), None, None

        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)
        total_items = len(prices)
        date_range = (min(date_created_list), max(date_created_list)) if date_created_list else (None, None)
        return avg_price, max_price, min_price, total_items, negotiable_prices_count, len(data), date_range


    async def main(self):
        # User input for the first two URLs
        first_url = input("Enter the URL for page 1: ")
        second_url = input("Enter the URL for page 2: ")
        num_pages = int(input("Enter the number of pages to scrape: "))

        # Generate the next URLs
        generated_urls = self.generate_urls(first_url, second_url, num_pages)
        if not generated_urls:
            logging.error("Failed to generate URLs. Please check the provided URLs.")
            return

        # Save the URLs to a text file
        with open("urls.txt", "w") as file:
            file.write(f"{first_url}\n{second_url}\n")
            for url in generated_urls:
                file.write(f"{url}\n")

        # Extract the search term from the URL
        search_term = first_url.split('/s-')[1].split('/')[0]

        # Get the current date and time for the filename
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Start the thread to listen for stop input
        stop_thread = threading.Thread(target=self.listen_for_stop)
        stop_thread.start()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            all_data = []
            item_number = 1

            # Initialize the progress bar
            total_urls = len([first_url, second_url] + generated_urls)
            with tqdm(total=total_urls, desc="Scraping Progress") as progress_bar:
                for idx, url in enumerate([first_url, second_url] + generated_urls, start=1):
                    if self.stop_scraping:
                        logging.info("Stopping scraping as requested by the user.")
                        break

                    logging.info(f"Scraping URL: {url} (Page {idx})")
                    progress_bar.set_postfix(current_page=idx)
                    progress_bar.update(1)
                    try:
                        data, item_number = await self.scrape_page(page, url, item_number)
                        if not data:
                            logging.info(f"No data found on {url}. Ending scraping.")
                            break
                        all_data.extend(data)
                        logging.info(f"URL {url} scraped successfully with {len(data)} items.")
                        
                        delay = random.uniform(2, 5)
                        logging.info(f"Sleeping for {delay:.2f} seconds.")
                        await asyncio.sleep(delay)
                        
                    except Exception as e:
                        logging.error(f"Failed to scrape {url}: {e}")
                        break

            await browser.close()

            # Save data to JSON file with appropriate filename
            filename_base = f"{search_term}_{current_time}_p{idx}"
            json_filename = f"{filename_base}.json"
            with open(json_filename, "w") as f:
                json.dump(all_data, f, indent=2)

            # Calculate price statistics
            avg_price, max_price, min_price, total_items, negotiable_prices_count, total_listings, date_range = self.calculate_price_stats(all_data)
            logging.info(f"Average Price: {avg_price}, Highest Price: {max_price}, Lowest Price: {min_price}")

            info = (
                f"Average Price: {avg_price:.2f} €\n"
                f"Highest Price: {max_price:.2f} €\n"
                f"Lowest Price: {min_price:.2f} €\n"
                f"Total Items with Price: {total_items}\n"
                f"Total Listings with Negotiable Prices: {negotiable_prices_count}\n"
                f"Total Listings: {total_listings}\n"
                f"Date Range of Listings: {date_range[0]} to {date_range[1]}\n"
            )
            
            # Save statistics to a text file with the same base name as the JSON file
            info_filename = f"{filename_base}_info.txt"
            with open(info_filename, "w") as f:
                f.write(info)

            logging.info(f"Data saved to {json_filename}")
            logging.info(f"Statistics saved to {info_filename}")
            
            # Display the contents of the info file
            print("\nScraping Summary:\n")
            print(info)

if __name__ == "__main__":
    scraper = Scraper()
    asyncio.run(scraper.main())
