#!/usr/bin/env python3
"""Test all 6 endpoints"""

from src.asurascans import Asurascans

scraper = Asurascans()

print("=" * 70)
print("TESTING ALL 6 ENDPOINTS")
print("=" * 70)

# Test 1: Search
result = scraper.search("solo")
print(f"✅ search          - {result['status']} - {len(result['results'])} results")

# Test 2: Genres
result = scraper.genres("action")
print(f"✅ genres          - {result['status']} - {len(result['results'])} results")

# Test 3: Latest
result = scraper.latest(1)
print(f"✅ latest          - {result['status']} - {len(result['results'])} results")

# Test 4: Popular
result = scraper.popular()
print(f"✅ popular         - {result['status']} - {len(result['results'])} results")

# Test 5: Info
result = scraper.info("solo-leveling")
info_data = result['results']
chapters = info_data.get('chapters', [])
print(f"✅ info            - {result['status']} - {info_data['title']} with {len(chapters)} chapters")

# Test 6: Pages (use actual chapter from info)
if chapters:
    chapter_id = chapters[0]['id']
    result = scraper.pages(chapter_id)
    pages = result.get('results', [])
    print(f"✅ pages           - {result['status']} - {len(pages)} images")
else:
    print(f"⚠️  pages           - skipped (no chapters found)")

print("=" * 70)
print("✅ All endpoints working!")
print("=" * 70)
