import json
import os

companies = [
    "block",
    "costco",
    "microsoft",
    "Nvidia",
    "Palantir",
    "paypal",
    "target",
    "visa",
    "walmart"
]

for company in companies:
    input_file = f"../data/raw/{company}.json"
    output_file = f"../data/structured/{company.lower()}_structured.json"

    if os.path.exists(output_file):
        print(f"{output_file} already exist, moving on")
        continue

    with open(input_file, "r") as r:
        data = json.load(r)

    with open(output_file, "w") as w:
        json.dump(data, w, indent=2)

        print(f"Done with {company}. Structured file created.")