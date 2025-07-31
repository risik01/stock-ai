#!/usr/bin/env python3
"""
Debug RSS feed parser
"""

import requests
import feedparser
import time

def debug_rss():
    url = "https://www.investing.com/rss/news.rss"
    headers = {
        'User-Agent': 'StockAI-NewsBot/2.0 (+https://github.com/risik01/stock-ai)'
    }
    
    print("🔍 DEBUG RSS PARSING")
    print("="*50)
    
    # 1. Test connessione
    print("1️⃣ Test connessione...")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"   Content-Length: {len(response.content)} bytes")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return
    
    # 2. Test parsing
    print("\n2️⃣ Test parsing feedparser...")
    try:
        feed = feedparser.parse(response.content)
        print(f"   Feed title: {feed.feed.get('title', 'No title')}")
        print(f"   Entries found: {len(feed.entries)}")
        print(f"   Bozo error: {feed.bozo}")
        if feed.bozo:
            print(f"   Bozo exception: {feed.bozo_exception}")
    except Exception as e:
        print(f"   ❌ Errore parsing: {e}")
        return
    
    # 3. Test primi entry
    if feed.entries:
        print("\n3️⃣ Primi 2 entry:")
        for i, entry in enumerate(feed.entries[:2]):
            print(f"\n   Entry {i+1}:")
            print(f"     Title: {entry.get('title', 'No title')}")
            print(f"     Published: {entry.get('published', 'No date')}")
            print(f"     Link: {entry.get('link', 'No link')}")
            print(f"     Summary: {entry.get('summary', 'No summary')[:100]}...")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    debug_rss()
