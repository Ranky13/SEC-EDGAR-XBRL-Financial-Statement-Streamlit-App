import pandas as pd
df = pd.read_excel("../data/processed/all_companies_extracted.xlsx")
df = df[df["fiscal_period"] == "FY"]

pivoted = df.pivot_table(
    index=["company", "fiscal_year"],
    columns="tag",
    values="value"
).reset_index()

print(pivoted.to_string())

