import json
import asyncio
import logging
import threading
from datetime import datetime
from playwright.async_api import async_playwright
from tqdm import tqdm
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("detailed_scraping.log"),
    logging.StreamHandler()
])

class Scraper:
    def __init__(self):
        self.stop_scraping = False

    def listen_for_stop(self):
        input("Press Enter to stop scraping...\n")
        self.stop_scraping = True

async def scrape_product_page(page, url):
    await page.goto(url, wait_until="networkidle")
    try:
        logging.debug(f"Scraping {url}")
        
        # Title
        title_element = await page.query_selector('h1')
        title_text = await title_element.inner_text() if title_element else 'No Title'
        logging.debug(f"Title: {title_text}")

        # Price
        price_element = await page.query_selector('span.price')
        price_text = await price_element.inner_text() if price_element else 'No Price'
        logging.debug(f"Price: {price_text}")
        
        # Description
        description_element = await page.query_selector('div#viewad-description')
        description_text = await description_element.inner_text() if description_element else 'No Description'
        logging.debug(f"Description: {description_text}")

        # Location
        location_element = await page.query_selector('span#viewad-locality')
        location_text = await location_element.inner_text() if location_element else 'No Location'
        logging.debug(f"Location: {location_text}")

        # Date Posted
        date_posted_element = await page.query_selector('span#viewad-extra-info')
        date_posted_text = await date_posted_element.inner_text() if date_posted_element else 'No Date Posted'
        logging.debug(f"Date Posted: {date_posted_text}")

        # Seller Username
        seller_username_element = await page.query_selector('.text-body-regular-strong.text-force-linebreak.userprofile-vip a')
        seller_username_text = await seller_username_element.inner_text() if seller_username_element else 'No Seller Username'
        logging.debug(f"Seller Username: {seller_username_text}")

        return {
            'url': url,
            'title': title_text,
            'price': price_text,
            'description': description_text,
            'location': location_text,
            'date_posted': date_posted_text,
            'seller_username': seller_username_text
        }
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return None

async def main():
    scraper = Scraper()

    # Load the JSON file with product links
    input_file = input("Enter the path to the JSON file with product links: ").strip()

    # Validate the input file path
    if not os.path.isfile(input_file):
        print(f"The file '{input_file}' does not exist. Please provide a valid file path.")
        return

    with open(input_file, "r") as f:
        products = json.load(f)

    # Extract the links
    product_links = [product['link'] for product in products if 'link' in product]

    # Prompt user for number of links to scrape
    while True:
        num_links_str = input(f"There are {len(product_links)} links available. How many would you like to scrape? (Enter a number or 'max' for all): ").strip()
        if num_links_str.lower() == 'max':
            num_links = len(product_links)
            break
        elif num_links_str.isdigit():
            num_links = int(num_links_str)
            if 0 < num_links <= len(product_links):
                break
            else:
                print(f"Please enter a number between 1 and {len(product_links)}.")
        else:
            print("Invalid input. Please enter a valid number or 'max'.")

    # Start the thread to listen for stop input
    stop_thread = threading.Thread(target=scraper.listen_for_stop)
    stop_thread.start()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        with tqdm(total=num_links, desc="Scraping Product Pages") as progress_bar:
            for idx, link in enumerate(product_links[:num_links]):
                if scraper.stop_scraping:
                    logging.info("Stopping scraping as requested by the user.")
                    break

                logging.info(f"Scraping product page: {link}")
                product_details = await scrape_product_page(page, link)
                if product_details:
                    # Update the corresponding product details in the original list
                    for product in products:
                        if product['link'] == product_details['url']:
                            product.update(product_details)
                            break
                progress_bar.update(1)
                await asyncio.sleep(1)  # Respectful delay between requests

        await browser.close()

    # Save the detailed product information back to the original JSON file
    with open(input_file, "w") as f:
        json.dump(products, f, indent=2)

    logging.info(f"Detailed product information saved to {input_file}")
    print(f"Detailed product information saved to {input_file}")

if __name__ == "__main__":
    asyncio.run(main())
