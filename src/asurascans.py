import requests
from bs4 import BeautifulSoup


class Asurascans:
    def __init__(self) -> None:
        self.parent_url = "https://asurascans.com"
        self.results = {"status": "", "results": []}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def _get_rendered(self, url):
        """Get page content with proper headers"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"[_get_rendered] Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[_get_rendered] Error: {e}")
            return None

    def search(self, query: str):
        try:
            url = f"{self.parent_url}/browse?q={query}"
            content = self._get_rendered(url)
            
            if not content:
                self.results["status"] = 0
                self.results["results"] = []
                return self.results
            
            self.results["status"] = 200
            soup = BeautifulSoup(content, "html.parser")
            
            # Find all series cards
            cards = soup.find_all("div", class_="series-card")
            parsed_content = []

            for card in cards:
                try:
                    temp_content = {}
                    
                    # Find the link with /comics/
                    link = card.find("a", href=lambda x: x and "/comics/" in x)
                    if not link:
                        continue
                    
                    # Extract title from img alt or h3
                    img = card.find("img")
                    if img and img.get("alt"):
                        temp_content["title"] = img.get("alt")
                    else:
                        h3 = card.find("h3")
                        if h3:
                            temp_content["title"] = h3.get_text(strip=True)
                    
                    if not temp_content.get("title"):
                        continue
                    
                    # Extract ID from href
                    href = link.get("href", "")
                    if href:
                        temp_content["id"] = href.split("/")[-1]
                    
                    # Extract image URL
                    if img:
                        temp_content["image"] = img.get("src", "")
                    
                    # Extract chapter count
                    for span in card.find_all("span"):
                        text = span.get_text(strip=True)
                        if "Ch" in text and any(c.isdigit() for c in text):
                            import re
                            match = re.search(r'\d+', text)
                            if match:
                                temp_content["chapters"] = match.group()
                            break
                    
                    parsed_content.append(temp_content)
                except Exception as e:
                    continue

            self.results["results"] = parsed_content
            return self.results
        except Exception as e:
            self.results["status"] = 0
            self.results["results"] = []
            return self.results

    def info(self, id: str):
        try:
            url = f"{self.parent_url}/comics/{id}"
            html_content = self._get_rendered(url)
            
            if not html_content:
                self.results["status"] = 0
                self.results["results"] = {}
                return self.results
            
            self.results["status"] = 200
            soup = BeautifulSoup(html_content, "html.parser")

            info = {}
            info["id"] = id
            
            # Title
            title_elem = soup.find("h1")
            info["title"] = title_elem.get_text(strip=True) if title_elem else ""
            
            # Description
            desc_elem = soup.find("div", id="description-text")
            if desc_elem:
                p_tag = desc_elem.find("p")
                info["description"] = p_tag.get_text(strip=True) if p_tag else ""
            else:
                info["description"] = ""
            
            # Status - look for the status badge with specific text color
            status_spans = soup.find_all("span", class_=lambda x: x and "text-[#A78BFA]" in x)
            info["status"] = status_spans[0].get_text(strip=True).lower() if status_spans else "unknown"
            
            # Type - look for type badge
            type_spans = soup.find_all("span", class_=lambda x: x and "text-[#913FE2]" in x and "uppercase" in x)
            info["type"] = type_spans[0].get_text(strip=True).lower() if type_spans else "unknown"
            
            # Author and Artist
            author_link = soup.find("a", href=lambda x: x and "?author=" in x)
            info["author"] = author_link.get_text(strip=True) if author_link else ""
            
            artist_link = soup.find("a", href=lambda x: x and "?artist=" in x)
            info["artist"] = artist_link.get_text(strip=True) if artist_link else ""
            
            # Genres
            genre_links = soup.find_all("a", href=lambda x: x and "?genres=" in x)
            info["genres"] = [g.get_text(strip=True) for g in genre_links]
            
            # Cover image
            cover_img = soup.find("img", src=lambda x: x and "cdn.asurascans.com/asura-images/covers/" in x)
            info["image"] = cover_img.get("src") if cover_img else ""
            
            # Chapters list
            chapter_links = soup.find_all("a", href=lambda x: x and "/chapter/" in x)
            chapters = []
            for link in chapter_links:
                try:
                    href = link.get("href", "")
                    # Extract chapter number from the end of href
                    chapter_num = href.rsplit("/", 1)[-1]
                    
                    # Get chapter title from font-medium span
                    chapter_title_span = link.find("span", class_="font-medium")
                    chapter_title = chapter_title_span.get_text(strip=True) if chapter_title_span else f"Chapter {chapter_num}"
                    
                    # Get date from text-white/40 span (last span with date)
                    date_span = link.find("span", class_="text-white/40")
                    chapter_date = date_span.get_text(strip=True) if date_span else ""
                    
                    chapters.append({
                        "number": chapter_num,
                        "title": chapter_title,
                        "date": chapter_date,
                        "id": href.lstrip("/")  # Store full path without leading slash
                    })
                except:
                    pass
            
            info["chapters"] = chapters
            
            self.results["results"] = info
            return self.results
        except Exception as e:
            self.results["status"] = 0
            self.results["results"] = {"error": str(e)}
            return self.results

    def pages(self, id: str):
        try:
            # id should be in format "comics/manga-id-suffix/chapter/number"
            # Ensure it starts with "comics/" for proper URL construction
            if not id.startswith("comics/"):
                # Fallback: try to construct from the id
                id = f"comics/{id}"
            
            url = f"{self.parent_url}/{id}"
            html_content = self._get_rendered(url)
            
            if not html_content:
                self.results["status"] = 0
                self.results["results"] = []
                return self.results
            
            self.results["status"] = 200
            soup = BeautifulSoup(html_content, "html.parser")

            # Find all images in the reader - they may use data-src or src attributes
            # Look for img tags within the reader area
            img_tags = soup.find_all("img", src=lambda x: x and ("cdn.asurascans.com" in x or x.startswith("/")))
            
            # Also check for images with data-src attribute
            pages = []
            for img in img_tags:
                img_src = img.get("src") or img.get("data-src")
                if img_src and "asurascans" in img_src:
                    pages.append(img_src)
            
            # If no images found, try alternative selectors for different page layouts
            if not pages:
                # Try finding images in common reader containers
                reader_area = soup.find("div", class_=lambda x: x and ("reader" in x.lower() or "chapter" in x.lower()))
                if reader_area:
                    img_tags = reader_area.find_all("img")
                    pages = [img.get("src") or img.get("data-src") for img in img_tags if img.get("src") or img.get("data-src")]
            
            self.results["results"] = pages
            return self.results

        except Exception as e:
            self.results["status"] = 0
            self.results["results"] = {"error": str(e)}
            return self.results

    def popular(self):
        try:
            url = f"{self.parent_url}/series-ranking"
            content = self._get_rendered(url)
            
            if not content:
                self.results["status"] = 0
                self.results["results"] = []
                return self.results
            
            self.results["status"] = 200
            soup = BeautifulSoup(content, "html.parser")
            
            # Find the ranking list container
            ranking_list = soup.find("div", class_="comics-ranking-list")
            if not ranking_list:
                self.results["results"] = []
                return self.results
            
            # Get direct <a> children (ranking items)
            links = ranking_list.find_all("a", recursive=False, href=lambda x: x and "/comics/" in x)
            parsed_content = []

            for link in links:
                try:
                    temp_content = {}
                    
                    # Extract title from img alt
                    img = link.find("img")
                    if img and img.get("alt"):
                        temp_content["title"] = img.get("alt")
                    else:
                        # Try to find span with title
                        span = link.find("span", class_=lambda x: x and "font-semibold" in x)
                        if span:
                            temp_content["title"] = span.get_text(strip=True)
                    
                    if not temp_content.get("title"):
                        continue
                    
                    # Extract ID from href
                    href = link.get("href", "")
                    if href:
                        temp_content["id"] = href.split("/")[-1]
                    
                    # Extract image URL
                    if img:
                        temp_content["image"] = img.get("src", "")
                    
                    parsed_content.append(temp_content)
                except Exception as e:
                    continue

            self.results["results"] = parsed_content
            return self.results
        except Exception as e:
            self.results["status"] = 0
            self.results["results"] = []
            return self.results

    def latest(self, page: str = "1"):
        try:
            url = f"{self.parent_url}/browse?sort=updated"
            if page != "1":
                url += f"&page={page}"
            content = self._get_rendered(url)
            
            if not content:
                self.results["status"] = 0
                self.results["results"] = []
                return self.results
            
            self.results["status"] = 200
            soup = BeautifulSoup(content, "html.parser")
            
            # Find all series cards
            cards = soup.find_all("div", class_="series-card")
            parsed_content = []

            for card in cards:
                try:
                    temp_content = {}
                    
                    # Find the link with /comics/
                    link = card.find("a", href=lambda x: x and "/comics/" in x)
                    if not link:
                        continue
                    
                    # Extract title from img alt or h3
                    img = card.find("img")
                    if img and img.get("alt"):
                        temp_content["title"] = img.get("alt")
                    else:
                        h3 = card.find("h3")
                        if h3:
                            temp_content["title"] = h3.get_text(strip=True)
                    
                    if not temp_content.get("title"):
                        continue
                    
                    # Extract ID from href
                    href = link.get("href", "")
                    if href:
                        temp_content["id"] = href.split("/")[-1]
                    
                    # Extract image URL
                    if img:
                        temp_content["image"] = img.get("src", "")
                    
                    # Extract chapter count
                    for span in card.find_all("span"):
                        text = span.get_text(strip=True)
                        if "Ch" in text and any(c.isdigit() for c in text):
                            import re
                            match = re.search(r'\d+', text)
                            if match:
                                temp_content["chapters"] = match.group()
                            break
                    
                    parsed_content.append(temp_content)
                except Exception as e:
                    continue

            self.results["results"] = parsed_content
            return self.results
        except Exception as e:
            self.results["status"] = 0
            self.results["results"] = []
            return self.results

    def genres(self, type: str):
        try:
            url = f"{self.parent_url}/browse?genres={type}"
            content = self._get_rendered(url)
            
            if not content:
                self.results["status"] = 0
                self.results["results"] = []
                return self.results
            
            self.results["status"] = 200
            soup = BeautifulSoup(content, "html.parser")
            
            # Find all series cards (new asurascans.com structure)
            cards = soup.find_all("div", class_="series-card")
            parsed_content = []

            for card in cards:
                try:
                    temp_content = {}
                    
                    # Find the link with /comics/
                    link = card.find("a", href=lambda x: x and "/comics/" in x)
                    if not link:
                        continue
                    
                    # Extract title from img alt or h3
                    img = card.find("img")
                    if img and img.get("alt"):
                        temp_content["title"] = img.get("alt")
                    else:
                        h3 = card.find("h3")
                        if h3:
                            temp_content["title"] = h3.get_text(strip=True)
                    
                    if not temp_content.get("title"):
                        continue
                    
                    # Extract ID from href
                    href = link.get("href", "")
                    if href:
                        # href is like /comics/omniscient-readers-viewpoint-0984835a
                        temp_content["id"] = href.split("/")[-1]
                    
                    # Extract image URL
                    if img:
                        temp_content["image"] = img.get("src", "")
                    
                    # Extract chapter count
                    for span in card.find_all("span"):
                        text = span.get_text(strip=True)
                        if "Ch" in text and any(c.isdigit() for c in text):
                            # Extract just the number
                            import re
                            match = re.search(r'\d+', text)
                            if match:
                                temp_content["chapters"] = match.group()
                            break
                    
                    parsed_content.append(temp_content)
                except Exception as e:
                    continue

            self.results["results"] = parsed_content
            return self.results
        except Exception as e:
            self.results["status"] = 0
            self.results["results"] = []
            return self.results
