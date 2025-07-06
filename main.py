from fastapi import FastAPI, Request, HTTPException
from app.scraper import scraper
from app.google_sheet_writing import write_to_gsheet

app = FastAPI()

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
    raise HTTPException(status_code=500, detail=posts_status)
  write_status = write_to_gsheet(posts)

  return {"status": write_status, "posts": posts}
