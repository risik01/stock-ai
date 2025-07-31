#!/usr/bin/env python3
"""
Performance Analytics - Sistema avanzato per analisi performance e risk management
Include metriche finanziarie professionali e gestione del rischio
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import warnings
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class PerformanceAnalytics:
    """Sistema completo per analisi performance e risk management"""
    
    def __init__(self, config):
        self.config = config
        self.reports_dir = Path("data/performance_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Parametri risk management
        self.risk_free_rate = config.get('risk', {}).get('risk_free_rate', 0.02)
        self.var_confidence = config.get('risk', {}).get('var_confidence', 0.05)
        self.benchmark = config.get('risk', {}).get('benchmark', 'SPY')
        
        logger.info("📊 PerformanceAnalytics inizializzato")
    
    def calculate_comprehensive_metrics(self, portfolio_data: pd.DataFrame, benchmark_data: pd.DataFrame = None) -> Dict:
        """
        Calcola metriche complete di performance
        
        Args:
            portfolio_data: DataFrame con colonne ['date', 'portfolio_value']
            benchmark_data: DataFrame opzionale per benchmark comparison
            
        Returns:
            Dict: Metriche complete di performance
        """
        logger.info("🔍 Calcolo metriche comprehensive...")
        
        if portfolio_data.empty:
            return {}
        
        # Prepara dati
        df = portfolio_data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        
        # Calcola rendimenti
        df['returns'] = df['portfolio_value'].pct_change().fillna(0)
        df['cumulative_returns'] = (1 + df['returns']).cumprod() - 1
        
        # Metriche base
        metrics = self._calculate_basic_metrics(df)
        
        # Metriche di rischio
        risk_metrics = self._calculate_risk_metrics(df)
        metrics.update(risk_metrics)
        
        # Metriche di drawdown
        drawdown_metrics = self._calculate_drawdown_metrics(df)
        metrics.update(drawdown_metrics)
        
        # Analisi rolling
        rolling_metrics = self._calculate_rolling_metrics(df)
        metrics.update(rolling_metrics)
        
        # Benchmark comparison se disponibile
        if benchmark_data is not None and not benchmark_data.empty:
            benchmark_metrics = self._calculate_benchmark_metrics(df, benchmark_data)
            metrics.update(benchmark_metrics)
        
        # Analisi distribuzione rendimenti
        distribution_metrics = self._calculate_distribution_metrics(df)
        metrics.update(distribution_metrics)
        
        # Risk-adjusted metrics
        risk_adjusted_metrics = self._calculate_risk_adjusted_metrics(df)
        metrics.update(risk_adjusted_metrics)
        
        logger.info(f"✅ Metriche calcolate: {len(metrics)} parametri")
        return metrics
    
    def _calculate_basic_metrics(self, df: pd.DataFrame) -> Dict:
        """Calcola metriche base di performance"""
        
        total_return = df['cumulative_returns'].iloc[-1] * 100
        
        # Rendimento annualizzato
        days = len(df)
        years = days / 252  # Trading days per anno
        annual_return = ((1 + df['cumulative_returns'].iloc[-1]) ** (1/years) - 1) * 100 if years > 0 else 0
        
        # Volatilità
        volatility = df['returns'].std() * np.sqrt(252) * 100
        
        # Win rate
        winning_days = (df['returns'] > 0).sum()
        win_rate = (winning_days / len(df)) * 100
        
        # Average win/loss
        winning_returns = df['returns'][df['returns'] > 0]
        losing_returns = df['returns'][df['returns'] < 0]
        
        avg_win = winning_returns.mean() * 100 if len(winning_returns) > 0 else 0
        avg_loss = losing_returns.mean() * 100 if len(losing_returns) > 0 else 0
        
        # Profit factor
        total_wins = winning_returns.sum()
        total_losses = abs(losing_returns.sum())
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_trades': len(df),
            'winning_trades': winning_days,
            'losing_trades': len(df) - winning_days
        }
    
    def _calculate_risk_metrics(self, df: pd.DataFrame) -> Dict:
        """Calcola metriche di rischio"""
        
        returns = df['returns']
        
        # Value at Risk (VaR)
        var_95 = np.percentile(returns, 5) * 100
        var_99 = np.percentile(returns, 1) * 100
        
        # Conditional VaR (Expected Shortfall)
        cvar_95 = returns[returns <= np.percentile(returns, 5)].mean() * 100
        cvar_99 = returns[returns <= np.percentile(returns, 1)].mean() * 100
        
        # Sharpe Ratio
        excess_returns = returns - (self.risk_free_rate / 252)
        sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252)
        sortino_ratio = (returns.mean() * 252 - self.risk_free_rate) / downside_volatility if downside_volatility > 0 else 0
        
        # Calmar Ratio (sarà calcolato dopo max drawdown)
        
        # Skewness e Kurtosis
        skewness = stats.skew(returns)
        kurtosis = stats.kurtosis(returns)
        
        return {
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'skewness': skewness,
            'kurtosis': kurtosis
        }
    
    def _calculate_drawdown_metrics(self, df: pd.DataFrame) -> Dict:
        """Calcola metriche di drawdown"""
        
        # Calcola drawdown
        running_max = df['portfolio_value'].cummax()
        drawdown = (df['portfolio_value'] - running_max) / running_max
        
        # Max Drawdown
        max_drawdown = drawdown.min() * 100
        
        # Drawdown duration
        drawdown_series = drawdown < 0
        
        if drawdown_series.any():
            # Trova periodi di drawdown
            drawdown_periods = []
            in_drawdown = False
            start_idx = None
            
            for i, is_dd in enumerate(drawdown_series):
                if is_dd and not in_drawdown:
                    in_drawdown = True
                    start_idx = i
                elif not is_dd and in_drawdown:
                    in_drawdown = False
                    drawdown_periods.append(i - start_idx)
            
            if in_drawdown:  # Ancora in drawdown
                drawdown_periods.append(len(drawdown_series) - start_idx)
            
            avg_drawdown_duration = np.mean(drawdown_periods) if drawdown_periods else 0
            max_drawdown_duration = max(drawdown_periods) if drawdown_periods else 0
        else:
            avg_drawdown_duration = 0
            max_drawdown_duration = 0
        
        # Calmar Ratio
        annual_return = df['returns'].mean() * 252 * 100
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Sterling Ratio
        sterling_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'max_drawdown': max_drawdown,
            'avg_drawdown_duration': avg_drawdown_duration,
            'max_drawdown_duration': max_drawdown_duration,
            'calmar_ratio': calmar_ratio,
            'sterling_ratio': sterling_ratio
        }
    
    def _calculate_rolling_metrics(self, df: pd.DataFrame, window: int = 30) -> Dict:
        """Calcola metriche rolling"""
        
        returns = df['returns']
        
        # Rolling Sharpe
        rolling_sharpe = returns.rolling(window).apply(
            lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
        )
        
        # Rolling volatility
        rolling_vol = returns.rolling(window).std() * np.sqrt(252) * 100
        
        # Stability metrics
        sharpe_stability = rolling_sharpe.std()
        vol_stability = rolling_vol.std()
        
        return {
            'rolling_sharpe_mean': rolling_sharpe.mean(),
            'rolling_sharpe_std': sharpe_stability,
            'rolling_volatility_mean': rolling_vol.mean(),
            'rolling_volatility_std': vol_stability,
            'performance_consistency': 1 / (1 + sharpe_stability) if sharpe_stability > 0 else 1
        }
    
    def _calculate_benchmark_metrics(self, df: pd.DataFrame, benchmark_data: pd.DataFrame) -> Dict:
        """Calcola metriche vs benchmark"""
        
        # Allinea dati
        benchmark_df = benchmark_data.copy()
        benchmark_df['date'] = pd.to_datetime(benchmark_df['date'])
        benchmark_df.set_index('date', inplace=True)
        benchmark_df['benchmark_returns'] = benchmark_df['value'].pct_change().fillna(0)
        
        # Merge dei dati
        merged = df.join(benchmark_df['benchmark_returns'], how='inner')
        
        if merged.empty:
            return {}
        
        portfolio_returns = merged['returns']
        benchmark_returns = merged['benchmark_returns']
        
        # Beta
        covariance = np.cov(portfolio_returns, benchmark_returns)[0][1]
        benchmark_variance = np.var(benchmark_returns)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
        
        # Alpha
        portfolio_annual_return = portfolio_returns.mean() * 252
        benchmark_annual_return = benchmark_returns.mean() * 252
        alpha = portfolio_annual_return - (self.risk_free_rate + beta * (benchmark_annual_return - self.risk_free_rate))
        
        # Information Ratio
        active_returns = portfolio_returns - benchmark_returns
        tracking_error = active_returns.std() * np.sqrt(252)
        information_ratio = active_returns.mean() * 252 / tracking_error if tracking_error > 0 else 0
        
        # Correlation
        correlation = np.corrcoef(portfolio_returns, benchmark_returns)[0][1]
        
        # Treynor Ratio
        treynor_ratio = (portfolio_annual_return - self.risk_free_rate) / beta if beta > 0 else 0
        
        return {
            'alpha': alpha * 100,
            'beta': beta,
            'correlation_vs_benchmark': correlation,
            'information_ratio': information_ratio,
            'tracking_error': tracking_error * 100,
            'treynor_ratio': treynor_ratio * 100
        }
    
    def _calculate_distribution_metrics(self, df: pd.DataFrame) -> Dict:
        """Calcola metriche distribuzione rendimenti"""
        
        returns = df['returns']
        
        # Test normalità
        _, normality_p_value = stats.normaltest(returns)
        is_normal = normality_p_value > 0.05
        
        # Percentili
        percentiles = {
            f'percentile_{p}': np.percentile(returns, p) * 100
            for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
        }
        
        # Tail ratio
        tail_ratio = abs(np.percentile(returns, 95)) / abs(np.percentile(returns, 5))
        
        return {
            'is_normal_distribution': is_normal,
            'normality_p_value': normality_p_value,
            'tail_ratio': tail_ratio,
            **percentiles
        }
    
    def _calculate_risk_adjusted_metrics(self, df: pd.DataFrame) -> Dict:
        """Calcola metriche aggiustate per il rischio"""
        
        returns = df['returns']
        
        # Omega Ratio
        threshold = 0  # Target return
        gains = returns[returns > threshold] - threshold
        losses = threshold - returns[returns < threshold]
        omega_ratio = gains.sum() / losses.sum() if losses.sum() > 0 else float('inf')
        
        # Pain Index
        pain_index = abs(df['returns'][df['returns'] < 0].sum()) / len(df) * 100
        
        # Ulcer Index
        running_max = df['portfolio_value'].cummax()
        drawdown = (df['portfolio_value'] - running_max) / running_max
        ulcer_index = np.sqrt((drawdown ** 2).mean()) * 100
        
        # Martin Ratio
        annual_return = returns.mean() * 252 * 100
        martin_ratio = annual_return / ulcer_index if ulcer_index > 0 else 0
        
        return {
            'omega_ratio': omega_ratio,
            'pain_index': pain_index,
            'ulcer_index': ulcer_index,
            'martin_ratio': martin_ratio
        }
    
    def create_performance_dashboard(self, portfolio_data: pd.DataFrame, metrics: Dict, 
                                   benchmark_data: pd.DataFrame = None) -> str:
        """Crea dashboard interattivo con Plotly"""
        
        logger.info("📊 Creazione dashboard performance...")
        
        # Prepara dati
        df = portfolio_data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['returns'] = df['portfolio_value'].pct_change().fillna(0)
        df['cumulative_returns'] = (1 + df['returns']).cumprod() - 1
        
        # Drawdown
        running_max = df['portfolio_value'].cummax()
        df['drawdown'] = (df['portfolio_value'] - running_max) / running_max * 100
        
        # Rolling metrics
        df['rolling_volatility'] = df['returns'].rolling(30).std() * np.sqrt(252) * 100
        df['rolling_sharpe'] = df['returns'].rolling(30).apply(
            lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else 0
        )
        
        # Crea subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Portfolio Value & Cumulative Returns',
                'Drawdown Analysis',
                'Rolling Volatility (30-day)',
                'Rolling Sharpe Ratio (30-day)',
                'Monthly Returns Heatmap',
                'Returns Distribution'
            ),
            specs=[
                [{"secondary_y": True}, {}],
                [{}, {}],
                [{"colspan": 2}, None]
            ]
        )
        
        # Portfolio value
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['portfolio_value'], name='Portfolio Value',
                      line=dict(color='blue', width=2)),
            row=1, col=1
        )
        
        # Cumulative returns (secondary y-axis)
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['cumulative_returns']*100, name='Cumulative Returns (%)',
                      line=dict(color='green', width=2), yaxis='y2'),
            row=1, col=1
        )
        
        # Drawdown
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['drawdown'], name='Drawdown',
                      fill='tonexty', fillcolor='rgba(255,0,0,0.3)',
                      line=dict(color='red')),
            row=1, col=2
        )
        
        # Rolling volatility
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['rolling_volatility'], name='Rolling Volatility',
                      line=dict(color='orange')),
            row=2, col=1
        )
        
        # Rolling Sharpe
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['rolling_sharpe'], name='Rolling Sharpe',
                      line=dict(color='purple')),
            row=2, col=2
        )
        
        # Returns distribution
        fig.add_trace(
            go.Histogram(x=df['returns']*100, name='Returns Distribution',
                        nbinsx=30, opacity=0.7),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f"Performance Dashboard - {metrics.get('total_return', 0):.2f}% Total Return",
            height=900,
            showlegend=True,
            template='plotly_white'
        )
        
        # Salva dashboard
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dashboard_path = self.reports_dir / f"performance_dashboard_{timestamp}.html"
        
        fig.write_html(str(dashboard_path))
        
        logger.info(f"✅ Dashboard salvato: {dashboard_path}")
        return str(dashboard_path)
    
    def generate_risk_report(self, portfolio_data: pd.DataFrame, metrics: Dict) -> Dict:
        """Genera report dettagliato di risk management"""
        
        logger.info("🛡️ Generazione risk report...")
        
        # Analisi stress test
        stress_scenarios = self._perform_stress_tests(portfolio_data)
        
        # Monte Carlo simulation
        monte_carlo_results = self._monte_carlo_simulation(portfolio_data)
        
        # Risk recommendations
        recommendations = self._generate_risk_recommendations(metrics)
        
        risk_report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'risk_level': self._classify_risk_level(metrics),
                'var_95': metrics.get('var_95', 0),
                'max_drawdown': metrics.get('max_drawdown', 0),
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'volatility': metrics.get('volatility', 0)
            },
            'stress_tests': stress_scenarios,
            'monte_carlo': monte_carlo_results,
            'recommendations': recommendations,
            'metrics': metrics
        }
        
        # Salva report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.reports_dir / f"risk_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(risk_report, f, indent=2, default=str)
        
        logger.info(f"📋 Risk report salvato: {report_path}")
        return risk_report
    
    def _perform_stress_tests(self, portfolio_data: pd.DataFrame) -> Dict:
        """Esegue stress test su scenari avversi"""
        
        df = portfolio_data.copy()
        df['returns'] = df['portfolio_value'].pct_change().fillna(0)
        
        scenarios = {
            'market_crash_2008': -0.20,  # -20% shock
            'flash_crash': -0.10,        # -10% shock
            'covid_crash_2020': -0.35,   # -35% shock
            'mild_correction': -0.05     # -5% shock
        }
        
        stress_results = {}
        
        for scenario, shock in scenarios.items():
            # Applica shock
            stressed_value = df['portfolio_value'].iloc[-1] * (1 + shock)
            impact = (stressed_value - df['portfolio_value'].iloc[-1]) / df['portfolio_value'].iloc[-1] * 100
            
            # Stima tempo di recupero (basato su volatilità storica)
            daily_vol = df['returns'].std()
            recovery_days = abs(shock) / daily_vol if daily_vol > 0 else float('inf')
            
            stress_results[scenario] = {
                'shock_percentage': shock * 100,
                'portfolio_impact': impact,
                'estimated_recovery_days': recovery_days,
                'stressed_portfolio_value': stressed_value
            }
        
        return stress_results
    
    def _monte_carlo_simulation(self, portfolio_data: pd.DataFrame, n_simulations: int = 1000, 
                               n_days: int = 252) -> Dict:
        """Esegue simulazione Monte Carlo per proiezioni future"""
        
        df = portfolio_data.copy()
        df['returns'] = df['portfolio_value'].pct_change().fillna(0)
        
        # Parametri distribuzione
        mean_return = df['returns'].mean()
        std_return = df['returns'].std()
        current_value = df['portfolio_value'].iloc[-1]
        
        # Simulazioni
        simulations = []
        
        for _ in range(n_simulations):
            # Genera rendimenti casuali
            random_returns = np.random.normal(mean_return, std_return, n_days)
            
            # Calcola valore finale
            final_value = current_value * np.prod(1 + random_returns)
            simulations.append(final_value)
        
        simulations = np.array(simulations)
        
        # Analisi risultati
        percentiles = {
            'p5': np.percentile(simulations, 5),
            'p25': np.percentile(simulations, 25),
            'p50': np.percentile(simulations, 50),
            'p75': np.percentile(simulations, 75),
            'p95': np.percentile(simulations, 95)
        }
        
        # Probabilità di perdita
        prob_loss = (simulations < current_value).mean() * 100
        
        return {
            'n_simulations': n_simulations,
            'n_days_projected': n_days,
            'current_value': current_value,
            'mean_projected_value': simulations.mean(),
            'percentiles': percentiles,
            'probability_of_loss': prob_loss,
            'best_case': simulations.max(),
            'worst_case': simulations.min()
        }
    
    def _classify_risk_level(self, metrics: Dict) -> str:
        """Classifica il livello di rischio del portfolio"""
        
        volatility = metrics.get('volatility', 0)
        max_drawdown = abs(metrics.get('max_drawdown', 0))
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        
        # Score di rischio composito
        risk_score = 0
        
        # Penalizzazioni
        if volatility > 30:
            risk_score += 3
        elif volatility > 20:
            risk_score += 2
        elif volatility > 15:
            risk_score += 1
        
        if max_drawdown > 30:
            risk_score += 3
        elif max_drawdown > 20:
            risk_score += 2
        elif max_drawdown > 10:
            risk_score += 1
        
        # Bonus per Sharpe ratio alto
        if sharpe_ratio > 1.5:
            risk_score -= 1
        elif sharpe_ratio > 1.0:
            risk_score -= 0.5
        
        # Classificazione
        if risk_score >= 5:
            return "HIGH"
        elif risk_score >= 3:
            return "MEDIUM"
        elif risk_score >= 1:
            return "MODERATE"
        else:
            return "LOW"
    
    def _generate_risk_recommendations(self, metrics: Dict) -> List[str]:
        """Genera raccomandazioni per risk management"""
        
        recommendations = []
        
        volatility = metrics.get('volatility', 0)
        max_drawdown = abs(metrics.get('max_drawdown', 0))
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        win_rate = metrics.get('win_rate', 0)
        
        # Raccomandazioni basate su volatilità
        if volatility > 25:
            recommendations.append("🔴 Volatilità molto alta: Considera riduzione position sizing")
        elif volatility > 20:
            recommendations.append("🟡 Volatilità elevata: Monitora esposizione al rischio")
        
        # Raccomandazioni drawdown
        if max_drawdown > 25:
            recommendations.append("🔴 Max drawdown critico: Implementa stop loss più stringenti")
        elif max_drawdown > 15:
            recommendations.append("🟡 Drawdown significativo: Rivedi strategia risk management")
        
        # Raccomandazioni Sharpe
        if sharpe_ratio < 0.5:
            recommendations.append("🔴 Sharpe ratio basso: Strategia non efficiente risk-adjusted")
        elif sharpe_ratio < 1.0:
            recommendations.append("🟡 Sharpe ratio migliorabile: Ottimizza risk-return profile")
        
        # Raccomandazioni win rate
        if win_rate < 40:
            recommendations.append("🔴 Win rate basso: Rivedi criteri di entrata/uscita")
        
        # Raccomandazioni generali
        if len(recommendations) == 0:
            recommendations.append("✅ Performance nel range accettabile")
        
        recommendations.append("💡 Mantieni diversificazione appropriate")
        recommendations.append("📊 Monitora correlazioni tra posizioni")
        
        return recommendations

def create_performance_report(portfolio_data: pd.DataFrame, config: Dict, 
                            benchmark_data: pd.DataFrame = None) -> Dict:
    """Funzione principale per creazione report performance completo"""
    
    analyzer = PerformanceAnalytics(config)
    
    # Calcola metriche
    metrics = analyzer.calculate_comprehensive_metrics(portfolio_data, benchmark_data)
    
    # Crea dashboard
    dashboard_path = analyzer.create_performance_dashboard(portfolio_data, metrics, benchmark_data)
    
    # Genera risk report
    risk_report = analyzer.generate_risk_report(portfolio_data, metrics)
    
    return {
        'metrics': metrics,
        'dashboard_path': dashboard_path,
        'risk_report': risk_report,
        'timestamp': datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test del modulo
    logging.basicConfig(level=logging.INFO)
    
    # Dati di test
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    # Simula portfolio con trend positivo e volatilità
    returns = np.random.normal(0.0005, 0.02, len(dates))  # 0.05% return medio, 2% volatilità
    portfolio_values = [10000]
    
    for ret in returns[1:]:
        new_value = portfolio_values[-1] * (1 + ret)
        portfolio_values.append(new_value)
    
    portfolio_data = pd.DataFrame({
        'date': dates,
        'portfolio_value': portfolio_values
    })
    
    # Test configurazione
    test_config = {
        'risk': {
            'risk_free_rate': 0.02,
            'var_confidence': 0.05,
            'benchmark': 'SPY'
        }
    }
    
    print("📊 Test PerformanceAnalytics...")
    
    try:
        # Test analisi completa
        analyzer = PerformanceAnalytics(test_config)
        metrics = analyzer.calculate_comprehensive_metrics(portfolio_data)
        
        print(f"✅ Metriche calcolate:")
        print(f"   Total Return: {metrics.get('total_return', 0):.2f}%")
        print(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"   Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
        print(f"   Volatility: {metrics.get('volatility', 0):.2f}%")
        print(f"   Win Rate: {metrics.get('win_rate', 0):.1f}%")
        
        # Test risk report
        risk_report = analyzer.generate_risk_report(portfolio_data, metrics)
        print(f"   Risk Level: {risk_report['summary']['risk_level']}")
        
    except Exception as e:
        print(f"❌ Errore test: {e}")
    
    print("🎉 Test completato!")
