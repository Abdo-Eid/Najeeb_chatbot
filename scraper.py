from playwright.sync_api import sync_playwright
import json
import time

url = "https://digital.gov.eg/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector(".logo-spin", state="detached")

    all_groups_data = []

    # Loop over groups
    for group_index in range(1, 23):  # Loop over 25 groups
        print(f"\n➡️ Opening group {group_index}...")

        try:
            # Click the group button
            group_button = page.locator(f'//html/body/main/div[3]/div/div[2]/div[3]/div/button[{group_index}]')
            group_button.click()

            # Wait for the group to load - make sure the questions for this group are visible
            try:
                page.wait_for_selector(f'//html/body/main/div[3]/div/div[3]/div/a', timeout=20000)  # Increased timeout to 20 seconds
            except Exception as e:
                print(f"Error: Unable to load questions for group {group_index}. {e}")
                continue  # Skip this group if it fails to load

            time.sleep(2)  # Wait for questions to load

            # Extract the group name
            group_name = group_button.inner_text().strip()

            group_data = []

            # Dynamically find the total number of questions in the group by counting <a> elements
            total_questions = len(page.query_selector_all(f'//html/body/main/div[3]/div/div[3]/div/a'))

            # If no questions, skip this group
            if total_questions == 0:
                print(f"⚠️ No questions found in group {group_index}. Skipping group.")
                continue

            # Loop through each question in the group
            for question_index in range(1, total_questions + 1):  # Use total_questions for the range
                # Construct XPath dynamically for each question's <p> element
                question_xpath = f'/html/body/main/div[3]/div/div[3]/div[{question_index}]/a/p[1]'
                
                # Wait for the question to be visible
                question_block = page.locator(f'xpath={question_xpath}')
                question_block.wait_for(state="visible", timeout=10000)  # Wait for up to 10 seconds

                # Try to extract the question text
                try:
                    question_text = question_block.inner_text().strip()
                except Exception as e:
                    print(f"Error extracting question for index {question_index}: {e}")
                    question_text = "لا يوجد"  # Assign "لا يوجد" if the question is missing

                # Construct XPath dynamically for the description (p[2] for the second <p> element)
                description_xpath = f'/html/body/main/div[3]/div/div[3]/div[{question_index}]/a/p[2]'
                
                # Get the description block element using the dynamic XPath
                description_block = page.locator(f'xpath={description_xpath}')
                
                # Try to extract the description text
                try:
                    description_text = description_block.inner_text().strip()
                except Exception as e:
                    print(f"Error extracting description for index {question_index}: {e}")
                    description_text = "لا يوجد"  # Assign "لا يوجد" if the description is missing

                # Click the question to navigate to the answer page
                question_block.click()

                # Try to extract the answer text
                try:
                    # Wait for the answer page to load by waiting for either the "شروط واحكام" or "المستندات المطلوبه"
                    page.locator('xpath=/html/body/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div').wait_for(timeout=10000)  # Wait for the answer to load

                    answer_text = page.locator('xpath=/html/body/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div').inner_text().strip()
                except Exception as e:
                    print(f"Error extracting answer for question {question_index}: {e}")
                    answer_text = "لا يوجد"  # Assign "لا يوجد" if the answer is missing

                # Try to extract the "المستندات المطلوبه" text
                try:
                    required_docs_text = page.locator('xpath=/html/body/div[2]/div/div[2]/div[1]/div[2]/div/div/div/div').inner_text().strip()
                except Exception as e:
                    print(f"Error extracting required documents for question {question_index}: {e}")
                    required_docs_text = "لا يوجد"  # Assign "لا يوجد" if the required documents are missing

                # Store the question, description, answer, and required documents
                group_data.append({
                    "السؤال": question_text,
                    "الوصف": description_text,
                    "الشروط والاحكام": answer_text,
                    "الاوراق المطلوبه": required_docs_text
                })

                # Go back to the main page to process the next question
                page.go_back()
                time.sleep(2)  # Adjust wait time to allow page navigation
                print(f"🔄 Processed question {question_index}/{total_questions} in group '{group_name}'...")

            print(f"✅ Group '{group_name}' — extracted {len(group_data)} questions.")

            # After processing all questions in the group, append the group data to the list
            all_groups_data.append({
                "group_name": group_name,
                "questions": group_data
            })

        except Exception as e:
            print(f"Error processing group {group_index}: {e}")
            continue  # Skip this group if it fails to process

    # Save the results as JSON
    with open("questions_with_answers.json", "w", encoding="utf-8") as f:
        json.dump(all_groups_data, f, ensure_ascii=False, indent=4)

    browser.close()
