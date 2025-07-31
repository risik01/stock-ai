#!/usr/bin/env python3
"""
Backtest Engine - Sistema di backtesting per strategie di trading
Simula le performance delle strategie su dati storici
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from data_collector import DataCollector
from portfolio import Portfolio
from strategy_engine import should_buy, should_sell
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class BacktestEngine:
    """Engine per il backtesting di strategie di trading"""
    
    def __init__(self, config):
        self.config = config
        self.data_collector = DataCollector(config)
        self.results_dir = Path("data/backtest_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Parametri backtesting
        self.initial_capital = config['trading']['initial_capital']
        self.commission = config['trading'].get('commission', 0.001)
        self.slippage = config['trading'].get('slippage', 0.0005)
        
        logger.info("🧪 BacktestEngine inizializzato")
    
    def run_backtest(self, start_date: str, end_date: str, symbols: List[str] = None) -> Dict:
        """
        Esegue backtesting completo
        
        Args:
            start_date (str): Data inizio in formato YYYY-MM-DD
            end_date (str): Data fine in formato YYYY-MM-DD
            symbols (List[str]): Lista simboli da testare
            
        Returns:
            Dict: Risultati del backtesting
        """
        logger.info(f"🚀 Avvio backtesting: {start_date} → {end_date}")
        
        if symbols is None:
            symbols = self.config['data']['symbols']
        
        try:
            # Carica dati storici
            historical_data = self._load_historical_data(start_date, end_date, symbols)
            
            if not historical_data:
                raise ValueError("Nessun dato storico disponibile")
            
            # Esegui simulazione
            results = self._simulate_trading(historical_data, start_date, end_date)
            
            # Calcola metriche
            metrics = self._calculate_metrics(results)
            
            # Genera report
            report = self._generate_report(results, metrics, start_date, end_date)
            
            # Salva risultati
            self._save_results(report, start_date, end_date)
            
            logger.info(f"✅ Backtesting completato: {metrics['total_return']:.2f}% return")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Errore backtesting: {e}")
            raise
    
    def _load_historical_data(self, start_date: str, end_date: str, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Carica dati storici per il periodo specificato"""
        logger.info(f"📊 Caricamento dati per {len(symbols)} simboli...")
        
        historical_data = {}
        
        for symbol in symbols:
            try:
                # Converte date in datetime
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                
                # Calcola periodo
                period_days = (end_dt - start_dt).days
                
                if period_days <= 365:
                    period = "1y"
                elif period_days <= 730:
                    period = "2y"
                else:
                    period = "5y"
                
                # Ottieni dati
                data = self.data_collector.get_stock_data(symbol, period)
                
                if data is not None and not data.empty:
                    # Filtra per periodo richiesto
                    data = data[start_date:end_date]
                    
                    if not data.empty:
                        historical_data[symbol] = data
                        logger.debug(f"✅ {symbol}: {len(data)} giorni")
                    else:
                        logger.warning(f"⚠️ {symbol}: Nessun dato nel periodo")
                else:
                    logger.warning(f"⚠️ {symbol}: Impossibile ottenere dati")
                    
            except Exception as e:
                logger.error(f"❌ Errore caricamento {symbol}: {e}")
        
        logger.info(f"📈 Dati caricati per {len(historical_data)}/{len(symbols)} simboli")
        return historical_data
    
    def _simulate_trading(self, historical_data: Dict[str, pd.DataFrame], start_date: str, end_date: str) -> Dict:
        """Simula il trading sui dati storici"""
        logger.info("🎮 Avvio simulazione trading...")
        
        # Inizializza portfolio
        portfolio = Portfolio(self.initial_capital)
        
        # Prepara dati allineati per date
        all_dates = set()
        for data in historical_data.values():
            all_dates.update(data.index.strftime('%Y-%m-%d'))
        
        trading_dates = sorted(list(all_dates))
        
        # Statistiche simulazione
        daily_values = []
        daily_positions = []
        all_signals = []
        
        logger.info(f"📅 Simulazione su {len(trading_dates)} giorni di trading")
        
        for i, date in enumerate(trading_dates):
            try:
                # Prezzi del giorno
                daily_prices = {}
                for symbol, data in historical_data.items():
                    if date in data.index.strftime('%Y-%m-%d'):
                        daily_prices[symbol] = data.loc[data.index.strftime('%Y-%m-%d') == date].iloc[0]
                
                if not daily_prices:
                    continue
                
                # Valutazione posizioni esistenti
                current_prices = {symbol: prices['Close'] for symbol, prices in daily_prices.items()}
                portfolio_value = portfolio.get_portfolio_value(current_prices)
                
                # Genera segnali di trading per ogni simbolo
                for symbol, prices in daily_prices.items():
                    try:
                        # Ottieni dati storici fino a questa data per analisi tecnica
                        hist_data = historical_data[symbol].loc[:date]
                        
                        if len(hist_data) < 20:  # Dati insufficienti per analisi
                            continue
                        
                        current_price = prices['Close']
                        
                        # Controlla se vendere posizioni esistenti
                        if symbol in portfolio.positions:
                            position = portfolio.positions[symbol]
                            entry_price = position['avg_price']
                            
                            # Stop loss / Take profit semplificati
                            pnl_pct = (current_price - entry_price) / entry_price
                            
                            should_sell_flag = (
                                pnl_pct <= -0.05 or  # Stop loss 5%
                                pnl_pct >= 0.15 or   # Take profit 15%
                                should_sell(hist_data, current_price)  # Segnale tecnico
                            )
                            
                            if should_sell_flag:
                                shares = position['shares']
                                total_value = shares * current_price
                                commission = total_value * self.commission
                                slippage = total_value * self.slippage
                                
                                if portfolio.sell(symbol, current_price, shares):
                                    # Applica costi
                                    portfolio.cash -= (commission + slippage)
                                    
                                    all_signals.append({
                                        'date': date,
                                        'symbol': symbol,
                                        'action': 'SELL',
                                        'price': current_price,
                                        'shares': shares,
                                        'value': total_value,
                                        'pnl_pct': pnl_pct * 100
                                    })
                        
                        # Controlla se comprare
                        elif len(portfolio.positions) < 10:  # Max 10 posizioni
                            if should_buy(hist_data, current_price):
                                # Calcola size posizione (es. 10% del portfolio)
                                position_value = portfolio_value * 0.1
                                shares = int(position_value / current_price)
                                
                                if shares > 0 and portfolio.cash > position_value:
                                    total_cost = shares * current_price
                                    commission = total_cost * self.commission
                                    slippage = total_cost * self.slippage
                                    
                                    if portfolio.buy(symbol, current_price, shares):
                                        # Applica costi
                                        portfolio.cash -= (commission + slippage)
                                        
                                        all_signals.append({
                                            'date': date,
                                            'symbol': symbol,
                                            'action': 'BUY',
                                            'price': current_price,
                                            'shares': shares,
                                            'value': total_cost,
                                            'pnl_pct': 0
                                        })
                    
                    except Exception as e:
                        logger.debug(f"Errore elaborazione {symbol} il {date}: {e}")
                        continue
                
                # Salva stato giornaliero
                portfolio_value = portfolio.get_portfolio_value(current_prices)
                daily_values.append({
                    'date': date,
                    'portfolio_value': portfolio_value,
                    'cash': portfolio.cash,
                    'positions_count': len(portfolio.positions),
                    'total_trades': len(portfolio.transactions)
                })
                
                daily_positions.append({
                    'date': date,
                    'positions': dict(portfolio.positions)
                })
                
                # Progress ogni 30 giorni
                if i % 30 == 0:
                    progress = (i / len(trading_dates)) * 100
                    logger.debug(f"📊 Progresso: {progress:.1f}% - Valore: ${portfolio_value:,.2f}")
            
            except Exception as e:
                logger.warning(f"⚠️ Errore simulazione giorno {date}: {e}")
                continue
        
        results = {
            'portfolio': portfolio,
            'daily_values': daily_values,
            'daily_positions': daily_positions,
            'signals': all_signals,
            'initial_capital': self.initial_capital,
            'final_value': daily_values[-1]['portfolio_value'] if daily_values else self.initial_capital
        }
        
        logger.info(f"🎯 Simulazione completata: {len(all_signals)} operazioni")
        return results
    
    def _calculate_metrics(self, results: Dict) -> Dict:
        """Calcola metriche di performance"""
        daily_values = results['daily_values']
        signals = results['signals']
        
        if not daily_values:
            return {}
        
        # Converti in DataFrame per analisi
        df = pd.DataFrame(daily_values)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Calcola rendimenti giornalieri
        df['daily_return'] = df['portfolio_value'].pct_change()
        
        # Metriche base
        initial_value = results['initial_capital']
        final_value = results['final_value']
        total_return = ((final_value - initial_value) / initial_value) * 100
        
        # Volatilità annualizzata
        volatility = df['daily_return'].std() * np.sqrt(252) * 100
        
        # Sharpe Ratio (assumendo risk-free rate = 2%)
        risk_free_rate = 0.02
        excess_return = (total_return / 100) - risk_free_rate
        sharpe_ratio = excess_return / (volatility / 100) if volatility > 0 else 0
        
        # Max Drawdown
        rolling_max = df['portfolio_value'].cummax()
        drawdown = (df['portfolio_value'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # Win Rate
        buy_signals = [s for s in signals if s['action'] == 'BUY']
        sell_signals = [s for s in signals if s['action'] == 'SELL']
        
        winning_trades = len([s for s in sell_signals if s['pnl_pct'] > 0])
        total_trades = len(sell_signals)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Profit Factor
        winning_pnl = sum([s['pnl_pct'] for s in sell_signals if s['pnl_pct'] > 0])
        losing_pnl = abs(sum([s['pnl_pct'] for s in sell_signals if s['pnl_pct'] < 0]))
        profit_factor = winning_pnl / losing_pnl if losing_pnl > 0 else float('inf')
        
        # Metriche avanzate
        days_traded = len(df)
        annual_return = ((final_value / initial_value) ** (252 / days_traded) - 1) * 100 if days_traded > 0 else 0
        
        metrics = {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(buy_signals),
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'days_traded': days_traded,
            'final_value': final_value,
            'initial_value': initial_value
        }
        
        return metrics
    
    def _generate_report(self, results: Dict, metrics: Dict, start_date: str, end_date: str) -> Dict:
        """Genera report completo del backtesting"""
        
        report = {
            'summary': {
                'start_date': start_date,
                'end_date': end_date,
                'duration_days': (datetime.strptime(end_date, '%Y-%m-%d') - 
                                datetime.strptime(start_date, '%Y-%m-%d')).days,
                'symbols_tested': len(set([s['symbol'] for s in results['signals']])),
                'timestamp': datetime.now().isoformat()
            },
            'performance': metrics,
            'trades': results['signals'],
            'daily_performance': results['daily_values'],
            'configuration': {
                'initial_capital': self.initial_capital,
                'commission': self.commission,
                'slippage': self.slippage,
                'max_positions': 10,
                'strategy': 'Technical Analysis + Risk Management'
            }
        }
        
        return report
    
    def _save_results(self, report: Dict, start_date: str, end_date: str):
        """Salva risultati del backtesting"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backtest_{start_date}_{end_date}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"💾 Risultati salvati: {filepath}")
            
            # Salva anche summary CSV per facile lettura
            summary_file = self.results_dir / f"summary_{timestamp}.csv"
            
            summary_data = {
                'Metrica': list(report['performance'].keys()),
                'Valore': list(report['performance'].values())
            }
            
            pd.DataFrame(summary_data).to_csv(summary_file, index=False)
            
        except Exception as e:
            logger.error(f"❌ Errore salvataggio risultati: {e}")
    
    def create_charts(self, report: Dict) -> Dict[str, str]:
        """Crea grafici per i risultati del backtesting"""
        charts = {}
        
        try:
            # Performance Chart
            daily_perf = pd.DataFrame(report['daily_performance'])
            daily_perf['date'] = pd.to_datetime(daily_perf['date'])
            
            plt.figure(figsize=(12, 8))
            
            # Subplot 1: Portfolio Value
            plt.subplot(2, 2, 1)
            plt.plot(daily_perf['date'], daily_perf['portfolio_value'])
            plt.title('Portfolio Value Over Time')
            plt.ylabel('Value ($)')
            plt.xticks(rotation=45)
            
            # Subplot 2: Drawdown
            rolling_max = daily_perf['portfolio_value'].cummax()
            drawdown = (daily_perf['portfolio_value'] - rolling_max) / rolling_max * 100
            
            plt.subplot(2, 2, 2)
            plt.fill_between(daily_perf['date'], drawdown, 0, alpha=0.3, color='red')
            plt.plot(daily_perf['date'], drawdown, color='red')
            plt.title('Drawdown')
            plt.ylabel('Drawdown (%)')
            plt.xticks(rotation=45)
            
            # Subplot 3: Monthly Returns
            daily_perf.set_index('date', inplace=True)
            monthly_returns = daily_perf['portfolio_value'].resample('M').last().pct_change() * 100
            
            plt.subplot(2, 2, 3)
            colors = ['green' if x > 0 else 'red' for x in monthly_returns]
            plt.bar(range(len(monthly_returns)), monthly_returns, color=colors, alpha=0.7)
            plt.title('Monthly Returns')
            plt.ylabel('Return (%)')
            
            # Subplot 4: Trade Distribution
            trades = report['trades']
            sell_trades = [t for t in trades if t['action'] == 'SELL']
            
            if sell_trades:
                pnl_values = [t['pnl_pct'] for t in sell_trades]
                
                plt.subplot(2, 2, 4)
                plt.hist(pnl_values, bins=20, alpha=0.7, edgecolor='black')
                plt.title('Trade P&L Distribution')
                plt.xlabel('P&L (%)')
                plt.ylabel('Number of Trades')
            
            plt.tight_layout()
            
            # Salva grafico
            chart_file = self.results_dir / f"charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            charts['performance'] = str(chart_file)
            
            logger.info(f"📊 Grafici salvati: {chart_file}")
            
        except Exception as e:
            logger.error(f"❌ Errore creazione grafici: {e}")
        
        return charts
    
    def compare_strategies(self, results_list: List[Dict]) -> Dict:
        """Confronta multiple strategie"""
        if not results_list:
            return {}
        
        comparison = {
            'strategies': [],
            'metrics_comparison': {},
            'best_strategy': None
        }
        
        for i, result in enumerate(results_list):
            strategy_name = f"Strategy_{i+1}"
            comparison['strategies'].append({
                'name': strategy_name,
                'total_return': result['performance']['total_return'],
                'sharpe_ratio': result['performance']['sharpe_ratio'],
                'max_drawdown': result['performance']['max_drawdown'],
                'win_rate': result['performance']['win_rate']
            })
        
        # Trova strategia migliore (basato su Sharpe Ratio)
        best_strategy = max(comparison['strategies'], key=lambda x: x['sharpe_ratio'])
        comparison['best_strategy'] = best_strategy['name']
        
        return comparison

if __name__ == "__main__":
    # Test del modulo
    logging.basicConfig(level=logging.INFO)
    
    # Configurazione di test
    test_config = {
        'trading': {
            'initial_capital': 10000,
            'commission': 0.001,
            'slippage': 0.0005
        },
        'data': {
            'symbols': ['AAPL', 'GOOGL'],
            'lookback_days': 365,
            'cache_enabled': True
        }
    }
    
    # Test backtesting
    engine = BacktestEngine(test_config)
    
    print("🧪 Test BacktestEngine...")
    
    # Test su periodo breve
    start_date = "2023-01-01"
    end_date = "2023-06-30"
    
    try:
        results = engine.run_backtest(start_date, end_date, ['AAPL'])
        
        print(f"✅ Backtesting completato:")
        print(f"   Rendimento: {results['performance']['total_return']:.2f}%")
        print(f"   Sharpe Ratio: {results['performance']['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {results['performance']['max_drawdown']:.2f}%")
        print(f"   Win Rate: {results['performance']['win_rate']:.1f}%")
        print(f"   Trades: {results['performance']['total_trades']}")
        
    except Exception as e:
        print(f"❌ Errore test: {e}")
    
    print("🎉 Test completato!")
