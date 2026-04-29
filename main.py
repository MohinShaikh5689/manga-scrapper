import requests
from fastapi import FastAPI, Response
from urllib.parse import quote
from bs4 import BeautifulSoup

from src.asurascans import Asurascans
from src.mangapill import Mangapill

app = FastAPI()


@app.get("/")
def homepage():
    return {
        "message": "Welcome to the manga scrapers API",
        "available_providers": ["mangapill", "asurascans"],
    }


@app.get("/debug/asurascans")
def debug_asurascans(url: str = "https://asurascans.io/genres/action"):
    """Debug endpoint to check asurascans HTML"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Look for any divs with class 'bsx'
        all_bsx = soup.find_all("div", class_="bsx")
        
        # Also try to find all divs with any class that contains 'post' or 'item'
        all_divs = soup.find_all("div")
        
        # Get first 5 divs to see structure
        sample_divs = [str(d)[:200] for d in all_divs[:10]]
        
        # Try to find title tags
        titles = soup.find_all("h2") + soup.find_all("h3") + soup.find_all("a")
        
        return {
            "status": response.status_code,
            "total_divs": len(all_divs),
            "bsx_divs_found": len(all_bsx),
            "titles_found": len(titles),
            "first_titles": [str(t)[:100] for t in titles[:3]],
            "sample_divs": sample_divs,
            "full_html_sample": response.text[1000:2000]
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@app.head("/")
async def read_root_head():
    return Response(headers={"Custom-Header": "Value"})


# Mangapill
@app.get("/mangapill/{category}/{path:path}")
def mangapill(category: str, path: str):
    if category == "search":
        return Mangapill().search(query=path)
    elif category == "info":
        return Mangapill().info(id=path)
    elif category == "pages":
        return Mangapill().pages(id=path)
    elif category == "newest":
        return Mangapill().new()
    elif category == "recent":
        return Mangapill().recent()
    elif category == "images":
        if path:
            # FastAPI's path param strips a slash from "://", restore it
            if path.startswith("https:/") and not path.startswith("https://"):
                path = path.replace("https:/", "https://", 1)
            elif path.startswith("http:/") and not path.startswith("http://"):
                path = path.replace("http:/", "http://", 1)
            headers = {"Referer": "https://mangapill.com/"}
            content = requests.get(url=path, headers=headers).content
            return Response(content=content, media_type="image/jpg")
        else:
            return {"detail": "image url is required"}
    else:
        return {"detail": "Invalid parameter"}


# Asurascans
@app.get("/asurascans/{category}/{path:path}")
def asurascans(category: str, path: str):
    if category == "search":
        if path:
            newQuery = path.replace(" ", "+")
            return Asurascans().search(query=newQuery)
    elif category == "info":
        return Asurascans().info(id=path)
    elif category == "pages":
        return Asurascans().pages(id=path)
    elif category == "popular":
        return Asurascans().popular()
    elif category == "latest":
        return Asurascans().latest(page=path)
    elif category == "genres":
        return Asurascans().genres(type=path)
    elif category == "genre-list":
        return {
            "endpoint": "asurascans",
            "genres": "action, adventure, comedy, romance",
        }
    else:
        return {"detail": "Invalid parameter"}
