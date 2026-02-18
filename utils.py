import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from config import BRANCHES

def get_service_client(json_file="credentials.json"):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
    return gspread.authorize(creds)

def fetch_master_data(client):
    all_data = []

    for branch in BRANCHES:
        sheet_id = branch["url"].split("/d/")[1].split("/")[0]
        ss = client.open_by_key(sheet_id)

        for sh in ss.worksheets():
            date_name = sh.title
            df = pd.DataFrame(sh.get_all_values())
            if len(df) < 3:
                continue
            for idx, row in df.iloc[2:].iterrows():
                if row[0] != "":
                    all_data.append({
                        "Date": date_name,
                        "Branch": branch["name"],
                        "Customer Name": row[0],
                        "Contact": row[1],
                        "Item": row[3],
                        "Description": row[4],
                        "IMEI": row[5]
                    })

    master_df = pd.DataFrame(all_data)
    master_df.drop_duplicates(subset=["IMEI"], inplace=True)
    return master_df
