import asyncio
from unidecode import unidecode
import aiohttp
import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

sem = asyncio.Semaphore(2)

BASE_URL = 'https://xepelin.com'

async def get_categories():
  categories = {}
  res = requests.get(f"{BASE_URL}/blog")
  if res.status_code != 200:
    return {}

  soup = BeautifulSoup(res.text, 'html.parser')
  menu = soup.select_one('ul.hidden.gap-7.lg\\:flex')
  if not menu: 
    return {}

  for a in menu.find_all('a', href=True):
    href = a['href']
    path = urlparse(href).path
    if re.match(r'^/blog/[^/]+$', path):
      name = a.get_text(strip=True)
      parsed_name = unidecode(name).lower().strip()
      categories[parsed_name] = {'category_path': path}
  return categories


async def fetch_all_articles(category_slug):
  sanity_url = None

  async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()

    fut = asyncio.Future()

    def handle_response(response):
      nonlocal sanity_url
      url = response.url
      if 'apicdn.sanity.io' in url and 'query=*' in url and not fut.done():
        fut.set_result(url)

    page.on('response', handle_response)
    await page.goto(f"{BASE_URL}{category_slug}", wait_until='domcontentloaded')

    try:
      sanity_url = await asyncio.wait_for(fut, timeout=5)
    except asyncio.TimeoutError:
      sanity_url = None

    await browser.close()


  if not sanity_url:
    print("No matching Sanity query URL found.")
    return []

  sliced_url = sanity_url
  start_index = sliced_url.rfind('%5B')
  end_index = sliced_url.rfind('%5D') + 3
  if start_index != -1 and end_index != -1:
    full_url = sliced_url[:start_index] + sliced_url[end_index:]
  else:
    full_url = sliced_url

  response = requests.get(full_url)
  response.raise_for_status()
  articles = response.json().get("result", [])
  return articles

async def get_reading_time(session, url):
  async with sem:
    try:
      async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as res:
        html = await res.text()
        soup = BeautifulSoup(html, 'html.parser')
        candidates = soup.find_all('div', class_=re.compile('Text_body__'))
        for div in candidates:
          text = div.get_text(strip=True).lower()
          if 'min de lectura' in text:
            return text
    except Exception as e:
      print(f"Error reading_time for {url}: {e}")
    return ''

async def get_reading_time_bulk(urls):
  async with aiohttp.ClientSession() as session:
    tasks = [get_reading_time(session, url) for url in urls]
    return await asyncio.gather(*tasks)

async def get_blog_posts_for_category(category_name, mapped_categories):
  if category_name == "all":
    results = []
    for single_category in mapped_categories:
      results.extend(await get_blog_posts_for_category(single_category, mapped_categories))
    return results

  slug = mapped_categories[category_name]['category_path']
  post_url = f"{BASE_URL}{slug}"
  articles = await fetch_all_articles(slug)
  result = []

  urls = []
  for article in articles:
    slug = article.get('slug', {}).get('current', '').strip()
    urls.append(f"{post_url}/{slug}")

  reading_times = await get_reading_time_bulk(urls)

  for article, reading_time in zip(articles, reading_times):
    result.append({
      'title': article.get('title', '').strip(),
      'category': category_name,
      'author': article.get('author', {}).get('name', '').strip(),
      'reading_time': reading_time,
      'published_date': article.get('_createdAt', ''),
    })

  return result

async def scraper(category):
  all_categories = await get_categories()
  if not all_categories:
    return 'error: connection error, try again', []

  allowed_categories = ['all'] + list(all_categories.keys())
  print(f"Allowed categories: {allowed_categories}")

  if category.lower() not in allowed_categories:
    return 'error: category not found', []

  posts = await get_blog_posts_for_category(category, all_categories)
  if not posts:
    return 'error: connection error, try again', []

  print(f"Total posts: {len(posts)}")
  return 'success', posts
