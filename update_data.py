import gspread
import pandas as pd
import time
from oauth2client.service_account import ServiceAccountCredentials
from config import BRANCHES

# List of required columns for master
REQUIRED_COLUMNS = [
    "CUSTOMER NAME",
    "CONTACT",
    "ACC INV NO",
    "ITEM",
    "ITEM DESCRIPTION",
    "SERIAL NUMBER / IMEI",
    "SUPPLIER NAME",
    "COST",
    "INVOICE VALUE",
    "SALES PERSON"
]

def get_service_client(json_file="credentials.json"):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
    return gspread.authorize(creds)

def fetch_master_data(client):
    all_data = []

    for branch in BRANCHES:
        sheet_id = branch["url"].split("/d/")[1].split("/")[0]
        try:
            ss = client.open_by_key(sheet_id)
        except Exception as e:
            print(f"Error opening sheet {branch['name']}: {e}")
            continue

        worksheets = ss.worksheets()
        print(f"Fetching {len(worksheets)} worksheets from branch {branch['name']}...")

        for sh in worksheets:
            try:
                values = sh.get_all_values()
                if len(values) < 2:
                    continue  # skip empty sheets

                # Find the header row dynamically (first row containing "CUSTOMER" or "CUSTOMER NAME")
                header_row_idx = None
                for i, row in enumerate(values):
                    row_upper = [str(cell).strip().upper() for cell in row]
                    if any("CUSTOMER" in cell for cell in row_upper):
                        header_row_idx = i
                        break

                if header_row_idx is None:
                    print(f"No header found in sheet {sh.title}, skipping.")
                    continue

                # Extract header and data rows
                header = [str(h).strip().upper() for h in values[header_row_idx]]
                data_rows = values[header_row_idx + 1:]

                df = pd.DataFrame(data_rows, columns=header)

                # Normalize missing columns
                for col in REQUIRED_COLUMNS:
                    if col not in df.columns:
                        df[col] = ""

                df.fillna("", inplace=True)

                # Append all rows
                for idx, row in df.iterrows():
                    all_data.append({
                        "Date": sh.title,
                        "Branch": branch["name"],
                        "Customer Name": row.get("CUSTOMER NAME", row.get("CUSTOMER CONTACT", "")),
                        "Contact": row.get("CONTACT", row.get("CUSTOMER CONTACT", "")),
                        "Acc Inv No": row.get("ACC INV NO", ""),
                        "Item": row.get("ITEM", ""),
                        "Description": row.get("ITEM DESCRIPTION", ""),
                        "IMEI": row.get("SERIAL NUMBER / IMEI", ""),
                        "Supplier": row.get("SUPPLIER NAME", ""),
                        "Cost": row.get("COST", ""),
                        "Invoice Value": row.get("INVOICE VALUE", ""),
                        "Sales Person": row.get("SALES PERSON", "")
                    })

                # Small delay to avoid hitting Google Sheets API quota
                time.sleep(1)

            except Exception as e:
                print(f"Error fetching worksheet {sh.title} in {branch['name']}: {e}")
                continue

    master_df = pd.DataFrame(all_data)
    master_df.drop_duplicates(subset=["IMEI"], inplace=True)
    master_df.sort_values(by=["Date", "Branch"], inplace=True)
    master_df.reset_index(drop=True, inplace=True)
    return master_df

if __name__ == "__main__":
    print("Starting master database update...")
    client = get_service_client("credentials.json")
    master_df = fetch_master_data(client)
    master_df.to_csv("data/master_db.csv", index=False, encoding="utf-8")
    print("✅ Master database updated successfully!")
    print(f"Total records: {len(master_df)}")
