from stable_baselines3 import PPO
from trading_env import TradingEnv
from data_collector import get_stock_data

df = get_stock_data("AAPL", "1mo", "1d")
prices = df["Close"].dropna().values

env = TradingEnv(prices)
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)

model.save("ppo_trading_model")
