""" 
Intrepretive Market Share Simulation web scraper

Authored by: Isaac Herbst
Last updated: 10/28/2024

This is a web scraper for Intrepretive's Market Share simulation found here:
https://www.interpretive.com/business-simulations/marketing-principles-simulation/

The only prerequsites for use are installing the libraries below, and chrome 130.0.0.0.
Additionally, you actually need login info. Simply replace the blank strings of username and password with your own
"""

import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Assumes chrome 130.0.0.0
service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument('--ignore-certificate-errors')

driver = webdriver.Chrome(service=service, options=options)

# Logging into this domain
driver.get("https://schools.interpretive.com/fsui3/index.php?token=0")

username, password = "", ""
WebDriverWait(driver, 0).until(EC.presence_of_element_located((By.NAME, "usr"))).send_keys(username)
driver.find_element(By.NAME, "pwd").send_keys(password + Keys.RETURN)

# Launching the simluation
WebDriverWait(driver, 0).until(EC.presence_of_element_located((By.LINK_TEXT, "Simulation"))).click()
WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.ID, "sim_team"))).click()
driver.switch_to.window(driver.window_handles[-1])

""" 
Each individual page name in the internal script loadFullMod() 
They are spaced like this because of how the main groups they fall under look like.
Here are the categories they each fall under:
Startup: mod1X
Decisions: mod2X
Decision Analysis: mod3X, mod5F0
Company: mod4X
Market: mod5X
Survey: mod6X
Simulation - this one's menus do not contain data, thus are not useful for this scraper.
"""
module_names = [
    "mod110", "mod120", "mod130",
    "mod210", "mod220", "mod250", "mod260", "mod270",
    "mod310", "mod320", "mod5F0",
    "mod470", "mod410", "mod420", "mod440",
    "mod510", "mod520", "mod540", "mod550", "mod560", "mod570", "mod580", "mod5A0", "mod5B0", "mod5C0", "mod5D0",
    "mod630", "mod670", "mod680"
]

# Year dropdown
period_dropdown = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, "period"))
)

# get first year, why does it start with -1?
initial_period = period_dropdown.get_attribute("value")
print(f"Initial period extracted: {initial_period}")

# Get max year (current year)
period_options = period_dropdown.find_elements(By.TAG_NAME, "option")
max_period = len(period_options) - 1  # 0-based indexing
print(f"Maximum period extracted: {max_period}")

# Holds all the scraped data
folder = "sim_data_json"
os.makedirs(folder, exist_ok=True)

""" 
Both of the timer.sleep() calls may need changed based on internet.
.7 seconds I found to not crash the program, while also getting through
the data relatively fast. If crashes are frequent, changing those to
2 seconds should be sufficient.
"""
for module_name in module_names:
    print(f"Loading module: {module_name}")
    driver.execute_script(f"loadModFull('{module_name}', true);")
    time.sleep(1)

    # Loop through each year, increasing the period
    for year in range(max_period + 1):
        print(f"Setting period to: {year}")
        driver.execute_script(f"document.getElementById('period').value = '{year}';")
        driver.execute_script("periodMod();")
        time.sleep(1)

        # Extract content from the DOM element contentPane
        content_pane = driver.find_element(By.ID, "contentPane")
        mod_header = content_pane.find_element(By.ID, "modHeader").text.strip()
        content_text = content_pane.text.strip()

        # Save by year
        year_folder = os.path.join(folder, f"Year {year}")
        os.makedirs(year_folder, exist_ok=True)

        json_file_name = f"{mod_header}.json"
        json_file_path = os.path.join(year_folder, json_file_name)

        """ 
        JSON prep. Because the data is formatted inconsistently/poorly, 
        there are a lot of edge cases. This loop attempts to accurately 
        catagorize the data into some form of word:number relationships.
        """
        content_lines = content_text.split('\n')
        content_dict = {}

        for line in content_lines:
            line = line.strip()
            if line:  # Check if the line is not empty
                # Check if the line has a colon (:) for structured data
                if ':' in line:
                    parts = line.rsplit(':', 1)  # Split into key and value at the last colon
                    key = parts[0].strip()  # The key is the part before the last colon
                    value = parts[1].strip()  # The value is the part after the last colon
                    content_dict[key] = value  # Store key-value pair in the dictionary
                else:
                    # Check for specific known patterns to merge keys and values
                    if 'Salary' in line or 'Expenses' in line or 'Training' in line:
                        parts = line.split('$', 1)  # Split at the first dollar sign
                        if len(parts) == 2:
                            key = parts[0].strip() + "$"  # The key includes the dollar sign
                            value = f"${parts[1].strip()} Million"  # Format the value correctly
                            content_dict[key] = value  # Store key-value pair in the dictionary
                        continue  # Skip to the next iteration
                    else:
                        # Split by spaces for items with counts, assuming the last part is the quantity
                        parts = line.rsplit(' ', 1)  # Split into key and value at the last space
                        if len(parts) == 2:
                            key = parts[0].strip()  # The key is the part before the last space
                            value = parts[1].strip()  # The value is the part after the last space
                            
                            # Adjust for specific known patterns for formatting
                            if 'Million' not in value:  # Check if value is not already formatted
                                content_dict[key] = value  # Store key-value pair in the dictionary
                            else:
                                value = value.replace(" Million", "") + " Million"  # Fix formatting
                                content_dict[key] = value  # Store key-value pair in the dictionary
                        else:
                            key = f"Item {len(content_dict) + 1}"  # Fallback for unstructured lines
                            content_dict[key] = line  # Add to dictionary

        # Prepare the final content structure, save as .JSON
        content_to_save = { "header": mod_header, "content": content_dict }

        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(content_to_save, json_file, ensure_ascii=False, indent=4)

driver.quit()