import os
import feedparser
import requests
import time
import json

# --- CONFIG ---
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

RSS_URL = "https://rss.app/feeds/Y68rj3ThBhhTnpTI.xml"

HEADERS_NOTION = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

CACHE_FILE = "notion_rss_cache.json"

# --- FUNZIONI UTILI ---
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_cache(urls):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(urls, f, ensure_ascii=False, indent=2)

def send_to_notion(title, link):
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "title": {"title": [{"text": {"content": title}}]},
            "link": {"url": link}
        }
    }
    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS_NOTION, json=payload)
    if response.status_code == 200:
        print(f"✅ Added to Notion: {title}")
        return True
    else:
        print(f"❌ Failed to add: {title} - {response.text}")
        return False

# --- SCRIPT PRINCIPALE ---
def main():
    cache = load_cache()
    feed = feedparser.parse(RSS_URL)
    new_links = []

    for entry in feed.entries:
        if entry.link not in cache:
            if send_to_notion(entry.title, entry.link):
                cache.append(entry.link)
                new_links.append(entry.link)
            time.sleep(1)  # evita troppi request rapidi

    if new_links:
        save_cache(cache)
        print(f"🎉 Added {len(new_links)} new items to Notion!")
    else:
        print("ℹ️ No new items to add.")

if __name__ == "__main__":
    main()
