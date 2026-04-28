import requests
from fastapi import FastAPI, Response
from urllib.parse import quote

from src.asurascans import Asurascans
from src.mangapill import Mangapill

app = FastAPI()


@app.get("/")
def homepage():
    return {
        "message": "Welcome to the manga scrapers API",
        "available_providers": ["mangapill", "asurascans"],
    }


@app.get("/debug/proxy")
def debug_proxy(url: str):
    """Debug endpoint to check what proxy returns"""
    proxy_url = "https://sup-proxy.zephex0-f6c.workers.dev/api-text?url="
    encoded_url = quote(url, safe=':/')
    full_url = f"{proxy_url}{encoded_url}"
    try:
        response = requests.get(full_url, timeout=10)
        return {
            "status": response.status_code,
            "content_length": len(response.content),
            "first_500_chars": response.text[:500],
            "proxy_url": full_url
        }
    except Exception as e:
        return {"error": str(e)}


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
