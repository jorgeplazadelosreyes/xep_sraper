import requests

def send_webhook(webhook_url, email, gsheet_link):
  payload = {
    "email": email,
    "link": gsheet_link
  }

  try:
    response = requests.post(webhook_url, json=payload, timeout=10)
    response.raise_for_status()
    return 'success'
  except requests.exceptions.RequestException as e:
    return f"error: {e}"
