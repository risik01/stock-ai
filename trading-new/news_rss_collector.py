#!/usr/bin/env python3
"""
News RSS Feed Collector - Raccolta notizie finanziarie in tempo reale
Modulo per raccogliere e analizzare notizie dai principali RSS feeds finanziari
"""

import feedparser
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import time
import re
from urllib.parse import urljoin
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class NewsArticle:
    """Struttura per un articolo di notizie"""
    title: str
    summary: str
    url: str
    published: datetime
    source: str
    symbols: List[str]
    sentiment: Optional[float] = None
    importance: Optional[float] = None
    category: Optional[str] = None

class NewsRSSCollector:
    """
    Collettore di notizie finanziarie da RSS feeds
    """
    
    def __init__(self, config_path: str = "../config/settings.json"):
        """Inizializza il collettore RSS"""
        self.config = self._load_config(config_path)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../data/news_collector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # RSS Feeds principali
        self.rss_feeds = {
            'yahoo_finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'cnbc': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'reuters_business': 'https://feeds.reuters.com/reuters/businessNews',
            'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
            'seeking_alpha': 'https://seekingalpha.com/feed.xml',
            'benzinga': 'https://feeds.benzinga.com/benzinga',
            'finviz': 'https://finviz.com/news.ashx',
            'investing_com': 'https://www.investing.com/rss/news.rss',
            'zacks': 'https://www.zacks.com/rss/articles.xml'
        }
        
        # Cache per evitare duplicati
        self.processed_articles = set()
        self.news_cache = []
        
        # Simboli da monitorare
        self.monitored_symbols = self.config.get('data', {}).get('symbols', 
            ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA'])
        
        # Keywords finanziarie importanti
        self.financial_keywords = {
            'positive': [
                'earnings beat', 'revenue growth', 'profit increase', 'buyback',
                'acquisition', 'partnership', 'expansion', 'innovation',
                'breakthrough', 'record high', 'outperform', 'upgrade',
                'strong guidance', 'beat expectations', 'dividend increase'
            ],
            'negative': [
                'earnings miss', 'revenue decline', 'loss', 'lawsuit',
                'investigation', 'downgrade', 'sell-off', 'bearish',
                'recession', 'bankruptcy', 'fraud', 'warning',
                'guidance cut', 'miss expectations', 'dividend cut'
            ],
            'neutral': [
                'conference', 'meeting', 'announcement', 'report',
                'statement', 'update', 'schedule', 'calendar'
            ]
        }
        
        self.logger.info("NewsRSSCollector inizializzato con successo")
    
    def _load_config(self, config_path: str) -> Dict:
        """Carica configurazione"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file non trovato: {config_path}")
            return {}
        except Exception as e:
            self.logger.error(f"Errore caricamento config: {e}")
            return {}
    
    def fetch_rss_feed(self, feed_name: str, url: str) -> List[NewsArticle]:
        """Raccoglie articoli da un singolo RSS feed"""
        try:
            self.logger.debug(f"Fetching RSS feed: {feed_name}")
            
            # Headers per simulare browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Fetch feed con timeout
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                self.logger.warning(f"Feed malformato per {feed_name}: {feed.bozo_exception}")
            
            articles = []
            
            for entry in feed.entries:
                try:
                    # Estrai data pubblicazione
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6])
                    else:
                        published = datetime.now()
                    
                    # Estrai contenuto
                    title = getattr(entry, 'title', 'No Title')
                    summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
                    url = getattr(entry, 'link', '')
                    
                    # Pulisci HTML dal summary
                    summary = self._clean_html(summary)
                    
                    # Cerca simboli menzionati
                    symbols = self._extract_symbols(title + ' ' + summary)
                    
                    # Crea articolo solo se ha simboli rilevanti o keywords finanziarie
                    if symbols or self._has_financial_content(title + ' ' + summary):
                        article = NewsArticle(
                            title=title,
                            summary=summary,
                            url=url,
                            published=published,
                            source=feed_name,
                            symbols=symbols
                        )
                        
                        # Evita duplicati
                        article_id = f"{title}_{url}"
                        if article_id not in self.processed_articles:
                            articles.append(article)
                            self.processed_articles.add(article_id)
                
                except Exception as e:
                    self.logger.warning(f"Errore processing entry da {feed_name}: {e}")
                    continue
            
            self.logger.info(f"Raccolti {len(articles)} articoli da {feed_name}")
            return articles
            
        except requests.RequestException as e:
            self.logger.error(f"Errore network per {feed_name}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Errore generico per {feed_name}: {e}")
            return []
    
    def _clean_html(self, text: str) -> str:
        """Rimuove tag HTML dal testo"""
        import re
        # Rimuovi tag HTML
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        # Rimuovi entità HTML
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        # Normalizza spazi
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _extract_symbols(self, text: str) -> List[str]:
        """Estrae simboli azionari dal testo"""
        symbols = []
        text_upper = text.upper()
        
        # Cerca simboli monitorati
        for symbol in self.monitored_symbols:
            # Pattern per trovare simboli
            patterns = [
                rf'\b{symbol}\b',  # Simbolo esatto
                rf'\${symbol}\b',  # Con dollaro
                rf'\({symbol}\)',  # Tra parentesi
                rf'{symbol}:'      # Con due punti
            ]
            
            for pattern in patterns:
                if re.search(pattern, text_upper):
                    if symbol not in symbols:
                        symbols.append(symbol)
                    break
        
        # Cerca anche nomi aziende comuni
        company_mappings = {
            'APPLE': 'AAPL',
            'GOOGLE': 'GOOGL',
            'ALPHABET': 'GOOGL',
            'MICROSOFT': 'MSFT',
            'TESLA': 'TSLA',
            'AMAZON': 'AMZN',
            'META': 'META',
            'FACEBOOK': 'META',
            'NVIDIA': 'NVDA'
        }
        
        for company, symbol in company_mappings.items():
            if company in text_upper and symbol not in symbols:
                symbols.append(symbol)
        
        return symbols
    
    def _has_financial_content(self, text: str) -> bool:
        """Verifica se il testo contiene contenuto finanziario rilevante"""
        text_lower = text.lower()
        
        financial_terms = [
            'stock', 'shares', 'earnings', 'revenue', 'profit', 'loss',
            'market', 'trading', 'investment', 'dividend', 'buyback',
            'acquisition', 'merger', 'ipo', 'nasdaq', 'nyse', 'sp500',
            'dow jones', 'portfolio', 'analyst', 'upgrade', 'downgrade'
        ]
        
        return any(term in text_lower for term in financial_terms)
    
    def collect_all_news(self, max_workers: int = 5) -> List[NewsArticle]:
        """Raccoglie notizie da tutti i feed RSS in parallelo"""
        all_articles = []
        
        self.logger.info("Avvio raccolta notizie da tutti i feed RSS...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Invia richieste per tutti i feed
            future_to_feed = {
                executor.submit(self.fetch_rss_feed, name, url): name 
                for name, url in self.rss_feeds.items()
            }
            
            # Raccogli risultati
            for future in as_completed(future_to_feed):
                feed_name = future_to_feed[future]
                try:
                    articles = future.result(timeout=60)
                    all_articles.extend(articles)
                except Exception as e:
                    self.logger.error(f"Errore raccolta feed {feed_name}: {e}")
        
        # Ordina per data (più recenti prima)
        all_articles.sort(key=lambda x: x.published, reverse=True)
        
        # Filtra articoli troppo vecchi (solo ultime 24 ore)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_articles = [a for a in all_articles if a.published > cutoff_time]
        
        self.logger.info(f"Raccolti {len(recent_articles)} articoli recenti da {len(self.rss_feeds)} feed")
        
        # Aggiorna cache
        self.news_cache = recent_articles
        
        return recent_articles
    
    def get_symbol_news(self, symbol: str, limit: int = 10) -> List[NewsArticle]:
        """Ottiene notizie specifiche per un simbolo"""
        symbol_articles = [
            article for article in self.news_cache 
            if symbol in article.symbols
        ]
        
        return symbol_articles[:limit]
    
    def get_breaking_news(self, minutes: int = 30) -> List[NewsArticle]:
        """Ottiene notizie breaking degli ultimi N minuti"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        breaking_news = [
            article for article in self.news_cache 
            if article.published > cutoff_time
        ]
        
        return breaking_news
    
    def analyze_news_volume(self) -> Dict[str, int]:
        """Analizza il volume di notizie per simbolo"""
        volume_analysis = {}
        
        for symbol in self.monitored_symbols:
            symbol_news = self.get_symbol_news(symbol)
            volume_analysis[symbol] = len(symbol_news)
        
        return volume_analysis
    
    def export_news_data(self, filename: str = None) -> str:
        """Esporta dati notizie in JSON"""
        if filename is None:
            filename = f"../data/news_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = []
        for article in self.news_cache:
            export_data.append({
                'title': article.title,
                'summary': article.summary,
                'url': article.url,
                'published': article.published.isoformat(),
                'source': article.source,
                'symbols': article.symbols,
                'sentiment': article.sentiment,
                'importance': article.importance,
                'category': article.category
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Dati notizie esportati in: {filename}")
        return filename
    
    def start_continuous_monitoring(self, interval_minutes: int = 15):
        """Avvia monitoraggio continuo delle notizie"""
        self.logger.info(f"Avvio monitoraggio continuo ogni {interval_minutes} minuti")
        
        def monitoring_loop():
            while True:
                try:
                    self.collect_all_news()
                    
                    # Analizza breaking news
                    breaking = self.get_breaking_news(minutes=interval_minutes)
                    if breaking:
                        self.logger.info(f"🚨 {len(breaking)} breaking news trovate!")
                        for news in breaking[:3]:  # Mostra solo le prime 3
                            self.logger.info(f"   📰 {news.title} - {news.symbols}")
                    
                    # Attendi prossimo ciclo
                    time.sleep(interval_minutes * 60)
                    
                except KeyboardInterrupt:
                    self.logger.info("Monitoraggio fermato dall'utente")
                    break
                except Exception as e:
                    self.logger.error(f"Errore nel monitoraggio: {e}")
                    time.sleep(60)  # Attendi 1 minuto prima di riprovare
        
        # Avvia in thread separato
        monitoring_thread = threading.Thread(target=monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        return monitoring_thread

def main():
    """Funzione principale per testing"""
    collector = NewsRSSCollector()
    
    print("🔄 Raccolta notizie finanziarie...")
    articles = collector.collect_all_news()
    
    print(f"\n📊 Raccolti {len(articles)} articoli")
    
    # Mostra statistiche per simbolo
    volume_analysis = collector.analyze_news_volume()
    print("\n📈 Volume notizie per simbolo:")
    for symbol, count in sorted(volume_analysis.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"   {symbol}: {count} articoli")
    
    # Mostra ultime breaking news
    breaking = collector.get_breaking_news(minutes=60)
    if breaking:
        print(f"\n🚨 Breaking News (ultima ora):")
        for news in breaking[:5]:
            symbols_str = ', '.join(news.symbols) if news.symbols else 'General'
            print(f"   📰 {news.title}")
            print(f"      🏷️  {symbols_str} | 🕒 {news.published.strftime('%H:%M')} | 📡 {news.source}")
    
    # Esporta dati
    export_file = collector.export_news_data()
    print(f"\n💾 Dati esportati: {export_file}")

if __name__ == "__main__":
    main()
