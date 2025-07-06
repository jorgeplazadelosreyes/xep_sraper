from fastapi import FastAPI, Request, HTTPException
from app.scraper import scraper

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

  status, posts = await scraper(category)
  return {"status": status, "posts": posts}
