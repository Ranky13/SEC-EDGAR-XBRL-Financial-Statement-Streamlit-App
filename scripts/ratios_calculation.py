import pandas as pd

df = pd.read_excel("../data/processed/all_companies_extracted.xlsx")

df = df[df["fiscal_period"] == "FY"]

pivoted = df.pivot_table(
    index=["company", "fiscal_year"],
    columns="tag",
    values="value"
).reset_index()

pivoted["current_ratio"] = pivoted["AssetsCurrent"] / pivoted["LiabilitiesCurrent"]
pivoted["net_margin"] = pivoted["NetIncomeLoss"] / pivoted["Revenues"]
pivoted["roe"] = pivoted["NetIncomeLoss"] / pivoted["StockholdersEquity"]
pivoted["roa"] = pivoted["NetIncomeLoss"] / pivoted["Assets"]
pivoted["debt_to_equity"] = pivoted["Liabilities"] / pivoted["StockholdersEquity"]

pivoted.to_excel("../data/processed/ratios.xlsx", index=False)

print(f"Done. {len(pivoted)} company-year rows with ratios calculated.")