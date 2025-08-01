import gym
from gym import spaces
import numpy as np

class TradingEnv(gym.Env):
    def __init__(self, prices):
        super(TradingEnv, self).__init__()
        self.prices = prices
        self.index = 0
        self.cash = 10.0
        self.shares = 0

        self.action_space = spaces.Discrete(3)  # 0: Hold, 1: Buy, 2: Sell
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(1,), dtype=np.float32)

    def reset(self):
        self.index = 0
        self.cash = 10.0
        self.shares = 0
        return [self.prices[self.index]]

    def step(self, action):
        price = self.prices[self.index]

        if action == 1 and self.cash >= price:
            self.shares += 1
            self.cash -= price
        elif action == 2 and self.shares > 0:
            self.cash += price
            self.shares -= 1

        self.index += 1
        done = self.index >= len(self.prices) - 1

        portfolio_value = self.cash + self.shares * price
        reward = portfolio_value - 10.0  # reward relativo al valore iniziale

        return [self.prices[self.index]], reward, done, {}

    def render(self, mode='human'):
        print(f"Step {self.index}, Cash: {self.cash:.2f}, Shares: {self.shares}, Total: {self.cash + self.shares * self.prices[self.index]:.2f}")

# Alias per compatibilità
TradingEnvironment = TradingEnv
