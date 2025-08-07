import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Any, Dict, Tuple, Union

class TradingEnv(gym.Env):
    """
    Custom Trading Environment compatible with gymnasium
    """
    
    def __init__(self, prices: Union[list, np.ndarray]):
        super(TradingEnv, self).__init__()
        self.prices = np.array(prices) if isinstance(prices, list) else prices
        self.index = 0
        self.cash = 10.0
        self.shares = 0
        self.initial_value = 10.0

        # Action space: 0: Hold, 1: Buy, 2: Sell
        self.action_space = spaces.Discrete(3)
        
        # Observation space: current price + portfolio state
        self.observation_space = spaces.Box(
            low=0, 
            high=np.inf, 
            shape=(3,),  # [price, cash, shares]
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        """Reset environment to initial state"""
        super().reset(seed=seed)
        
        self.index = 0
        self.cash = self.initial_value
        self.shares = 0
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Execute one time step"""
        if self.index >= len(self.prices) - 1:
            # Episode done
            observation = self._get_observation()
            info = self._get_info()
            return observation, 0.0, True, False, info
            
        price = float(self.prices[self.index])
        prev_portfolio_value = self.cash + self.shares * price

        # Execute action
        if action == 1 and self.cash >= price:  # Buy
            self.shares += 1
            self.cash -= price
        elif action == 2 and self.shares > 0:  # Sell
            self.cash += price
            self.shares -= 1
        # action == 0 is Hold, do nothing

        self.index += 1
        
        # Calculate reward
        if self.index < len(self.prices):
            current_price = float(self.prices[self.index])
            current_portfolio_value = self.cash + self.shares * current_price
            reward = current_portfolio_value - prev_portfolio_value
        else:
            reward = 0.0

        # Check if done
        done = self.index >= len(self.prices) - 1
        truncated = False  # For gymnasium compatibility
        
        observation = self._get_observation()
        info = self._get_info()

        return observation, reward, done, truncated, info

    def _get_observation(self) -> np.ndarray:
        """Get current observation"""
        if self.index < len(self.prices):
            price = float(self.prices[self.index])
        else:
            price = float(self.prices[-1])
            
        return np.array([price, self.cash, float(self.shares)], dtype=np.float32)
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional info"""
        if self.index < len(self.prices):
            current_price = float(self.prices[self.index])
            portfolio_value = self.cash + self.shares * current_price
        else:
            portfolio_value = self.cash
            
        return {
            'step': self.index,
            'portfolio_value': portfolio_value,
            'cash': self.cash,
            'shares': self.shares,
            'return': (portfolio_value - self.initial_value) / self.initial_value
        }

    def render(self, mode='human'):
        """Render the environment"""
        info = self._get_info()
        if mode == 'human':
            print(f"Step {info['step']}: "
                  f"Portfolio=${info['portfolio_value']:.2f}, "
                  f"Cash=${info['cash']:.2f}, "
                  f"Shares={info['shares']}, "
                  f"Return={info['return']:.2%}")

# Alias per compatibilità con codice esistente
TradingEnvironment = TradingEnv
