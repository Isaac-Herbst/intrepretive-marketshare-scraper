""" Not working yet """

import os
import json
import re

# Path to the folder containing year subdirectories with JSON files
folder_path = "sim_data_json"

# Regex pattern to match files named "Decision Summary - Period N.json"
decision_summary_pattern = re.compile(r"Decision Summary - Period \d+\.json")

# Regex patterns to extract dynamic values
patterns = {
    "Sales Force": r"Sales Force.*?(\d{1,3}\.\d%)",
    "Drugstores": r"Drugstores\s+(\d+)",
    "Indirect Support": r"Indirect Support.*?(\d+)",
    "Grocery Stores": r"Grocery Stores\s+(\d+)",
    "Mass Merch": r"MassMerch.*?(\d+)",
    "Total Sales Force": r"Total Sales Force.*?(\d+)",
    "Advertising": r"Advertising.*?(\d{1,3}\.\d%)",
    "Promotion": r"Promotion.*?(\d{1,3}\.\d%)",
    "Reports Ordered": r"Item 12\s*:\s*(\w+)",
    "MSRP ($)": r"MSRP\s*\(\$\)\s*:\s*([\d.]+)",
    "Discount (%)": r"Discount\s*\(%\)\s*:\s*([\d.]+%)",
    "Advertising Budget": r"Advertising Budget\s*\$?([\d.]+)\s*Million",
    "Primary %": r"Primary %\s*:\s*([\d.]+%)",
    "Benefit %": r"Benefit %\s*:\s*([\d.]+%)",
    "Comparison %": r"Comparison %.*?([\d.]+%) with (\w+)",
    "Reminder %": r"Reminder %\s*:\s*([\d.]+%)",
    "Promote Benefits": r"Promote Benefits.*?: (.+?)(?=\s*\w+|$)",
    "Promotion Allowance (%)": r"Promotion Allowance\s*\(%\)\s*:\s*([\d.]+%)",
    "Product Displays": r"Product Displays\s*\$([\d.]+)\s*Million",
    "Coupons": r"Coupons\s*\$([\d.]+)\s*Million",
    "Special Decision": r"Special\s*Decision\s*:\s*(.*)"
}

def reformat_decision_summary(data):
    """Reformats the decision summary content to match the specified structure."""
    # New content structure to match the required format
    reformatted_content = {}

    # Extract values dynamically based on regular expressions
    for key, pattern in patterns.items():
        match = re.search(pattern, str(data["content"]))
        reformatted_content[key] = match.group(1) if match else ""

    # Adding static keys that do not need regex matching
    reformatted_content.update({
        "Decision Summary - Period": data["content"].get("Decision Summary - Period", ""),
        "Decision Summary for Allstar, Input for Period": data["content"].get("Decision Summary for Allstar, Input for Period", ""),
        "Summary of Decisions": data["content"].get("Summary of Decisions", "(Allround)"),
        "Period": "1 2 3 4 5 6",
        "Replays": "0 0 0 0 0 0",
        "Restarts": data["content"].get("Restarts", "0"),
        "Brand": "Analg Antihist Decon Cough Supp. Expec Alcoh Description",
        "Allround": "1000 4 60 30 0 20 4hr-multi-liquid"
    })

    return reformatted_content

# Loop through JSON files in the folder
for year_folder in os.listdir(folder_path):
    year_folder_path = os.path.join(folder_path, year_folder)
    
    # Process only directories named "Year N"
    if os.path.isdir(year_folder_path) and year_folder.startswith("Year "):
        for filename in os.listdir(year_folder_path):
            if decision_summary_pattern.match(filename):
                file_path = os.path.join(year_folder_path, filename)

                # Load JSON content
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                # Reformat only if it's a decision summary
                if "Decision Summary - Period" in data["header"]:
                    data["content"] = reformat_decision_summary(data)

                    # Save the modified JSON back to the file
                    with open(file_path, 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)

                    print(f"Reformatted {filename} in {year_folder}")
                else:
                    print(f"Skipped {filename} in {year_folder} - Header mismatch")
