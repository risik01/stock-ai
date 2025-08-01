import numpy as np
import pandas as pd
import pickle
import logging
from pathlib import Path
import gymnasium as gym
from gymnasium import spaces
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class TradingEnvironment(gym.Env):
    """Custom trading environment for RL agent"""
    
    def __init__(self, data, initial_capital=10000):
        super(TradingEnvironment, self).__init__()
        
        self.data = data
        self.initial_capital = initial_capital
        self.current_step = 0
        self.max_steps = len(data) - 1
        
        # Action space: 0=hold, 1=buy, 2=sell
        self.action_space = spaces.Discrete(3)
        
        # Observation space: price features + portfolio state
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, 
            shape=(10,), dtype=np.float32
        )
        
        self.reset()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.cash = self.initial_capital
        self.shares = 0
        self.total_value = self.initial_capital
        return self._get_observation(), {}
    
    def step(self, action):
        if self.current_step >= len(self.data):
            return self._get_observation(), 0, True, False, {}
            
        current_price = self.data.iloc[self.current_step]['Close']
        
        # Execute action
        if action == 1:  # Buy
            shares_to_buy = self.cash // current_price
            self.shares += shares_to_buy
            self.cash -= shares_to_buy * current_price
        elif action == 2:  # Sell
            self.cash += self.shares * current_price
            self.shares = 0
        
        # Move to next step
        self.current_step += 1
        
        # Calculate reward
        new_total_value = self.cash + self.shares * current_price
        reward = new_total_value - self.total_value
        self.total_value = new_total_value
        
        done = self.current_step >= self.max_steps
        truncated = False
        
        return self._get_observation(), reward, done, truncated, {}
    
    def _get_observation(self):
        if self.current_step >= len(self.data):
            return np.zeros(10, dtype=np.float32)
            
        row = self.data.iloc[self.current_step]
        
        # Technical indicators as features
        features = [
            row['Close'],
            row['Volume'],
            row['High'] - row['Low'],  # Daily range
            self.cash / self.initial_capital,  # Cash ratio
            self.shares,  # Share count
            self.total_value / self.initial_capital,  # Portfolio performance
        ]
        
        # Add some simple technical indicators
        if self.current_step > 5:
            sma_5 = self.data['Close'].iloc[self.current_step-5:self.current_step].mean()
            features.append(row['Close'] / sma_5 - 1)  # Price vs SMA ratio
        else:
            features.append(0)
            
        if self.current_step > 1:
            price_change = (row['Close'] / self.data.iloc[self.current_step-1]['Close']) - 1
            features.append(price_change)
        else:
            features.append(0)
            
        # Pad to fixed size
        while len(features) < 10:
            features.append(0)
            
        return np.array(features[:10], dtype=np.float32)

class RLAgent:
    def __init__(self, config):
        self.config = config
        self.model_file = Path("data/rl_model.pkl")
        self.learning_rate = config['rl_agent']['learning_rate']
        self.epsilon = config['rl_agent']['epsilon']
        self.discount_factor = config['rl_agent']['discount_factor']
        
        # Simple Q-learning agent
        self.q_table = {}
        self.training_stats = {
            'episodes': 0,
            'total_reward': 0,
            'average_reward': 0
        }
        
        # Experience replay
        self.experiences = []
        self.max_experiences = 1000
        
        # Performance tracking
        self.performance_history = []
        
        # File per salvare il modello
        self.history_file = "/workspaces/stock-ai/data/performance_history.json"
        
        self.load_model()
    
    def load_model(self):
        """Load trained model"""
        if self.model_file.exists():
            try:
                with open(self.model_file, 'rb') as f:
                    data = pickle.load(f)
                    self.q_table = data.get('q_table', {})
                    self.training_stats = data.get('stats', self.training_stats)
                logger.info("Loaded trained RL model")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
    
    def save_model(self):
        """Save trained model"""
        data = {
            'q_table': self.q_table,
            'stats': self.training_stats
        }
        with open(self.model_file, 'wb') as f:
            pickle.dump(data, f)
        logger.info("Saved RL model")
    
    def get_state_key(self, observation):
        """Convert observation to state key for Q-table"""
        # Discretize continuous values
        discretized = []
        for val in observation:
            if abs(val) < 0.01:
                discretized.append(0)
            elif val > 0:
                discretized.append(1)
            else:
                discretized.append(-1)
        return tuple(discretized)
    
    def get_action(self, market_state):
        """Get action from trained agent"""
        # Convert market state to observation
        observation = self._market_state_to_observation(market_state)
        state_key = self.get_state_key(observation)
        
        # Epsilon-greedy action selection
        if np.random.random() < self.epsilon:
            action_idx = np.random.choice(3)
        else:
            q_values = self.q_table.get(state_key, [0, 0, 0])
            action_idx = np.argmax(q_values)
        
        # Convert action index to trading action
        actions = ['hold', 'buy', 'sell']
        action_type = actions[action_idx]
        
        # Create action with default symbol (would be improved)
        if len(market_state) > 0:
            symbol = list(market_state.keys())[0]
            price = market_state[symbol]['close']
            
            return {
                'symbol': symbol,
                'type': action_type,
                'quantity': 10 if action_type in ['buy', 'sell'] else 0,
                'price': price
            }
        
        return {'symbol': 'AAPL', 'type': 'hold', 'quantity': 0, 'price': 0}
    
    def _market_state_to_observation(self, market_state):
        """Convert market state to observation array"""
        if not market_state:
            return np.zeros(10)
            
        # Use first symbol's data
        symbol_data = list(market_state.values())[0]
        
        obs = [
            symbol_data.get('close', 0),
            symbol_data.get('volume', 0) / 1000000,  # Normalize volume
            symbol_data.get('rsi', 50) / 100,  # Normalize RSI
            symbol_data.get('price_change_1d', 0),
            symbol_data.get('sma_5', 0) / symbol_data.get('close', 1),
            symbol_data.get('sma_10', 0) / symbol_data.get('close', 1),
            symbol_data.get('sma_20', 0) / symbol_data.get('close', 1),
            symbol_data.get('macd', 0),
            symbol_data.get('bb_upper', 0) / symbol_data.get('close', 1),
            symbol_data.get('bb_lower', 0) / symbol_data.get('close', 1),
        ]
        
        return np.array(obs[:10], dtype=np.float32)
    
    def train(self, training_data, episodes):
        """Train the RL agent"""
        logger.info(f"Training RL agent for {episodes} episodes")
        
        try:
            # Prepare training data
            if isinstance(training_data, pd.DataFrame) and not training_data.empty:
                # Check if we have the required columns
                required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                if not all(col in training_data.columns for col in required_columns):
                    logger.error(f"Training data missing required columns: {required_columns}")
                    return
                    
                # Use first symbol's data for training
                if 'Symbol' in training_data.columns:
                    symbol_data = training_data[training_data['Symbol'] == training_data['Symbol'].iloc[0]]
                else:
                    symbol_data = training_data
                    
                if symbol_data.empty:
                    logger.error("No symbol data available for training")
                    return
                    
                env = TradingEnvironment(symbol_data)
            else:
                logger.error("Invalid or empty training data")
                return
            
            total_rewards = []
            
            for episode in range(episodes):
                try:
                    state, _ = env.reset()
                    total_reward = 0
                    done = False
                    step_count = 0
                    max_steps = 1000  # Prevent infinite loops
                    
                    while not done and step_count < max_steps:
                        state_key = self.get_state_key(state)
                        
                        # Epsilon-greedy action selection
                        if np.random.random() < self.epsilon:
                            action = np.random.choice(3)
                        else:
                            q_values = self.q_table.get(state_key, [0, 0, 0])
                            action = np.argmax(q_values)
                        
                        next_state, reward, done, truncated, _ = env.step(action)
                        next_state_key = self.get_state_key(next_state)
                        
                        # Q-learning update
                        if state_key not in self.q_table:
                            self.q_table[state_key] = [0, 0, 0]
                        
                        current_q = self.q_table[state_key][action]
                        next_q_values = self.q_table.get(next_state_key, [0, 0, 0])
                        max_next_q = max(next_q_values)
                        
                        new_q = current_q + self.learning_rate * (
                            reward + self.discount_factor * max_next_q - current_q
                        )
                        self.q_table[state_key][action] = new_q
                        
                        state = next_state
                        total_reward += reward
                        step_count += 1
                        
                        if truncated:
                            done = True
                    
                    total_rewards.append(total_reward)
                    
                    # Decay epsilon
                    self.epsilon = max(0.01, self.epsilon * 0.995)
                    
                    if episode % 100 == 0:
                        avg_reward = np.mean(total_rewards[-100:]) if total_rewards else 0
                        logger.info(f"Episode {episode}, Average Reward: {avg_reward:.2f}, Epsilon: {self.epsilon:.3f}")
                        
                except Exception as e:
                    logger.error(f"Error in training episode {episode}: {e}")
                    continue
            
            # Update stats
            self.training_stats['episodes'] += episodes
            self.training_stats['total_reward'] = sum(total_rewards) if total_rewards else 0
            self.training_stats['average_reward'] = np.mean(total_rewards) if total_rewards else 0
            
            self.save_model()
            logger.info(f"Training completed. Average reward: {self.training_stats['average_reward']:.2f}")
            
        except Exception as e:
            logger.error(f"Error in training: {e}")
    
    def backtest(self, data, portfolio):
        """Run backtesting"""
        logger.info("Running backtest...")
        
        # Simple backtest implementation
        initial_value = portfolio.get_total_value()
        
        # Simulate trading over historical data
        for symbol, df in data.items():
            for i in range(len(df)):
                # Create mock market state
                market_state = {symbol: {'close': df.iloc[i]['Close']}}
                action = self.get_action(market_state)
                portfolio.simulate_trade(action)
        
        final_value = portfolio.get_total_value()
        
        return {
            'initial_value': initial_value,
            'final_value': final_value,
            'return': (final_value / initial_value - 1) * 100
        }
    
    def get_stats(self):
        """Get training statistics"""
        return self.training_stats
    
    def is_trained(self):
        """Check if agent is trained"""
        return len(self.q_table) > 0
    
    def add_experience(self, state, action, reward, next_state, portfolio_value):
        """
        Aggiunge un'esperienza alla memoria
        
        Args:
            state: Stato
            action: Azione
            reward: Ricompensa
            next_state: Nuovo stato
            portfolio_value: Valore del portafoglio
        """
        experience = {
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": next_state,
            "portfolio_value": portfolio_value,
            "timestamp": datetime.now().isoformat()
        }
        
        self.experiences.append(experience)
        
        # Mantieni solo le ultime N esperienze
        if len(self.experiences) > self.max_experiences:
            self.experiences.pop(0)
        
        # Aggiorna Q-value
        self.update_q_value(state, action, reward, next_state)
    
    def replay_experiences(self, batch_size=32):
        """
        Replay delle esperienze per migliorare l'apprendimento
        
        Args:
            batch_size: Dimensione del batch per il replay
        """
        if len(self.experiences) < batch_size:
            return
        
        # Seleziona esperienze casuali
        batch = np.random.choice(self.experiences, batch_size, replace=False)
        
        for exp in batch:
            self.update_q_value(exp["state"], exp["action"], exp["reward"], exp["next_state"])
    
    def update_q_value(self, state, action, reward, next_state):
        """
        Aggiorna il Q-value usando l'equazione di Bellman
        
        Args:
            state: Stato precedente
            action: Azione eseguita
            reward: Ricompensa ricevuta
            next_state: Nuovo stato
        """
        if state not in self.q_table:
            self.q_table[state] = {"buy": 0.0, "hold": 0.0, "sell": 0.0}
        
        if next_state not in self.q_table:
            self.q_table[next_state] = {"buy": 0.0, "hold": 0.0, "sell": 0.0}
        
        # Q-learning update
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state].values())
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q
    
    def calculate_reward(self, action, price_change_pct, portfolio_performance):
        """
        Calcola la ricompensa basata sull'azione e performance
        
        Args:
            action: Azione eseguita
            price_change_pct: Variazione percentuale del prezzo
            portfolio_performance: Performance del portafoglio
            
        Returns:
            float: Ricompensa
        """
        base_reward = 0
        
        if action == "buy":
            # Ricompensa positiva se il prezzo sale dopo l'acquisto
            base_reward = price_change_pct * 10
        elif action == "sell":
            # Ricompensa positiva se il prezzo scende dopo la vendita
            base_reward = -price_change_pct * 10
        elif action == "hold":
            # Piccola ricompensa per non fare nulla
            base_reward = 0.1
        
        # Bonus/penalità basata sulla performance del portafoglio
        portfolio_bonus = portfolio_performance * 5
        
        return base_reward + portfolio_bonus
    
    def get_learning_stats(self):
        """
        Restituisce statistiche sull'apprendimento
        
        Returns:
            dict: Statistiche
        """
        total_states = len(self.q_table)
        total_experiences = len(self.experiences)
        
        # Calcola la confidence media
        avg_confidence = 0
        if total_states > 0:
            all_q_values = []
            for state_actions in self.q_table.values():
                all_q_values.extend(state_actions.values())
            avg_confidence = np.mean(np.abs(all_q_values)) if all_q_values else 0
        
        return {
            "total_states": total_states,
            "total_experiences": total_experiences,
            "avg_confidence": avg_confidence,
            "epsilon": self.epsilon,
            "performance_history": self.performance_history[-10:]  # Ultime 10
        }
    
    def decay_epsilon(self, min_epsilon=0.01, decay_rate=0.995):
        """
        Riduce gradualmente l'exploration rate
        
        Args:
            min_epsilon: Valore minimo di epsilon
            decay_rate: Tasso di decadimento
        """
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)
