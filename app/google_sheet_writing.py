import gspread
import os
import json
import base64
from oauth2client.service_account import ServiceAccountCredentials

def write_to_gsheet(data, sheet_url):
	scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
	b64_creds = os.environ.get("GOOGLE_CREDS_BASE64")
	creds_json = json.loads(base64.b64decode(b64_creds))
	
	creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
	client = gspread.authorize(creds)

	sheet = client.open_by_url(sheet_url)
	worksheet = sheet.sheet1

	headers = list(data[0].keys())
	rows = [headers] + [[str(item.get(col, "")) for col in headers] for item in data]

	worksheet.clear()
	worksheet.append_rows(rows)
	return "success" if rows else "failed to write data"