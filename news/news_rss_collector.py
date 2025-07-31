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
import hashlib
import os

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
        
        # Configurazione da settings.json
        news_config = self.config.get('news_trading', {})
        
        # RSS Feeds da configurazione
        self.rss_feeds = news_config.get('rss_feeds', {
            'marketwatch_pulse': 'https://feeds.content.dowjones.io/public/rss/mw_marketpulse',
            'investing_com': 'https://www.investing.com/rss/news.rss',
            'reuters_business': 'http://feeds.reuters.com/reuters/businessNews',
            'yahoo_finance_aapl': 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL&region=US&lang=en-US',
            'cnbc_markets': 'https://www.cnbc.com/id/15839135/device/rss/rss.html',
            'seeking_alpha': 'https://seekingalpha.com/feed.xml',
            'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
            'marketwatch': 'https://www.marketwatch.com/rss/topstories',
            'finviz': 'https://finviz.com/news.ashx?c=1',
            'benzinga': 'https://www.benzinga.com/rss/benzinga'
        })
        
        # Configurazioni di rate limiting
        self.update_interval = max(news_config.get('update_interval', 600), 
                                 news_config.get('min_update_interval', 300))  # Min 5 minuti
        self.user_agent = news_config.get('user_agent', 
                                        'StockAI-NewsBot/2.0 (+https://github.com/risik01/stock-ai)')
        self.request_timeout = news_config.get('request_timeout', 30)
        self.max_retries = news_config.get('max_retries', 3)
        self.etag_cache_enabled = news_config.get('etag_cache', True)
        
        # Cache per evitare duplicati e ETag
        self.processed_articles = set()
        self.news_cache = []
        self.etag_cache = {}
        self.last_modified_cache = {}
        self.last_fetch_time = {}
        self.cache_file = '../data/rss_cache.json'
        
        # Carica cache persistente
        self._load_cache()
        
        # Rate limiting warning
        if self.update_interval < 300:
            self.logger.warning(
                f"⚠️  ATTENZIONE: Intervallo di aggiornamento {self.update_interval}s < 5 minuti "
                "potrebbe causare blocchi dai server RSS! Raccomandato: >= 300s"
            )
        
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
        self.logger.info(f"Rate limiting: {self.update_interval}s tra aggiornamenti")
        self.logger.info(f"Feed RSS configurati: {len(self.rss_feeds)}")
    
    def _load_cache(self):
        """Carica cache persistente ETag e Last-Modified"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.etag_cache = cache_data.get('etags', {})
                    self.last_modified_cache = cache_data.get('last_modified', {})
                    self.last_fetch_time = cache_data.get('last_fetch', {})
                    self.logger.info(f"Cache caricata: {len(self.etag_cache)} ETags")
        except Exception as e:
            self.logger.warning(f"Errore caricamento cache: {e}")
            self.etag_cache = {}
            self.last_modified_cache = {}
            self.last_fetch_time = {}
    
    def _save_cache(self):
        """Salva cache persistente"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            cache_data = {
                'etags': self.etag_cache,
                'last_modified': self.last_modified_cache,
                'last_fetch': self.last_fetch_time,
                'saved_at': datetime.now().isoformat()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Errore salvataggio cache: {e}")
    
    def _should_fetch_feed(self, feed_name: str) -> bool:
        """Controlla se il feed deve essere aggiornato (rate limiting)"""
        last_fetch = self.last_fetch_time.get(feed_name, 0)
        time_since_fetch = time.time() - last_fetch
        
        if time_since_fetch < self.update_interval:
            remaining = self.update_interval - time_since_fetch
            self.logger.debug(f"Feed {feed_name}: rate limit attivo, {remaining:.0f}s rimanenti")
            return False
        
        return True
    
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
        """Raccoglie articoli da un singolo RSS feed con ETag e rate limiting"""
        try:
            # Controllo rate limiting
            if not self._should_fetch_feed(feed_name):
                return []
            
            self.logger.debug(f"Fetching RSS feed: {feed_name}")
            
            # Headers personalizzati con User-Agent e cache
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'application/rss+xml, application/xml, text/xml',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            # Aggiungi ETag e Last-Modified se disponibili
            if self.etag_cache_enabled:
                if feed_name in self.etag_cache:
                    headers['If-None-Match'] = self.etag_cache[feed_name]
                if feed_name in self.last_modified_cache:
                    headers['If-Modified-Since'] = self.last_modified_cache[feed_name]
            
            # Fetch feed con timeout e retry
            response = None
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(url, headers=headers, timeout=self.request_timeout)
                    
                    # Aggiorna ultimo fetch time
                    self.last_fetch_time[feed_name] = time.time()
                    
                    # Gestione 304 Not Modified
                    if response.status_code == 304:
                        self.logger.debug(f"Feed {feed_name}: nessun aggiornamento (304)")
                        return []
                    
                    # Gestione errori HTTP
                    if response.status_code >= 400:
                        if response.status_code == 429:
                            self.logger.warning(f"Rate limit per {feed_name}: {response.status_code}")
                            # Aumenta l'intervallo per questo feed
                            self.last_fetch_time[feed_name] = time.time() + (self.update_interval * 2)
                        else:
                            self.logger.error(f"Errore HTTP per {feed_name}: {response.status_code}")
                        return []
                    
                    # Salva ETag e Last-Modified
                    if self.etag_cache_enabled:
                        if 'etag' in response.headers:
                            self.etag_cache[feed_name] = response.headers['etag']
                        if 'last-modified' in response.headers:
                            self.last_modified_cache[feed_name] = response.headers['last-modified']
                    
                    break
                    
                except requests.exceptions.Timeout:
                    self.logger.warning(f"Timeout per {feed_name} (tentativo {attempt + 1})")
                    if attempt == self.max_retries - 1:
                        return []
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Errore network per {feed_name}: {str(e)}")
                    return []
            
            if not response:
                return []
            
            # Parse feed RSS
            feed = feedparser.parse(response.content)
            
            if feed.bozo and hasattr(feed, 'bozo_exception'):
                self.logger.warning(f"Feed malformato per {feed_name}: {feed.bozo_exception}")
                
            articles = []
            for entry in feed.entries:
                try:
                    # Estrai informazioni articolo
                    title = entry.get('title', 'No Title')
                    summary = entry.get('summary', entry.get('description', ''))
                    url = entry.get('link', '')
                    
                    # Parse data pubblicazione
                    published = self._parse_date(entry.get('published', ''))
                    if not published:
                        published = datetime.now()
                    
                    # Pulisci HTML dal summary
                    summary = self._clean_html(summary)
                    
                    # Estrai simboli menzionati
                    symbols = self._extract_symbols(title + ' ' + summary)
                    
                    # Crea oggetto articolo (accetta tutti gli articoli RSS finanziari)
                    article = NewsArticle(
                        title=title,
                        summary=summary,
                        url=url,
                        published=published,
                        source=feed_name,
                        symbols=symbols
                    )
                    
                    # Evita duplicati
                    article_hash = self._get_article_hash(article)
                    if article_hash not in self.processed_articles:
                        self.processed_articles.add(article_hash)
                        articles.append(article)
                        
                except Exception as e:
                    self.logger.warning(f"Errore parsing articolo da {feed_name}: {e}")
                    continue
            
            # Salva cache dopo fetch riuscito
            if self.etag_cache_enabled:
                self._save_cache()
            
            self.logger.info(f"Raccolti {len(articles)} articoli da {feed_name}")
            return articles
            
        except Exception as e:
            self.logger.error(f"Errore generale per feed {feed_name}: {str(e)}")
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
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse data da string RSS"""
        if not date_str:
            return None
        
        try:
            # Prova vari formati
            from email.utils import parsedate_to_datetime
            result = parsedate_to_datetime(date_str)
            # Converte a datetime naive (rimuove timezone info)
            if result.tzinfo is not None:
                result = result.replace(tzinfo=None)
            return result
        except:
            try:
                # Formato ISO
                result = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                # Converte a datetime naive
                if result.tzinfo is not None:
                    result = result.replace(tzinfo=None)
                return result
            except:
                # Altri formati comuni
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S',
                    '%a, %d %b %Y %H:%M:%S %Z',
                    '%a, %d %b %Y %H:%M:%S',
                    '%Y-%m-%d'
                ]
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except:
                        continue
                return None
    
    def _get_article_hash(self, article: NewsArticle) -> str:
        """Genera hash univoco per articolo"""
        content = f"{article.title}_{article.url}_{article.published.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _has_financial_content(self, text: str) -> bool:
        """Controlla se il testo ha contenuto finanziario rilevante"""
        text_lower = text.lower()
        financial_keywords = [
            'earnings', 'revenue', 'profit', 'stock', 'shares', 'market',
            'trading', 'investment', 'financial', 'economy', 'economic',
            'wall street', 'nasdaq', 'dow jones', 's&p', 'fed', 'federal reserve'
        ]
        return any(keyword in text_lower for keyword in financial_keywords)
        
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
