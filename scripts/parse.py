import os
import json
import pandas as pd

companies = [
    "block",
    "paypal",
    "visa",
]

TAG_ALTERNATIVES = {
    "Assets": ["Assets"],
    "AssetsCurrent": ["AssetsCurrent"],
    "Liabilities": ["Liabilities"],
    "LiabilitiesCurrent": ["LiabilitiesCurrent"],
    "Revenues": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
    ],
    "NetIncomeLoss": ["NetIncomeLoss"],
    "StockholdersEquity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
}


def extract_company(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    entity_name = data["entityName"]
    us_gaap = data["facts"]["us-gaap"]

    rows = []

    for canonical_tag, possible_names in TAG_ALTERNATIVES.items():
        for actual_tag_name in possible_names:
            if actual_tag_name not in us_gaap:
                continue

            tag_data = us_gaap[actual_tag_name]

            if "USD" not in tag_data["units"]:
                continue

            entries = tag_data["units"]["USD"]

            for entry in entries:
                rows.append({
                    "company": entity_name,
                    "tag": canonical_tag,
                    "fiscal_year": entry.get("fy"),
                    "fiscal_period": entry.get("fp"),
                    "period_end": entry.get("end"),
                    "value": entry.get("val"),
                    "form": entry.get("form"),
                    "filed": entry.get("filed"),
                })


    df = pd.DataFrame(rows)
    df = df.sort_values("filed")


    df = df.drop_duplicates(subset=["tag", "period_end"], keep="first")

    return df


all_dataframes = []

for company in companies:
    filepath = f"../data/raw/{company}.json"

    if not os.path.exists(filepath):
        print(f"{filepath} not found. Skipping")
        continue

    print(f"Processing {company}...")

    company_df = extract_company(filepath)

    output_path = f"../data/processed/{company}_extracted.xlsx"
    company_df.to_excel(output_path, index=False)
    print(f"  -> saved {output_path} ({len(company_df)} rows)")

    all_dataframes.append(company_df)

final_df = pd.concat(all_dataframes, ignore_index=True)
final_df.to_excel("../data/processed/all_companies_extracted.xlsx", index=False)

print(f"\nDone.. {len(final_df)} total rows across {len(all_dataframes)} companies.")