from stable_baselines3 import PPO
from trading_env import TradingEnv
from data_collector import get_stock_data

df = get_stock_data("AAPL", "1mo", "1d")
prices = df["Close"].dropna().values

env = TradingEnv(prices)
model = PPO.load("ppo_trading_model")

obs = env.reset()
done = False
while not done:
    action, _ = model.predict(obs)
    obs, reward, done, _ = env.step(action)
    env.render()
