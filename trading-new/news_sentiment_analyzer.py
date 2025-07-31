#!/usr/bin/env python3
"""
News Sentiment Analyzer - Analisi sentiment delle notizie finanziarie
Modulo per analizzare sentiment e importanza delle notizie per decisioni di trading
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import numpy as np
from dataclasses import dataclass
import yfinance as yf

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("⚠️ TextBlob non disponibile. Installa con: pip install textblob")

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("⚠️ VADER Sentiment non disponibile. Installa con: pip install vaderSentiment")

from news_rss_collector import NewsArticle

@dataclass
class SentimentScore:
    """Punteggio sentiment per un articolo"""
    polarity: float  # -1 (negativo) a +1 (positivo)
    subjectivity: float  # 0 (oggettivo) a 1 (soggettivo)
    confidence: float  # 0 a 1
    method: str  # metodo usato
    
@dataclass
class TradingSignal:
    """Segnale di trading basato su notizie"""
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    sentiment_score: float
    news_count: int
    reason: str
    timestamp: datetime
    news_articles: List[NewsArticle]

class NewsSentimentAnalyzer:
    """
    Analizzatore sentiment per notizie finanziarie
    """
    
    def __init__(self):
        """Inizializza l'analizzatore sentiment"""
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../data/sentiment_analyzer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Inizializza analyzer VADER se disponibile
        if VADER_AVAILABLE:
            self.vader_analyzer = SentimentIntensityAnalyzer()
        else:
            self.vader_analyzer = None
        
        # Dizionario sentiment finanziario personalizzato
        self.financial_sentiment_dict = {
            # Parole molto positive
            'breakthrough': 1.0, 'record': 0.8, 'beat': 0.7, 'surge': 0.8,
            'soar': 0.8, 'jump': 0.6, 'rally': 0.7, 'boom': 0.8,
            'bullish': 0.7, 'optimize': 0.6, 'upgrade': 0.7, 'outperform': 0.8,
            
            # Parole positive
            'growth': 0.5, 'increase': 0.4, 'rise': 0.4, 'gain': 0.5,
            'profit': 0.6, 'revenue': 0.3, 'expand': 0.5, 'innovation': 0.6,
            'partnership': 0.4, 'acquisition': 0.5, 'buyback': 0.6,
            
            # Parole molto negative
            'crash': -1.0, 'plunge': -0.8, 'collapse': -0.9, 'fraud': -0.9,
            'bankrupt': -1.0, 'scandal': -0.8, 'investigation': -0.7,
            'bearish': -0.7, 'downgrade': -0.7, 'underperform': -0.8,
            
            # Parole negative
            'decline': -0.4, 'fall': -0.4, 'drop': -0.5, 'loss': -0.6,
            'miss': -0.5, 'cut': -0.4, 'concern': -0.3, 'warning': -0.6,
            'lawsuit': -0.6, 'delay': -0.3, 'postpone': -0.3
        }
        
        # Moltiplicatori per intensità
        self.intensity_multipliers = {
            'very': 1.3, 'extremely': 1.5, 'highly': 1.2, 'significantly': 1.4,
            'massive': 1.6, 'huge': 1.4, 'major': 1.3, 'minor': 0.7,
            'slightly': 0.6, 'somewhat': 0.8, 'moderate': 0.9
        }
        
        # Simboli e loro settori per analisi contestuale
        self.symbol_sectors = {
            'AAPL': 'Technology', 'GOOGL': 'Technology', 'MSFT': 'Technology',
            'TSLA': 'Automotive/Energy', 'AMZN': 'E-commerce/Cloud',
            'META': 'Social Media', 'NVDA': 'Semiconductors'
        }
        
        self.logger.info("NewsSentimentAnalyzer inizializzato")
    
    def analyze_text_sentiment(self, text: str, method: str = 'hybrid') -> SentimentScore:
        """Analizza sentiment di un testo"""
        
        if method == 'textblob' and TEXTBLOB_AVAILABLE:
            return self._analyze_with_textblob(text)
        elif method == 'vader' and VADER_AVAILABLE:
            return self._analyze_with_vader(text)
        elif method == 'financial':
            return self._analyze_with_financial_dict(text)
        elif method == 'hybrid':
            return self._analyze_hybrid(text)
        else:
            # Fallback al dizionario finanziario
            return self._analyze_with_financial_dict(text)
    
    def _analyze_with_textblob(self, text: str) -> SentimentScore:
        """Analisi sentiment con TextBlob"""
        blob = TextBlob(text)
        
        return SentimentScore(
            polarity=blob.sentiment.polarity,
            subjectivity=blob.sentiment.subjectivity,
            confidence=0.7,  # TextBlob ha confidenza moderata
            method='textblob'
        )
    
    def _analyze_with_vader(self, text: str) -> SentimentScore:
        """Analisi sentiment con VADER"""
        scores = self.vader_analyzer.polarity_scores(text)
        
        # Converti compound score in polarity (-1 a +1)
        polarity = scores['compound']
        
        # Calcola subjectivity basata su intensità
        subjectivity = abs(scores['pos'] - scores['neg'])
        
        # Confidenza basata su intensità del compound score
        confidence = min(abs(polarity) * 1.5, 1.0)
        
        return SentimentScore(
            polarity=polarity,
            subjectivity=subjectivity,
            confidence=confidence,
            method='vader'
        )
    
    def _analyze_with_financial_dict(self, text: str) -> SentimentScore:
        """Analisi sentiment con dizionario finanziario personalizzato"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        sentiment_scores = []
        total_intensity = 0
        
        for i, word in enumerate(words):
            if word in self.financial_sentiment_dict:
                base_score = self.financial_sentiment_dict[word]
                
                # Controlla intensificatori nelle parole precedenti
                intensity = 1.0
                if i > 0 and words[i-1] in self.intensity_multipliers:
                    intensity = self.intensity_multipliers[words[i-1]]
                
                # Controlla negazioni
                if i > 0 and words[i-1] in ['not', 'no', 'never', 'without']:
                    base_score *= -0.8
                
                final_score = base_score * intensity
                sentiment_scores.append(final_score)
                total_intensity += abs(intensity)
        
        if not sentiment_scores:
            return SentimentScore(0.0, 0.0, 0.0, 'financial_dict')
        
        # Calcola sentiment medio
        polarity = np.mean(sentiment_scores)
        
        # Subjectivity basata su numero di parole sentiment trovate
        subjectivity = min(len(sentiment_scores) / len(words) * 2, 1.0)
        
        # Confidenza basata su numero di match e intensità
        confidence = min(len(sentiment_scores) / 10.0 + total_intensity / 20.0, 1.0)
        
        return SentimentScore(
            polarity=polarity,
            subjectivity=subjectivity,
            confidence=confidence,
            method='financial_dict'
        )
    
    def _analyze_hybrid(self, text: str) -> SentimentScore:
        """Analisi sentiment ibrida combinando più metodi"""
        scores = []
        
        # Prova tutti i metodi disponibili
        if TEXTBLOB_AVAILABLE:
            scores.append(self._analyze_with_textblob(text))
        
        if VADER_AVAILABLE:
            scores.append(self._analyze_with_vader(text))
        
        # Sempre includi dizionario finanziario
        scores.append(self._analyze_with_financial_dict(text))
        
        if not scores:
            return SentimentScore(0.0, 0.0, 0.0, 'none')
        
        # Calcola media ponderata (dizionario finanziario ha peso maggiore)
        weights = []
        for score in scores:
            if score.method == 'financial_dict':
                weights.append(0.5)  # Peso maggiore per dizionario finanziario
            else:
                weights.append(0.25)
        
        weights = np.array(weights)
        weights = weights / weights.sum()  # Normalizza
        
        polarity = np.average([s.polarity for s in scores], weights=weights)
        subjectivity = np.average([s.subjectivity for s in scores], weights=weights)
        confidence = np.average([s.confidence for s in scores], weights=weights)
        
        return SentimentScore(
            polarity=polarity,
            subjectivity=subjectivity,
            confidence=confidence,
            method='hybrid'
        )
    
    def analyze_article_sentiment(self, article: NewsArticle) -> SentimentScore:
        """Analizza sentiment di un singolo articolo"""
        # Combina titolo e summary (titolo ha peso maggiore)
        combined_text = f"{article.title} {article.title} {article.summary}"
        
        sentiment = self.analyze_text_sentiment(combined_text, method='hybrid')
        
        # Aggiorna articolo con sentiment
        article.sentiment = sentiment.polarity
        
        return sentiment
    
    def analyze_symbol_sentiment(self, articles: List[NewsArticle], symbol: str) -> Dict:
        """Analizza sentiment complessivo per un simbolo"""
        symbol_articles = [a for a in articles if symbol in a.symbols]
        
        if not symbol_articles:
            return {
                'symbol': symbol,
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'article_count': 0,
                'positive_articles': 0,
                'negative_articles': 0,
                'neutral_articles': 0
            }
        
        sentiments = []
        confidences = []
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for article in symbol_articles:
            sentiment = self.analyze_article_sentiment(article)
            sentiments.append(sentiment.polarity)
            confidences.append(sentiment.confidence)
            
            if sentiment.polarity > 0.1:
                positive_count += 1
            elif sentiment.polarity < -0.1:
                negative_count += 1
            else:
                neutral_count += 1
        
        # Calcola sentiment medio ponderato per confidenza
        weights = np.array(confidences)
        if weights.sum() > 0:
            avg_sentiment = np.average(sentiments, weights=weights)
        else:
            avg_sentiment = np.mean(sentiments)
        
        avg_confidence = np.mean(confidences)
        
        return {
            'symbol': symbol,
            'sentiment_score': avg_sentiment,
            'confidence': avg_confidence,
            'article_count': len(symbol_articles),
            'positive_articles': positive_count,
            'negative_articles': negative_count,
            'neutral_articles': neutral_count,
            'articles': symbol_articles
        }
    
    def generate_trading_signals(self, articles: List[NewsArticle], 
                                symbols: List[str]) -> List[TradingSignal]:
        """Genera segnali di trading basati su sentiment delle notizie"""
        signals = []
        
        for symbol in symbols:
            symbol_analysis = self.analyze_symbol_sentiment(articles, symbol)
            
            if symbol_analysis['article_count'] == 0:
                continue
            
            sentiment_score = symbol_analysis['sentiment_score']
            confidence = symbol_analysis['confidence']
            news_count = symbol_analysis['article_count']
            
            # Determina azione basata su sentiment e confidenza
            action = 'HOLD'
            reason = 'Sentiment neutrale'
            
            # Soglie per decisioni
            strong_positive_threshold = 0.3
            weak_positive_threshold = 0.1
            weak_negative_threshold = -0.1
            strong_negative_threshold = -0.3
            
            min_confidence = 0.3
            min_articles = 1
            
            if (sentiment_score > strong_positive_threshold and 
                confidence > min_confidence and news_count >= min_articles):
                action = 'BUY'
                reason = f"Sentiment molto positivo ({sentiment_score:.2f})"
                
            elif (sentiment_score > weak_positive_threshold and 
                  confidence > min_confidence and news_count >= 2):
                action = 'BUY'
                reason = f"Sentiment positivo con {news_count} notizie"
                
            elif (sentiment_score < strong_negative_threshold and 
                  confidence > min_confidence and news_count >= min_articles):
                action = 'SELL'
                reason = f"Sentiment molto negativo ({sentiment_score:.2f})"
                
            elif (sentiment_score < weak_negative_threshold and 
                  confidence > min_confidence and news_count >= 2):
                action = 'SELL'
                reason = f"Sentiment negativo con {news_count} notizie"
            
            # Aggiusta confidenza finale
            final_confidence = confidence * min(news_count / 3.0, 1.0)
            
            # Crea segnale
            signal = TradingSignal(
                symbol=symbol,
                action=action,
                confidence=final_confidence,
                sentiment_score=sentiment_score,
                news_count=news_count,
                reason=reason,
                timestamp=datetime.now(),
                news_articles=symbol_analysis['articles']
            )
            
            signals.append(signal)
        
        # Ordina per confidenza (più confidenti prima)
        signals.sort(key=lambda x: x.confidence, reverse=True)
        
        return signals
    
    def get_market_sentiment_overview(self, articles: List[NewsArticle], 
                                    symbols: List[str]) -> Dict:
        """Ottiene panoramica sentiment del mercato"""
        symbol_sentiments = {}
        
        for symbol in symbols:
            analysis = self.analyze_symbol_sentiment(articles, symbol)
            symbol_sentiments[symbol] = analysis
        
        # Calcola sentiment generale del mercato
        all_sentiments = [a['sentiment_score'] for a in symbol_sentiments.values() 
                         if a['article_count'] > 0]
        
        if all_sentiments:
            market_sentiment = np.mean(all_sentiments)
            sentiment_std = np.std(all_sentiments)
        else:
            market_sentiment = 0.0
            sentiment_std = 0.0
        
        # Classifica sentiment del mercato
        if market_sentiment > 0.2:
            market_mood = "Molto Bullish"
        elif market_sentiment > 0.05:
            market_mood = "Bullish"
        elif market_sentiment > -0.05:
            market_mood = "Neutrale"
        elif market_sentiment > -0.2:
            market_mood = "Bearish"
        else:
            market_mood = "Molto Bearish"
        
        return {
            'timestamp': datetime.now(),
            'market_sentiment': market_sentiment,
            'market_mood': market_mood,
            'sentiment_volatility': sentiment_std,
            'symbols_analyzed': len([s for s in symbol_sentiments.values() 
                                   if s['article_count'] > 0]),
            'total_articles': sum(s['article_count'] for s in symbol_sentiments.values()),
            'symbol_details': symbol_sentiments
        }
    
    def export_sentiment_analysis(self, analysis: Dict, filename: str = None) -> str:
        """Esporta analisi sentiment in JSON"""
        if filename is None:
            filename = f"../data/sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Converti datetime in string per JSON
        export_data = analysis.copy()
        if 'timestamp' in export_data:
            export_data['timestamp'] = export_data['timestamp'].isoformat()
        
        # Converti anche timestamp negli articoli
        for symbol_data in export_data.get('symbol_details', {}).values():
            if 'articles' in symbol_data:
                for article in symbol_data['articles']:
                    if hasattr(article, 'published'):
                        article.published = article.published.isoformat()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Analisi sentiment esportata in: {filename}")
        return filename

def main():
    """Funzione principale per testing"""
    from news_rss_collector import NewsRSSCollector
    
    print("🔄 Test News Sentiment Analyzer...")
    
    # Inizializza componenti
    collector = NewsRSSCollector()
    analyzer = NewsSentimentAnalyzer()
    
    # Raccoglie notizie
    print("📰 Raccolta notizie...")
    articles = collector.collect_all_news()
    
    if not articles:
        print("❌ Nessuna notizia trovata")
        return
    
    print(f"✅ Raccolti {len(articles)} articoli")
    
    # Analizza sentiment
    print("🔍 Analisi sentiment...")
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    
    # Panoramica mercato
    market_overview = analyzer.get_market_sentiment_overview(articles, symbols)
    
    print(f"\n📊 SENTIMENT MERCATO:")
    print(f"   🎯 Sentiment Generale: {market_overview['market_sentiment']:.3f}")
    print(f"   😊 Mood: {market_overview['market_mood']}")
    print(f"   📊 Volatilità: {market_overview['sentiment_volatility']:.3f}")
    print(f"   📰 Articoli Totali: {market_overview['total_articles']}")
    
    # Dettagli per simbolo
    print(f"\n📈 SENTIMENT PER SIMBOLO:")
    for symbol, data in market_overview['symbol_details'].items():
        if data['article_count'] > 0:
            sentiment = data['sentiment_score']
            emoji = "📈" if sentiment > 0.1 else "📉" if sentiment < -0.1 else "➡️"
            print(f"   {emoji} {symbol}: {sentiment:.3f} "
                  f"({data['positive_articles']}+ {data['negative_articles']}- "
                  f"{data['neutral_articles']}=)")
    
    # Genera segnali di trading
    print(f"\n🤖 SEGNALI DI TRADING:")
    signals = analyzer.generate_trading_signals(articles, symbols)
    
    for signal in signals[:5]:  # Mostra primi 5
        action_emoji = "🟢" if signal.action == 'BUY' else "🔴" if signal.action == 'SELL' else "🟡"
        print(f"   {action_emoji} {signal.symbol}: {signal.action} "
              f"(conf: {signal.confidence:.2f}) - {signal.reason}")
    
    # Esporta analisi
    export_file = analyzer.export_sentiment_analysis(market_overview)
    print(f"\n💾 Analisi esportata: {export_file}")

if __name__ == "__main__":
    main()
