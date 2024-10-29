"""
A parser for the Income Statements found in the simulation. 
Gives this format rather than the default found in the scraper:

{
    "header": "Income Statement - Period 2",
    "content": {
        "Income Statement - Period": "2",
        "Income Statement for": "Allstar",
        "Allround Sales": "240.5",
        "Manufacturer Sales": "240.5 (100.0%)",
        "Promotional Allowance": "33.7 (14.0%)",
        "Cost of Goods Sold": "65.0 (27.0%)",
        "Gross Margin": "141.8 (59.0%)",
        "Promotion": "5.4 (2.2%)",
        "Advertising": "9.5 (4.0%)",
        "Sales Force": "8.6 (3.6%)",
        "Administrative": "8.1 (3.4%)",
        "Total Marketing": "31.6 (13.1%)",
        "Contribution after Marketing": "110.2 (45.8%)",
        "Fixed Costs": "56.7 (23.6%)",
        "Net Income": "53.5 (22.2%)",
        "Next Period Budget": "28.2 (11.7%)",
        "Note": "Amounts are in millions of dollars."
    }
}

"""

import os
import json
import re

folder_path = "sim_data_json"

income_statement_pattern = re.compile(r"Income Statement - Period \d+\.json")

def reformat_income_statement(data):
    reformatted_content = {}
    for key, value in data["content"].items():
        # Split and reformat keys that include values and percentages
        if ' ' in key and any(char.isdigit() for char in key.split()[-1]):
            # Split into name and percentage/value
            parts = key.rsplit(' ', 1)
            reformatted_key = parts[0].strip()
            if parts[1].replace('.', '', 1).isdigit() and '%' in value:
                reformatted_content[reformatted_key] = f"{parts[1]} ({value})"
            else:
                reformatted_content[reformatted_key] = value
        else:
            reformatted_content[key] = value
    return reformatted_content

for year_folder in os.listdir(folder_path):
    year_folder_path = os.path.join(folder_path, year_folder)
    
    if os.path.isdir(year_folder_path) and year_folder.startswith("Year "):
        # Income statements use the internal year system, not all pages do
        year_number = int(year_folder.split(" ")[1]) - 1
        
        for filename in os.listdir(year_folder_path):
            if income_statement_pattern.match(filename):
                file_path = os.path.join(year_folder_path, filename)

                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                # Reformat only if it's an income statement
                if f"Income Statement - Period {year_number}" in data["header"]:
                    data["content"] = reformat_income_statement(data)

                    # Overwrites the current JSON file
                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)

                    print(f"Reformatted {filename} in {year_folder}")
                else:
                    print(f"Skipped {filename} in {year_folder} - Header mismatch")