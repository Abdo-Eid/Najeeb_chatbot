from playwright.sync_api import sync_playwright
import json
import time

# Function to extract text safely from a locator
# This function ensures that if an error occurs, a default value is returned
def extract_text(locator, default_value="لا يوجد"):
    try:
        return locator.inner_text().strip()  # Return the inner text of the locator
    except Exception as e:
        print(f"Error extracting text: {e}")  # Print error if extraction fails
        return default_value  # Return the default value if extraction fails




# Function to process each group on the webpage
# This function handles opening the group, waiting for the questions, and processing them
def process_group(page, group_index):
    print(f"\n➡️ Opening group {group_index}...")
    try:
        # Find and click the group button
        group_button = page.locator(f'//html/body/main/div[3]/div/div[2]/div[3]/div/button[{group_index}]')
        group_button.click()

        # Wait for the questions in the group to load
        try:
            page.wait_for_selector(f'//html/body/main/div[3]/div/div[3]/div/a', timeout=5000)  # Increased timeout to 5 seconds
        except Exception as e:
            print(f"Error: Unable to load questions for group {group_index}. {e}")
            return None  # Return None if questions fail to load

        time.sleep(2)  # Wait for questions to load

        # Extract the group's name
        group_name = extract_text(group_button)
        group_data = []

        # Count the total number of questions in this group
        total_questions = len(page.query_selector_all(f'//html/body/main/div[3]/div/div[3]/div/a'))
        if total_questions == 0:
            print(f"⚠️ No questions found in group {group_index}. Skipping group.")
            return None  # Return None if there are no questions in the group

        # Process each question in the group
        for question_index in range(1, total_questions + 1):
            question_data = process_question(page, group_index, question_index, group_name)
            if question_data:
                group_data.append(question_data)

        return group_data  # Return the processed data for this group

    except Exception as e:
        print(f"Error processing group {group_index}: {e}")
        return None  # Return None if an error occurs while processing the group






# Function to process each question in a group
# This function handles extracting question details, such as text, description, and answer
def process_question(page, group_index, question_index, group_name):
    question_xpath = f'/html/body/main/div[3]/div/div[3]/div[{question_index}]/a/p[1]'
    description_xpath = f'/html/body/main/div[3]/div/div[3]/div[{question_index}]/a/p[2]'

    # Find and click the group button
    group_button = page.locator(f'//html/body/main/div[3]/div/div[2]/div[3]/div/button[{group_index}]')
    group_button.click()

    # Wait for the question to become visible
    question_block = page.locator(f'xpath={question_xpath}')
    question_block.wait_for(state="visible", timeout=10000)

    # Extract question text and description text using the helper function
    question_text = extract_text(question_block)
    description_block = page.locator(f'xpath={description_xpath}')
    description_text = extract_text(description_block)

    # Click the question to open the answer page
    question_block.click()
    
    # Extract the answer text using the helper function
    answer_text = extract_answer(page)

    # Extract the required documents and related services
    required_docs_text = extract_text(page.locator('xpath=/html/body/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div'))
    related_services = extract_related_services(page)

    service_url = page.url  # Get the URL of the service page

    page.go_back()  # Go back to the main page
    time.sleep(2)  # Wait for the page to load before continuing

    print(f"🔄 Processed question {question_index} in group '{group_name}'...")

    # Return a dictionary containing the question and related details
    return {
        "category": group_name,
        "service_name": question_text,
        "service_url": service_url,
        "description": description_text,
        "terms": answer_text.split(r"/n/n"),
        "Documents": required_docs_text,
        "related_servises": related_services
    }


# Function to extract related services and their links
def extract_related_services(page):
    # Initialize an empty list to store the extracted services and links
    related_services = []

    # Find all <a> tags within the "my-3" class (where services are listed)
    service_elements = page.query_selector_all('div.MuiAccordionDetails-root a')

    # Loop through each service element to extract the text and link
    for service in service_elements:
        service_text = extract_text(service)  # Extract the text of the service
        service_link = service.get_attribute('href')  # Extract the link (URL) associated with the service
        
        # Append the extracted data to the list
        related_services.append({
            "text": service_text,
            "link": "https://digital.gov.eg/"+service_link
        })

    return related_services  # Return the list of related services with their links




# Function to extract the answer text from the answer page
# This function handles waiting for the answer to load and extracting its content
def extract_answer(page):
    try:
        # Wait for the answer section to load
        page.locator('xpath=/html/body/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div').wait_for(timeout=5000)
        return page.locator('xpath=/html/body/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div').inner_text().strip()
    except Exception as e:
        print(f"Error extracting answer: {e}")
        return "لا يوجد"  # Return a default value if the answer cannot be extracted



# Main function to run the scraper
# This function starts the scraping process, handles the browser setup, and saves the results to a file
def scrape_data():
    url = "https://digital.gov.eg/"
    all_groups_data = []  # List to store the extracted data

    with sync_playwright() as p:
        # Launch the browser and navigate to the URL
        browser = p.chromium.launch(headless=True)  # Set headless to True for background operation
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector(".logo-spin", state="detached")  # Wait for the page to load

        # Loop over groups to process each one
        for group_index in range(1, 24):  # Loop over 23 groups
            group_data = process_group(page, group_index)
            if group_data:
                all_groups_data.extend(group_data)  # Add the processed data for the group

        # Save the results as a JSON file
        with open("scraped_data.json", "w", encoding="utf-8") as f:
            json.dump(all_groups_data, f, ensure_ascii=False, indent=4)

        browser.close()  # Close the browser



# Run the scraper function
scrape_data()
