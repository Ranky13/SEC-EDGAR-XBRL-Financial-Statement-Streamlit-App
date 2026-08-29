import json
import pandas as pd

companies = ["block", "paypal", "visa"]

for company in companies:
    filepath = f"../data/raw/{company}.json"

    with open(filepath, "r") as f:
        data = json.load(f)

    us_gaap = data["facts"]["us-gaap"]

    rows = []
    for tag_name, tag_data in us_gaap.items():
        label = tag_data.get("label", "")
        units_dict = tag_data.get("units", {})

        for unit_type, entries in units_dict.items():
            if len(entries) == 0:
                continue
            rows.append({
                "tag": tag_name,
                "label": label,
                "unit_type": unit_type,
                "num_data_points": len(entries),
                "earliest_year": min(e.get("fy") for e in entries if e.get("fy")),
                "latest_year": max(e.get("fy") for e in entries if e.get("fy")),
            })

    df = pd.DataFrame(rows).sort_values("tag")
    output_path = f"../data/processed/{company}_tag_catalog.xlsx"
    df.to_excel(output_path, index=False)
    print(f"Saved {output_path} ({len(df)} tags)")