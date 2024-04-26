import argparse
import logging
import csv
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from retrying import retry

# Constants
BASE_URL = "https://quotes.toscrape.com"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up User-Agent rotation
ua = UserAgent()

@retry(wait_exponential_multiplier=2000, wait_exponential_max=10000)
def make_request(url):
    session = requests.Session()
    session.headers.update({'User-Agent': ua.random})
    response = session.get(url)
    response.raise_for_status()
    return response

def scrape_author_info(url: str) -> dict:
    """
    Scrape author info from the specified URL.

    Args:
        url (str): The URL to scrape.

    Returns:
        dict: A dictionary containing the author's birthdate, birthplace, and description.
    """
    response = make_request(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    author_info = {}

    # Extract birthdate and birthplace
    born_info = soup.select_one('p:-soup-contains("Born:")')
    if born_info:
        born_info_parts = born_info.text.split(': ')
        if len(born_info_parts) > 1:
            born_info_text = born_info_parts[1]
            birth_date_parts = born_info_text.split(' in ')
            if len(birth_date_parts) > 1:
                author_info['birthdate'] = birth_date_parts[0].strip()
                author_info['birthplace'] = birth_date_parts[1].strip()
            else:
                author_info['birthdate'] = born_info_text.strip()

    # Extract description
    description = soup.select_one('div.author-description')
    author_info['description'] = description.text if description else ""

    return author_info

def scrape_quotes(url: str, num_pages: int) -> list:
    """
    Scrape quotes from the specified URL.

    Args:
        url (str): The URL to scrape.
        num_pages (int): The number of pages to scrape.

    Returns:
        list: A list of quote dictionaries.
    """
    quotes = []
    logger.info("Scraping quotes...")

    for page in range(1, num_pages + 1):
        page_url = f"{url}/page/{page}/"
        response = make_request(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all quote elements on the page
        quote_elements = soup.select('div.quote')

        # Loop through each quote element
        for element in quote_elements:
            quote_text = get_text(element, 'span.text')
            author = get_text(element, 'small.author')
            bio_href = get_href(element, 'span a')

            # Scrape author info from "about" page
            author_info_url = urljoin(BASE_URL, bio_href)
            author_info = scrape_author_info(author_info_url)

            # Store the quote data in a dictionary
            quote_info = {
                'Quote': quote_text,
                'Author': author,
                'Bio Href': bio_href,
                'Birthdate': author_info.get('birthdate', ""),
                'Birthplace': author_info.get('birthplace', ""),
                'Description': author_info.get('description', "")
            }

            # Add the quote data to the list
            quotes.append(quote_info)

        logger.info(f"Page {page} scraped. Quotes found: {len(quotes)}")

    return quotes

def get_text(element, selector: str) -> str:
    """
    Get the text from an element.

    Args:
        element: The element to get the text from.
        selector (str): The CSS selector to use.

    Returns:
        str: The text from the element.
    """
    text_element = element.select_one(selector)
    return text_element.text if text_element else ""

def get_href(element, selector: str) -> str:
    """
    Get the href from an element.

    Args:
        element: The element to get the href from.
        selector (str): The CSS selector to use.

    Returns:
        str: The href from the element.
    """
    anchor_element = element.select_one(selector)
    return anchor_element.get('href', "") if anchor_element else ""

def write_quotes_to_csv(quotes: list, filename: str) -> None:
    """
    Write the quotes to a CSV file.

    Args:
        quotes (list): The list of quotes to write.
        filename (str): The filename to write to.
    """
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Quote', 'Author', 'Bio Href', 'Birthdate', 'Birthplace', 'Description'])
        writer.writeheader()
        writer.writerows(quotes)

def main():
    use_default_settings = input("Do you want to use default settings? (Y/N): ")

    if use_default_settings.lower() == 'y':
        parser = argparse.ArgumentParser(description="Scrape quotes from quotes.toscrape.com")
        parser.add_argument("-n", "--num_pages", type=int, default=30, help="Number of pages to scrape")
        parser.add_argument("-o", "--output_file", default="quotes.csv", help="Output file name")
        args = parser.parse_args()

        quotes_list = scrape_quotes(BASE_URL, args.num_pages)
        write_quotes_to_csv(quotes_list, args.output_file)
        quote_count = len(quotes_list)
        logger.info(f"Scraping complete. Quotes found: {quote_count}")
    else:
        num_pages = int(input("Enter the number of pages to scrape: "))
        output_file = input("Enter the output file name: ")

        quotes_list = scrape_quotes(BASE_URL, num_pages)
        write_quotes_to_csv(quotes_list, output_file)
        quote_count = len(quotes_list)
        logger.info(f"Scraping complete. Quotes found: {quote_count}")

if __name__ == "__main__":
    main()