import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from tqdm import tqdm
import sys
from typing import List, Dict, TypedDict, Optional

# Define a TypedDict to represent the structure of a related service link
class RelatedService(TypedDict):
    text: str
    link: str

# Define a TypedDict to represent the structure of the scraped service data
class ScrapedServiceData(TypedDict):
    category: str
    service_name: str
    service_url: str
    description: str
    terms: List[str]
    Documents: List[str]
    related_servises: List[RelatedService]

def extract_list_content(container: Optional[BeautifulSoup]) -> List[str]:
    """
    Extracts and cleans text from paragraph tags within a given BeautifulSoup container.
    Removes leading hyphens and filters out empty strings.
    Specifically handles the case where the content is just "لا يوجد" and returns an empty list.

    Args:
        container: The BeautifulSoup object representing the container element
                   (e.g., an accordion details div).

    Returns:
        A list of cleaned strings extracted from paragraph tags, or an empty list
        if the container is empty or contains only "لا يوجد".
    """
    if not container:
        return []

    # Extract text from each paragraph, clean it, and remove leading hyphens
    items = [p.get_text(strip=True).lstrip('- \t\n') for p in container.select('p')]
    # Filter out any empty strings that might result from cleaning
    cleaned_items = [item for item in items if item]

    # Check if the only item is "لا يوجد" and return an empty list in that case
    if len(cleaned_items) == 1 and cleaned_items[0] == "لا يوجد":
        return []

    return cleaned_items

def scrape_service_bs4(service_url: str, category: str) -> Optional[ScrapedServiceData]:
    """
    Scrapes a single service page using BeautifulSoup and extracts relevant data.

    Args:
        service_url: The URL of the service page to scrape.
        category: The category the service belongs to (passed from the category scraper).

    Returns:
        A dictionary conforming to ScrapedServiceData containing the scraped data,
        or None if an error occurred during fetching or parsing.
    """
    try:
        # Fetch the HTML content of the service page
        response = requests.get(service_url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the main service name (the large heading)
        service_name_tag = soup.select_one("div.MuiContainer-root.MuiContainer-maxWidthLg.css-1qsxih2 > h1")
        service_name = service_name_tag.get_text(strip=True) if service_name_tag else ""

        # Find all accordion sections and map their headings to their content details
        accordion_sections: Dict[str, BeautifulSoup] = {}
        for accordion in soup.select('div.MuiAccordion-root'):
            summary = accordion.select_one('div.MuiAccordionSummary-content h2')
            details = accordion.select_one('div.MuiAccordionDetails-root')
            if summary and details:
                heading_text = summary.get_text(strip=True)
                accordion_sections[heading_text] = details

        # Extract Description from the corresponding accordion section
        description_container = accordion_sections.get("وصف الخدمة")
        description = description_container.get_text("\n", strip=True) if description_container else ""

        # Extract Terms using the helper function
        terms_container = accordion_sections.get("شروط و أحكام الخدمة")
        terms = extract_list_content(terms_container)

        # Extract Required Documents using the helper function
        documents_container = accordion_sections.get("المستندات المطلوبة")
        documents = extract_list_content(documents_container)


        # Extract Related Services from the corresponding accordion section
        related_services: List[RelatedService] = []
        related_services_container = accordion_sections.get("خدمات مشابهة")
        if related_services_container:
            related_links = related_services_container.select("a")
            for link in related_links:
                text = link.get_text(strip=True)
                href = link.get("href")
                if href:
                    # Construct the full URL for related services
                    full_link = urljoin("https://digital.gov.eg/", href)
                    related_services.append({
                        "text": text,
                        "link": full_link
                    })

        # Return the structured scraped data
        return ScrapedServiceData(
            category=category,
            service_name=service_name,
            service_url=service_url,
            description=description,
            terms=terms,
            Documents=documents,
            related_servises=related_services
        )

    except requests.exceptions.RequestException as e:
        # Log HTTP errors to standard error
        print(f"❌ HTTP Error scraping {service_url}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        # Log any other scraping errors to standard error
        print(f"❌ Error scraping {service_url}: {e}", file=sys.stderr)
        return None

# Main execution block
if __name__ == "__main__":
    try:
        # Load the service URLs grouped by category from the pre-scraped JSON
        with open("services_by_category.json", "r", encoding="utf-8") as f:
            services_by_category = json.load(f)

        all_data: List[ScrapedServiceData] = []
        # Calculate the total number of services for the progress bar
        total_services = sum(len(services) for services in services_by_category.values())

        # Iterate through categories and services, scraping each service page
        with tqdm(total=total_services, desc="Scraping Services") as pbar:
            for category, services in services_by_category.items():
                for service in services:
                    data = scrape_service_bs4(service["url"], category)
                    if data:
                        all_data.append(data)
                    # Update the progress bar after processing each service
                    pbar.update(1)

        # Save the collected data to a JSON file
        with open("scraped_services_data.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)

        print("\n✅ Data saved to scraped_services_data.json")

    except FileNotFoundError:
        # Handle the case where the input file is not found
        print("Error: services_by_category.json not found. Please run the first script to generate it.", file=sys.stderr)
    except Exception as e:
        # Handle any unexpected errors during the main process
        print(f"An error occurred during processing: {e}", file=sys.stderr)