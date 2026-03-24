import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Define scope
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

sheet = client.open("anklib_data").sheet1


def save_to_sheets(data: dict):
    """
    Saves user-confirmed book metadata into Google Sheets
    with formatted headers (bold + sentence case).
    """

    # Internal keys (DO NOT CHANGE — used for mapping)
    keys = [
        "timestamp",
        "title",
        "author",
        "publisher",
        "isbn",
        "edition",
        "price",
        "accession_number",
        "number_of_pages"
    ]

    # 🆕 FORMAT HEADERS → Sentence case + no underscores
    headers = [
        key.replace("_", " ").upper()
        for key in keys
    ]

    existing_data = sheet.get_all_values()

    # Ensure headers exist only once
    if not existing_data:
        sheet.append_row(headers)
    elif existing_data[0] != headers:
        sheet.insert_row(headers, 1)

    # 🆕 MAKE HEADER ROW BOLD
    sheet.format("1:1", {"textFormat": {"bold": True}})

    # Row data mapping (unchanged logic)
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("title") or "",
        data.get("author") or "",
        data.get("publisher") or "",
        data.get("isbn") or "",
        data.get("edition") or "",
        data.get("price") or "",
        data.get("accession_number") or "",
        data.get("number_of_pages") or ""
    ]

    print("Writing row:", row)

    sheet.append_row(row)