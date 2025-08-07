#!/usr/bin/env python3
"""
AI Background Training System
Sistema per addestrare l'AI in background per giorni/settimane
prima di lanciare il trading reale
"""

import os
import sys
import json
import time
import asyncio
import logging
import signal
import pickle
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# Setup logging
log_dir = Path("../logs/training")  # logs/training invece di data/training
log_dir.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'ai_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

sys.path.append('src')

class AIKnowledgeBase:
    """Base di conoscenza dell'AI che si accumula nel tempo"""
    
    def __init__(self):
        self.market_patterns = {}
        self.symbol_behaviors = {}
        self.successful_strategies = []
        self.failed_strategies = []
        self.market_correlations = {}
        self.news_impact_analysis = {}
        self.volatility_patterns = {}
        self.training_start_time = datetime.now()
        self.total_observations = 0
        self.accuracy_metrics = {
            'prediction_accuracy': 0.0,
            'profit_predictions': 0,
            'loss_predictions': 0,
            'total_predictions': 0
        }
        
    def add_market_observation(self, symbol, price_data, news_sentiment, market_context):
        """Aggiunge osservazione di mercato alla knowledge base"""
        timestamp = datetime.now()
        
        # Analizza pattern del simbolo
        if symbol not in self.symbol_behaviors:
            self.symbol_behaviors[symbol] = {
                'price_history': [],
                'volatility_history': [],
                'news_correlation': [],
                'best_buy_times': [],
                'best_sell_times': [],
                'loss_patterns': []
            }
        
        # Calcola metriche
        if len(price_data) >= 2:
            current_price = price_data[-1]
            previous_price = price_data[-2]
            change_pct = (current_price - previous_price) / previous_price
            
            # Analizza volatilità
            volatility = np.std(price_data[-10:]) if len(price_data) >= 10 else 0
            
            # Salva osservazioni
            self.symbol_behaviors[symbol]['price_history'].append({
                'timestamp': timestamp,
                'price': current_price,
                'change_pct': change_pct,
                'volatility': volatility,
                'news_sentiment': news_sentiment
            })
            
            # Analizza correlazione news-prezzo
            if abs(news_sentiment) > 0.1:  # Solo news significative
                price_reaction = change_pct
                self.symbol_behaviors[symbol]['news_correlation'].append({
                    'news_sentiment': news_sentiment,
                    'price_reaction': price_reaction,
                    'timestamp': timestamp
                })
        
        self.total_observations += 1
        
        # Mantieni solo ultimi 10000 dati per simbolo
        for symbol_data in self.symbol_behaviors.values():
            for key in symbol_data:
                if isinstance(symbol_data[key], list) and len(symbol_data[key]) > 10000:
                    symbol_data[key] = symbol_data[key][-10000:]
    
    def learn_from_trade_result(self, trade_decision, actual_outcome):
        """Impara dai risultati dei trade per migliorare predizioni"""
        strategy_signature = {
            'symbol': trade_decision['symbol'],
            'action': trade_decision['action'],
            'score': trade_decision['score'],
            'price_change': trade_decision['price_change'],
            'news_sentiment': trade_decision['news_sentiment'],
            'market_time': datetime.now().hour
        }
        
        if actual_outcome > 0:  # Profitto
            self.successful_strategies.append({
                'strategy': strategy_signature,
                'profit': actual_outcome,
                'timestamp': datetime.now()
            })
            self.accuracy_metrics['profit_predictions'] += 1
        else:  # Perdita
            self.failed_strategies.append({
                'strategy': strategy_signature,
                'loss': actual_outcome,
                'timestamp': datetime.now()
            })
            self.accuracy_metrics['loss_predictions'] += 1
        
        self.accuracy_metrics['total_predictions'] += 1
        self.accuracy_metrics['prediction_accuracy'] = (
            self.accuracy_metrics['profit_predictions'] / 
            self.accuracy_metrics['total_predictions']
        )
    
    def get_learned_insights(self, symbol):
        """Restituisce insights appresi per un simbolo"""
        if symbol not in self.symbol_behaviors:
            return None
        
        data = self.symbol_behaviors[symbol]
        
        insights = {
            'avg_volatility': np.mean([obs['volatility'] for obs in data['price_history'][-100:]]) if data['price_history'] else 0,
            'news_sensitivity': self._calculate_news_sensitivity(symbol),
            'best_trading_hours': self._find_best_trading_hours(symbol),
            'risk_level': self._assess_risk_level(symbol),
            'confidence_score': min(len(data['price_history']) / 1000, 1.0)  # Confidence basata su dati
        }
        
        return insights
    
    def _calculate_news_sensitivity(self, symbol):
        """Calcola quanto il simbolo reagisce alle news"""
        if symbol not in self.symbol_behaviors:
            return 0.0
        
        correlations = self.symbol_behaviors[symbol]['news_correlation']
        if len(correlations) < 10:
            return 0.0
        
        # Calcola correlazione media
        news_scores = [c['news_sentiment'] for c in correlations[-50:]]
        price_reactions = [c['price_reaction'] for c in correlations[-50:]]
        
        if len(news_scores) > 0:
            correlation = np.corrcoef(news_scores, price_reactions)[0, 1]
            return abs(correlation) if not np.isnan(correlation) else 0.0
        
        return 0.0
    
    def _find_best_trading_hours(self, symbol):
        """Trova gli orari migliori per trading del simbolo"""
        if symbol not in self.symbol_behaviors:
            return []
        
        hourly_performance = {}
        for trade in self.successful_strategies[-100:]:  # Ultimi 100 trade di successo
            if trade['strategy']['symbol'] == symbol:
                hour = trade['timestamp'].hour
                hourly_performance[hour] = hourly_performance.get(hour, 0) + 1
        
        # Restituisce top 3 ore
        sorted_hours = sorted(hourly_performance.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:3]]
    
    def _assess_risk_level(self, symbol):
        """Valuta livello di rischio del simbolo"""
        if symbol not in self.symbol_behaviors:
            return 0.5
        
        recent_data = self.symbol_behaviors[symbol]['price_history'][-100:]
        if len(recent_data) < 10:
            return 0.5
        
        volatilities = [d['volatility'] for d in recent_data]
        avg_volatility = np.mean(volatilities)
        
        # Normalizza volatilità su scala 0-1
        risk_score = min(avg_volatility * 100, 1.0)  # Assumi max volatilità del 1%
        return risk_score
    
    def save_knowledge_base(self, filename=None):
        """Salva knowledge base su file"""
        if filename is None:
            filename = f"ai_knowledge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        filepath = log_dir / filename
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'market_patterns': self.market_patterns,
                    'symbol_behaviors': self.symbol_behaviors,
                    'successful_strategies': self.successful_strategies,
                    'failed_strategies': self.failed_strategies,
                    'market_correlations': self.market_correlations,
                    'news_impact_analysis': self.news_impact_analysis,
                    'volatility_patterns': self.volatility_patterns,
                    'training_start_time': self.training_start_time,
                    'total_observations': self.total_observations,
                    'accuracy_metrics': self.accuracy_metrics,
                    'save_timestamp': datetime.now()
                }, f)
            
            logger.info(f"💾 Knowledge base salvata: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"❌ Errore salvataggio knowledge base: {e}")
            return None
    
    def load_knowledge_base(self, filepath):
        """Carica knowledge base da file"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.market_patterns = data.get('market_patterns', {})
            self.symbol_behaviors = data.get('symbol_behaviors', {})
            self.successful_strategies = data.get('successful_strategies', [])
            self.failed_strategies = data.get('failed_strategies', [])
            self.market_correlations = data.get('market_correlations', {})
            self.news_impact_analysis = data.get('news_impact_analysis', {})
            self.volatility_patterns = data.get('volatility_patterns', {})
            self.training_start_time = data.get('training_start_time', datetime.now())
            self.total_observations = data.get('total_observations', 0)
            self.accuracy_metrics = data.get('accuracy_metrics', {
                'prediction_accuracy': 0.0,
                'profit_predictions': 0,
                'loss_predictions': 0,
                'total_predictions': 0
            })
            
            logger.info(f"📖 Knowledge base caricata: {filepath}")
            logger.info(f"📊 Osservazioni totali: {self.total_observations}")
            logger.info(f"🎯 Accuratezza predizioni: {self.accuracy_metrics['prediction_accuracy']:.2%}")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Errore caricamento knowledge base: {e}")
            return False

class AIBackgroundTrainer:
    """Sistema di training AI in background"""
    
    def __init__(self, symbols=None):
        self.symbols = symbols or ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA']
        self.knowledge_base = AIKnowledgeBase()
        self.is_training = False
        self.shutdown_event = asyncio.Event()
        
        # Inizializza componenti
        self._setup_data_collector()
        self._setup_news_collector()
        
        logger.info(f"🧠 AI Background Trainer inizializzato")
        logger.info(f"📊 Simboli monitorati: {', '.join(self.symbols)}")
    
    def _setup_data_collector(self):
        """Setup data collector"""
        try:
            from realtime_data import RealTimeDataCollector
            self.data_collector = RealTimeDataCollector()
            logger.info("✅ Real-time data collector caricato")
        except Exception as e:
            logger.error(f"❌ Errore setup data collector: {e}")
            self.data_collector = None
    
    def _setup_news_collector(self):
        """Setup news collector"""
        try:
            from simple_dual_ai import SimpleNewsCollector
            self.news_collector = SimpleNewsCollector()
            logger.info("✅ News collector caricato")
        except Exception as e:
            logger.error(f"❌ Errore setup news collector: {e}")
            self.news_collector = None
    
    async def start_training(self, duration_days=10):
        """Inizia training per N giorni"""
        logger.info(f"🚀 === AVVIO AI BACKGROUND TRAINING ===")
        logger.info(f"⏰ Durata training: {duration_days} giorni")
        logger.info(f"🔄 Intervallo osservazioni: 30 secondi")
        
        self.is_training = True
        end_time = datetime.now() + timedelta(days=duration_days)
        
        # Signal handler per CTRL+C
        def signal_handler(signum, frame):
            logger.info("🛑 Ricevuto segnale interruzione training")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        observations_count = 0
        last_save = datetime.now()
        
        try:
            while datetime.now() < end_time and not self.shutdown_event.is_set():
                await self._training_cycle()
                observations_count += 1
                
                # Log progress ogni 100 osservazioni
                if observations_count % 100 == 0:
                    elapsed = datetime.now() - self.knowledge_base.training_start_time
                    logger.info(f"📈 Training progress: {observations_count} osservazioni in {elapsed}")
                    logger.info(f"🎯 Accuratezza attuale: {self.knowledge_base.accuracy_metrics['prediction_accuracy']:.2%}")
                
                # Auto-save ogni ora
                if datetime.now() - last_save > timedelta(hours=1):
                    self.knowledge_base.save_knowledge_base("ai_knowledge_autosave.pkl")
                    last_save = datetime.now()
                
                # Aspetta prima del prossimo ciclo
                try:
                    await asyncio.wait_for(self.shutdown_event.wait(), timeout=30.0)
                    break  # Shutdown richiesto
                except asyncio.TimeoutError:
                    pass  # Continua training
        
        except Exception as e:
            logger.error(f"❌ Errore durante training: {e}")
        
        finally:
            # Salva knowledge base finale
            final_save_path = self.knowledge_base.save_knowledge_base()
            
            # Report finale
            elapsed = datetime.now() - self.knowledge_base.training_start_time
            logger.info(f"🏁 === TRAINING COMPLETATO ===")
            logger.info(f"⏰ Durata totale: {elapsed}")
            logger.info(f"📊 Osservazioni totali: {self.knowledge_base.total_observations}")
            logger.info(f"🎯 Accuratezza finale: {self.knowledge_base.accuracy_metrics['prediction_accuracy']:.2%}")
            logger.info(f"💾 Knowledge base salvata: {final_save_path}")
            
            self.is_training = False
    
    async def _training_cycle(self):
        """Singolo ciclo di training"""
        try:
            # Raccoglie dati di mercato
            if self.data_collector:
                current_prices = self.data_collector.get_all_current_prices()
                price_changes = self.data_collector.get_all_price_changes()
            else:
                return
            
            # Raccoglie sentiment news
            news_sentiment = 0.0
            if self.news_collector:
                try:
                    articles = self.news_collector.collect_news()
                    if articles:
                        news_sentiment = self.news_collector.analyze_sentiment(articles)
                except Exception as e:
                    logger.debug(f"Errore news collection: {e}")
            
            # Aggiunge osservazioni alla knowledge base
            for symbol in self.symbols:
                if symbol in current_prices:
                    # Ottieni storia prezzi dal collector
                    price_history = []
                    if hasattr(self.data_collector, 'price_history') and symbol in self.data_collector.price_history:
                        recent_prices = self.data_collector.price_history[symbol][-50:]  # Ultimi 50
                        price_history = [p['price'] for p in recent_prices]
                    
                    if len(price_history) >= 2:
                        self.knowledge_base.add_market_observation(
                            symbol=symbol,
                            price_data=price_history,
                            news_sentiment=news_sentiment,
                            market_context={
                                'timestamp': datetime.now(),
                                'market_hour': datetime.now().hour,
                                'weekday': datetime.now().weekday()
                            }
                        )
        
        except Exception as e:
            logger.error(f"❌ Errore training cycle: {e}")

def main():
    """Funzione principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Background Training System')
    parser.add_argument('--days', type=int, default=10, help='Giorni di training (default: 10)')
    parser.add_argument('--load', type=str, help='Carica knowledge base esistente')
    parser.add_argument('--symbols', nargs='+', help='Simboli da monitorare')
    
    args = parser.parse_args()
    
    # Crea trainer
    trainer = AIBackgroundTrainer(symbols=args.symbols)
    
    # Carica knowledge base se specificata
    if args.load:
        trainer.knowledge_base.load_knowledge_base(args.load)
    
    # Avvia training
    try:
        asyncio.run(trainer.start_training(duration_days=args.days))
    except KeyboardInterrupt:
        logger.info("🛑 Training interrotto dall'utente")
    except Exception as e:
        logger.error(f"❌ Errore critico: {e}")

if __name__ == "__main__":
    main()
