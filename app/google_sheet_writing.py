import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_URL = "https://docs.google.com/spreadsheets/d/1383yCHi58GlXC8xaAIHZQ4Pfian9LCptKaFgW3pO6Zk/edit?usp=sharing"

def write_to_gsheet(data):
	scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
	creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
	client = gspread.authorize(creds)

	sheet = client.open_by_url(SHEET_URL)
	worksheet = sheet.sheet1

	headers = list(data[0].keys())
	rows = [headers] + [[str(item.get(col, "")) for col in headers] for item in data]

	worksheet.clear()
	worksheet.append_rows(rows)
	return "success" if rows else "failed to write data"