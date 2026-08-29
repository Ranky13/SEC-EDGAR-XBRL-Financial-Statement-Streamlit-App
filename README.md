# Fintech Financial Health Dashboard

A comparative financial analysis of Block, PayPal, and Visa, built from real financial data these companies file with the SEC. The project covers the full workflow: pulling the raw data, cleaning it, calculating financial ratios, and presenting the results in an interactive dashboard.

**Live app:** _[https://sec-edgar-xbrl-financial-statement-app.streamlit.app/]_

## What it does

Public companies file detailed financial statements with the SEC every quarter. This project pulls that data directly from SEC EDGAR for Block, PayPal, and Visa, then calculates five standard financial ratios — Current Ratio, Net Margin, ROE, ROA, and Debt-to-Equity — and visualizes how the three companies compare and how each has changed over time.

## A real data problem, and how it was handled

While building this, it became clear that companies don't always use the same label for the same financial concept. PayPal and Block reported revenue under one label in earlier years and switched to another later on. Visa did the same with both revenue and shareholder equity. Rather than guessing, each company's full set of reported labels was checked directly to confirm the real ones and which years each covered, then the extraction logic was built to follow all of them and combine the results under one consistent name.

One gap couldn't be resolved this way: PayPal has no revenue figure under any label for fiscal year 2019. This was left as a known, documented gap rather than filled in from an outside source.

## Project structure

- `data/` — raw SEC files and the cleaned, calculated outputs
- `scripts/` — extraction and ratio calculation logic
- `app/` — the Streamlit dashboard

## Tools used

Python, pandas, Excel, Streamlit, SEC EDGAR
