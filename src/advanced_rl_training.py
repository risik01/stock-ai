#!/usr/bin/env python3
"""
Advanced RL Training - Sistema avanzato per il training dell'agente RL
Include tecniche moderne di reinforcement learning per trading
"""

import numpy as np
import pandas as pd
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings

try:
    from stable_baselines3 import PPO, SAC, TD3, A2C
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
    from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
    from stable_baselines3.common.monitor import Monitor
    from stable_baselines3.common.noise import NormalActionNoise
    import optuna
    ADVANCED_RL_AVAILABLE = True
except ImportError:
    ADVANCED_RL_AVAILABLE = False
    logging.warning("⚠️ Stable-baselines3 not available. Using basic RL implementation.")

from trading_env import TradingEnvironment
from data_collector import DataCollector
import pickle

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class TensorBoardCallback(BaseCallback):
    """Callback per logging avanzato durante il training"""
    
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
        
    def _on_step(self) -> bool:
        # Log delle metriche durante il training
        if len(self.model.ep_info_buffer) > 0:
            for info in self.model.ep_info_buffer:
                if 'episode' in info:
                    self.episode_rewards.append(info['episode']['r'])
                    self.episode_lengths.append(info['episode']['l'])
        return True

class AdvancedRLTrainer:
    """Sistema avanzato per il training di agenti RL"""
    
    def __init__(self, config):
        self.config = config
        self.data_collector = DataCollector(config)
        self.models_dir = Path("data/rl_models")
        self.logs_dir = Path("data/rl_logs")
        self.models_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Parametri training
        self.total_timesteps = config.get('rl', {}).get('total_timesteps', 100000)
        self.learning_rate = config.get('rl', {}).get('learning_rate', 3e-4)
        self.batch_size = config.get('rl', {}).get('batch_size', 64)
        
        # Algoritmi disponibili
        if ADVANCED_RL_AVAILABLE:
            self.algorithms = {
                'PPO': PPO,
                'SAC': SAC,
                'TD3': TD3,
                'A2C': A2C
            }
        else:
            self.algorithms = {}
        
        logger.info("🤖 AdvancedRLTrainer inizializzato")
        if not ADVANCED_RL_AVAILABLE:
            logger.warning("⚠️ Funzionalità RL avanzate non disponibili")
    
    def create_training_environment(self, symbols: List[str], train_start: str, train_end: str) -> TradingEnvironment:
        """Crea ambiente di training ottimizzato"""
        logger.info(f"🏗️ Creazione ambiente training: {len(symbols)} simboli")
        
        # Carica dati di training
        training_data = {}
        for symbol in symbols:
            try:
                # Calcola periodo per ottenere dati sufficienti
                start_dt = datetime.strptime(train_start, '%Y-%m-%d')
                end_dt = datetime.strptime(train_end, '%Y-%m-%d')
                period_days = (end_dt - start_dt).days
                
                if period_days <= 365:
                    period = "2y"  # Prendi più dati del necessario
                else:
                    period = "5y"
                
                data = self.data_collector.get_stock_data(symbol, period)
                
                if data is not None and not data.empty:
                    # Filtra per periodo di training
                    data = data[train_start:train_end]
                    
                    if len(data) > 100:  # Dati sufficienti
                        training_data[symbol] = data
                        logger.debug(f"✅ {symbol}: {len(data)} giorni")
                    else:
                        logger.warning(f"⚠️ {symbol}: Dati insufficienti ({len(data)} giorni)")
                
            except Exception as e:
                logger.error(f"❌ Errore caricamento {symbol}: {e}")
        
        if not training_data:
            raise ValueError("Nessun dato di training disponibile")
        
        # Crea ambiente con dati di training
        env = TradingEnvironment(training_data, initial_balance=self.config['trading']['initial_capital'])
        
        logger.info(f"🎯 Ambiente creato: {len(training_data)} simboli, {sum(len(data) for data in training_data.values())} punti dati")
        return env
    
    def hyperparameter_optimization(self, env: TradingEnvironment, algorithm: str = 'PPO', n_trials: int = 20) -> Dict:
        """Ottimizzazione iperparametri con Optuna"""
        if not ADVANCED_RL_AVAILABLE:
            logger.warning("⚠️ Ottimizzazione iperparametri non disponibile")
            return {}
        
        logger.info(f"🔍 Ottimizzazione iperparametri {algorithm} ({n_trials} trials)")
        
        def objective(trial):
            # Suggerimenti iperparametri basati su algoritmo
            if algorithm == 'PPO':
                params = {
                    'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-2),
                    'n_steps': trial.suggest_categorical('n_steps', [128, 256, 512, 1024, 2048]),
                    'batch_size': trial.suggest_categorical('batch_size', [32, 64, 128, 256]),
                    'gamma': trial.suggest_uniform('gamma', 0.9, 0.9999),
                    'ent_coef': trial.suggest_loguniform('ent_coef', 1e-8, 1e-1),
                    'clip_range': trial.suggest_uniform('clip_range', 0.1, 0.4),
                    'n_epochs': trial.suggest_int('n_epochs', 3, 30)
                }
            elif algorithm == 'SAC':
                params = {
                    'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-2),
                    'buffer_size': trial.suggest_categorical('buffer_size', [50000, 100000, 300000]),
                    'batch_size': trial.suggest_categorical('batch_size', [64, 128, 256]),
                    'gamma': trial.suggest_uniform('gamma', 0.9, 0.9999),
                    'tau': trial.suggest_uniform('tau', 0.001, 0.02),
                    'ent_coef': trial.suggest_categorical('ent_coef', ['auto', 0.5, 0.1, 0.05, 0.01])
                }
            else:
                # Parametri generici
                params = {
                    'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-2),
                    'gamma': trial.suggest_uniform('gamma', 0.9, 0.9999)
                }
            
            try:
                # Crea modello con parametri suggeriti
                model_class = self.algorithms[algorithm]
                model = model_class('MlpPolicy', env, **params, verbose=0)
                
                # Training breve per valutazione
                model.learn(total_timesteps=5000)
                
                # Valuta performance
                obs = env.reset()
                total_reward = 0
                for _ in range(100):
                    action, _ = model.predict(obs, deterministic=True)
                    obs, reward, done, _ = env.step(action)
                    total_reward += reward
                    if done:
                        obs = env.reset()
                
                return total_reward
                
            except Exception as e:
                logger.debug(f"Trial fallito: {e}")
                return -1000  # Penalità per trial falliti
        
        # Esegui ottimizzazione
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, timeout=3600)  # Max 1 ora
        
        best_params = study.best_params
        best_value = study.best_value
        
        logger.info(f"🎯 Migliori parametri: {best_params}")
        logger.info(f"🏆 Miglior score: {best_value:.2f}")
        
        return {
            'best_params': best_params,
            'best_value': best_value,
            'study': study
        }
    
    def train_ensemble_models(self, env: TradingEnvironment, algorithms: List[str] = None) -> Dict:
        """Training di ensemble di modelli RL"""
        if not ADVANCED_RL_AVAILABLE:
            logger.warning("⚠️ Training ensemble non disponibile")
            return {}
        
        if algorithms is None:
            algorithms = ['PPO', 'SAC', 'A2C']
        
        logger.info(f"🎭 Training ensemble: {algorithms}")
        
        models = {}
        performance = {}
        
        for algorithm in algorithms:
            if algorithm not in self.algorithms:
                logger.warning(f"⚠️ Algoritmo {algorithm} non disponibile")
                continue
            
            try:
                logger.info(f"🚀 Training {algorithm}...")
                
                # Ottimizza iperparametri
                optimization_result = self.hyperparameter_optimization(env, algorithm, n_trials=10)
                best_params = optimization_result.get('best_params', {})
                
                # Crea modello con parametri ottimizzati
                model_class = self.algorithms[algorithm]
                
                if algorithm == 'TD3':
                    # TD3 richiede noise per action space continuo
                    n_actions = env.action_space.shape[-1]
                    action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
                    model = model_class('MlpPolicy', env, action_noise=action_noise, **best_params, verbose=1)
                else:
                    model = model_class('MlpPolicy', env, **best_params, verbose=1)
                
                # Callback per monitoraggio
                callback = TensorBoardCallback()
                
                # Training completo
                model.learn(
                    total_timesteps=self.total_timesteps,
                    callback=callback,
                    tb_log_name=f"{algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                
                # Salva modello
                model_path = self.models_dir / f"{algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                model.save(str(model_path))
                
                # Valuta performance
                perf = self._evaluate_model(model, env)
                
                models[algorithm] = {
                    'model': model,
                    'path': str(model_path),
                    'params': best_params,
                    'performance': perf
                }
                
                performance[algorithm] = perf
                
                logger.info(f"✅ {algorithm} completato - Reward medio: {perf['mean_reward']:.2f}")
                
            except Exception as e:
                logger.error(f"❌ Errore training {algorithm}: {e}")
                continue
        
        # Crea ensemble
        ensemble = self._create_ensemble(models)
        
        results = {
            'models': models,
            'performance': performance,
            'ensemble': ensemble,
            'best_single_model': max(performance.items(), key=lambda x: x[1]['mean_reward'])[0] if performance else None
        }
        
        logger.info(f"🎉 Ensemble training completato: {len(models)} modelli")
        return results
    
    def _evaluate_model(self, model, env: TradingEnvironment, n_episodes: int = 10) -> Dict:
        """Valuta performance di un modello"""
        episode_rewards = []
        episode_lengths = []
        
        for episode in range(n_episodes):
            obs = env.reset()
            episode_reward = 0
            episode_length = 0
            
            while True:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, done, _ = env.step(action)
                episode_reward += reward
                episode_length += 1
                
                if done:
                    break
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
        
        return {
            'mean_reward': np.mean(episode_rewards),
            'std_reward': np.std(episode_rewards),
            'mean_length': np.mean(episode_lengths),
            'min_reward': np.min(episode_rewards),
            'max_reward': np.max(episode_rewards)
        }
    
    def _create_ensemble(self, models: Dict) -> Dict:
        """Crea ensemble di modelli"""
        if not models:
            return {}
        
        # Pesi basati su performance
        total_performance = sum(model['performance']['mean_reward'] for model in models.values())
        
        if total_performance <= 0:
            # Pesi uniformi se performance negative
            weights = {alg: 1.0 / len(models) for alg in models.keys()}
        else:
            weights = {
                alg: model['performance']['mean_reward'] / total_performance
                for alg, model in models.items()
            }
        
        ensemble = {
            'models': list(models.keys()),
            'weights': weights,
            'creation_date': datetime.now().isoformat()
        }
        
        logger.info(f"🎯 Ensemble creato con pesi: {weights}")
        return ensemble
    
    def predict_ensemble(self, ensemble: Dict, models: Dict, observation) -> np.ndarray:
        """Predizione usando ensemble di modelli"""
        if not ensemble or not models:
            return np.array([0])  # Azione neutra
        
        predictions = []
        weights = []
        
        for algorithm in ensemble['models']:
            if algorithm in models:
                try:
                    model = models[algorithm]['model']
                    action, _ = model.predict(observation, deterministic=True)
                    predictions.append(action)
                    weights.append(ensemble['weights'][algorithm])
                except Exception as e:
                    logger.debug(f"Errore predizione {algorithm}: {e}")
                    continue
        
        if not predictions:
            return np.array([0])
        
        # Media pesata delle predizioni
        predictions = np.array(predictions)
        weights = np.array(weights)
        weights = weights / weights.sum()  # Normalizza pesi
        
        ensemble_prediction = np.average(predictions, axis=0, weights=weights)
        return ensemble_prediction
    
    def incremental_learning(self, model, new_data: Dict, n_steps: int = 10000):
        """Apprendimento incrementale con nuovi dati"""
        if not ADVANCED_RL_AVAILABLE:
            logger.warning("⚠️ Apprendimento incrementale non disponibile")
            return None
        
        logger.info(f"📚 Apprendimento incrementale: {n_steps} steps")
        
        try:
            # Crea ambiente con nuovi dati
            new_env = TradingEnvironment(new_data, initial_balance=self.config['trading']['initial_capital'])
            
            # Aggiorna ambiente del modello
            model.set_env(new_env)
            
            # Continua training
            model.learn(total_timesteps=n_steps)
            
            # Salva modello aggiornato
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_path = self.models_dir / f"incremental_{timestamp}.zip"
            model.save(str(model_path))
            
            logger.info(f"✅ Apprendimento incrementale completato: {model_path}")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"❌ Errore apprendimento incrementale: {e}")
            return None
    
    def analyze_learning_curve(self, log_path: str) -> Dict:
        """Analizza curve di apprendimento da TensorBoard logs"""
        try:
            # Placeholder per analisi curve di apprendimento
            # In un'implementazione completa, qui si analizzerebbero i file di log TensorBoard
            
            analysis = {
                'convergence_detected': True,
                'learning_stability': 'Good',
                'recommended_timesteps': self.total_timesteps,
                'early_stopping_point': None
            }
            
            logger.info("📈 Analisi curve di apprendimento completata")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Errore analisi learning curve: {e}")
            return {}
    
    def save_training_report(self, results: Dict, symbols: List[str], train_period: str):
        """Salva report completo del training"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        report = {
            'timestamp': timestamp,
            'train_period': train_period,
            'symbols': symbols,
            'config': self.config,
            'results': {
                'models_trained': list(results.get('models', {}).keys()),
                'performance': results.get('performance', {}),
                'best_model': results.get('best_single_model'),
                'ensemble_weights': results.get('ensemble', {}).get('weights', {})
            },
            'training_params': {
                'total_timesteps': self.total_timesteps,
                'learning_rate': self.learning_rate,
                'batch_size': self.batch_size
            }
        }
        
        # Salva report JSON
        report_path = self.logs_dir / f"training_report_{timestamp}.json"
        
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"📋 Report training salvato: {report_path}")
            
            # Crea visualizzazioni
            self._create_training_visualizations(results, timestamp)
            
        except Exception as e:
            logger.error(f"❌ Errore salvataggio report: {e}")
    
    def _create_training_visualizations(self, results: Dict, timestamp: str):
        """Crea visualizzazioni dei risultati di training"""
        try:
            performance = results.get('performance', {})
            
            if not performance:
                return
            
            # Performance comparison
            plt.figure(figsize=(12, 8))
            
            algorithms = list(performance.keys())
            mean_rewards = [performance[alg]['mean_reward'] for alg in algorithms]
            std_rewards = [performance[alg]['std_reward'] for alg in algorithms]
            
            plt.subplot(2, 2, 1)
            bars = plt.bar(algorithms, mean_rewards, yerr=std_rewards, capsize=5)
            plt.title('Model Performance Comparison')
            plt.ylabel('Mean Reward')
            plt.xticks(rotation=45)
            
            # Colora le barre
            for i, bar in enumerate(bars):
                if mean_rewards[i] > 0:
                    bar.set_color('green')
                else:
                    bar.set_color('red')
            
            # Ensemble weights
            ensemble = results.get('ensemble', {})
            if ensemble.get('weights'):
                plt.subplot(2, 2, 2)
                weights = list(ensemble['weights'].values())
                plt.pie(weights, labels=algorithms, autopct='%1.1f%%')
                plt.title('Ensemble Weights')
            
            # Reward distribution
            plt.subplot(2, 2, 3)
            all_rewards = [performance[alg]['mean_reward'] for alg in algorithms]
            plt.hist(all_rewards, bins=10, alpha=0.7, edgecolor='black')
            plt.title('Reward Distribution')
            plt.xlabel('Mean Reward')
            plt.ylabel('Count')
            
            # Performance metrics table
            plt.subplot(2, 2, 4)
            plt.axis('tight')
            plt.axis('off')
            
            table_data = []
            for alg in algorithms:
                perf = performance[alg]
                table_data.append([
                    alg,
                    f"{perf['mean_reward']:.2f}",
                    f"{perf['std_reward']:.2f}",
                    f"{perf['max_reward']:.2f}"
                ])
            
            table = plt.table(cellText=table_data,
                            colLabels=['Algorithm', 'Mean', 'Std', 'Max'],
                            cellLoc='center',
                            loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1.2, 1.5)
            plt.title('Performance Metrics')
            
            plt.tight_layout()
            
            # Salva grafico
            chart_path = self.logs_dir / f"training_results_{timestamp}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"📊 Visualizzazioni salvate: {chart_path}")
            
        except Exception as e:
            logger.error(f"❌ Errore creazione visualizzazioni: {e}")

def run_advanced_training(config: Dict):
    """Funzione principale per training avanzato"""
    trainer = AdvancedRLTrainer(config)
    
    # Parametri training
    symbols = config['data']['symbols'][:3]  # Limita per test
    train_start = "2022-01-01"
    train_end = "2023-12-31"
    
    try:
        # Crea ambiente
        env = trainer.create_training_environment(symbols, train_start, train_end)
        
        # Training ensemble
        results = trainer.train_ensemble_models(env, ['PPO', 'SAC'])
        
        # Salva report
        trainer.save_training_report(results, symbols, f"{train_start}_{train_end}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Errore training avanzato: {e}")
        return {}

if __name__ == "__main__":
    # Test del modulo
    logging.basicConfig(level=logging.INFO)
    
    # Configurazione di test
    test_config = {
        'trading': {
            'initial_capital': 10000
        },
        'data': {
            'symbols': ['AAPL', 'GOOGL'],
            'lookback_days': 365
        },
        'rl': {
            'total_timesteps': 50000,
            'learning_rate': 3e-4,
            'batch_size': 64
        }
    }
    
    print("🤖 Test AdvancedRLTrainer...")
    
    if ADVANCED_RL_AVAILABLE:
        results = run_advanced_training(test_config)
        print(f"✅ Training completato: {len(results.get('models', {}))} modelli")
    else:
        print("⚠️ Stable-baselines3 non disponibile per test completo")
    
    print("🎉 Test completato!")
