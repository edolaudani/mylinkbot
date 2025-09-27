import os
import feedparser
import requests
import json
import openai

# -----------------------------
# CONFIGURAZIONE DA VARIABILI D'AMBIENTE
# -----------------------------
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
RSS_FEED = os.getenv("RSS_FEED")

openai.api_key = OPENAI_KEY

# Headers per Notion API
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# -----------------------------
# FUNZIONE PER USARE OPENAI
# -----------------------------
def extract_details_with_ai(title, description):
    prompt = f"""
    Extract the company name and location from this job listing.
    Title: {title}
    Description: {description}
    Return as JSON with keys "company" and "location". If not found, return empty strings. Very important: description cannot exceed 1500 characters.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        text = response['choices'][0]['message']['content']
        result = json.loads(text)
        return result.get("company", ""), result.get("location", "")
    except Exception as e:
        print(f"⚠️ AI extraction failed: {e}")
        return "", ""

# -----------------------------
# FUNZIONE PER CREARE UNA PAGINA IN NOTION
# -----------------------------
def add_to_notion(item):
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": item.get("title", "No Title")}}]},
            "Link": {"url": item.get("link")},
            "Company": {"rich_text": [{"text": {"content": item.get("company", "")}}]},
            "Location": {"rich_text": [{"text": {"content": item.get("location", "")}}]},
            "Description": {"rich_text": [{"text": {"content": item.get("description", "")}}]}
        }
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, data=json.dumps(data))
    
    if response.status_code in [200, 201]:
        print(f"✅ Added: {item.get('title')}")
    else:
        print(f"❌ Failed to add: {item.get('title')} - {response.text}")

# -----------------------------
# PARSING RSS
# -----------------------------
feed = feedparser.parse(RSS_FEED)

for entry in feed.entries:
    title = entry.get("title", "")
    link = entry.get("link", "")
    description = entry.get("summary", "")

    # Estrai company e location con AI
    company, location = extract_details_with_ai(title, description)

    # Prepara il dizionario con i campi
    item = {
        "title": title,
        "link": link,
        "description": description,
        "company": company,
        "location": location
    }

    # Inserisci nella Notion
    add_to_notion(item)

print("Done.")

