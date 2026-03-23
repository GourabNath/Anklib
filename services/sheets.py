import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

"""
Description:
    Initializes connection to Google Sheets using service account credentials.
"""

# Define scope (permissions)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from JSON
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

# Authorize client
client = gspread.authorize(creds)

# Open your Google Sheet (make sure name matches exactly)
sheet = client.open("anklib_data").sheet1



def save_to_sheets(data: dict):
    """
    Saves user-confirmed book metadata into Google Sheets
    with stable headers and consistent alignment.
    """

    headers = ["timestamp", "title", "author", "publisher", "isbn", "edition", "price"]

    existing_data = sheet.get_all_values()

    # ✅ Ensure headers exist ONLY ONCE
    if not existing_data:
        sheet.append_row(headers)
    elif existing_data[0] != headers:
        sheet.insert_row(headers, 1)

    # ✅ Force consistent structure (no None values)
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("title") or "",
        data.get("author") or "",
        data.get("publisher") or "",
        data.get("isbn") or "",
        data.get("edition") or "",
        data.get("price") or ""
    ]

    print("Writing row:", row)  # Debug

    sheet.append_row(row)