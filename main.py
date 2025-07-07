from fastapi import FastAPI, Request, HTTPException
from app.scraper import scraper
from app.google_sheet_writing import write_to_gsheet
from app.webhook import send_webhook

app = FastAPI()

WEBHOOK_EMAIL = 'jorge.plazadelosreyes0@gmail.com'
GSHEET_URL = 'https://docs.google.com/spreadsheets/d/1383yCHi58GlXC8xaAIHZQ4Pfian9LCptKaFgW3pO6Zk'

@app.post("/scrape")
async def scrape(request: Request):
  body = await request.json()
  category = body.get("category")
  webhook = body.get("webhook")
  if not webhook:
    raise HTTPException(status_code=400, detail="Missing 'webhook' parameter")
  if not category:
    raise HTTPException(status_code=400, detail="Missing 'category' parameter")

  posts_status, posts = await scraper(category)
  if posts_status != "success":
    return {"status": posts_status}
  write_status = write_to_gsheet(posts, GSHEET_URL)
  if write_status != "success":
    return {"status": write_status}
  webhook_status = send_webhook(webhook, GSHEET_URL, WEBHOOK_EMAIL)
  if webhook_status != "success":
    return {"status": webhook_status}

  return {"status": write_status}
