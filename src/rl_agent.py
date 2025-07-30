import numpy as np
import pickle
import os
from datetime import datetime
import json

class TradingAgent:
    """Agente di Reinforcement Learning per il trading"""
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.1):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon  # Exploration rate
        
        # Q-table: {state: {action: q_value}}
        self.q_table = {}
        
        # Experience replay
        self.experiences = []
        self.max_experiences = 1000
        
        # Performance tracking
        self.performance_history = []
        
        # File per salvare il modello
        self.model_file = "/workspaces/stock-ai/data/rl_model.pkl"
        self.history_file = "/workspaces/stock-ai/data/performance_history.json"
        
        # Carica modello esistente se disponibile
        self.load_model()
    
    def get_state(self, df, ticker):
        """
        Converte i dati del titolo in uno stato discreto
        
        Args:
            df: DataFrame con i dati del titolo
            ticker: Simbolo del titolo
            
        Returns:
            str: Stato rappresentato come stringa
        """
        if len(df) < 5:
            return "insufficient_data"
        
        current_price = df["Close"].iloc[-1]
        prev_price = df["Close"].iloc[-2]
        avg_5d = df['Close'].rolling(window=5).mean().iloc[-1]
        volatility = df["Close"].pct_change().std()
        
        # Trend
        trend = "up" if current_price > prev_price else "down"
        
        # Posizione rispetto alla media
        position = "above" if current_price > avg_5d else "below"
        
        # Volatilità
        vol_level = "high" if volatility > 0.03 else "medium" if volatility > 0.015 else "low"
        
        return f"{ticker}_{trend}_{position}_{vol_level}"
    
    def get_action(self, state):
        """
        Seleziona un'azione basata sulla policy epsilon-greedy
        
        Args:
            state: Stato attuale
            
        Returns:
            str: Azione scelta ("buy", "hold", "sell")
        """
        actions = ["buy", "hold", "sell"]
        
        # Epsilon-greedy exploration
        if np.random.random() < self.epsilon:
            return np.random.choice(actions)
        
        # Exploitation: scegli l'azione con Q-value più alto
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in actions}
        
        return max(self.q_table[state], key=self.q_table[state].get)
    
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
    
    def save_model(self):
        """Salva il modello su file"""
        try:
            os.makedirs(os.path.dirname(self.model_file), exist_ok=True)
            
            model_data = {
                "q_table": self.q_table,
                "experiences": self.experiences,
                "learning_rate": self.learning_rate,
                "discount_factor": self.discount_factor,
                "epsilon": self.epsilon
            }
            
            with open(self.model_file, "wb") as f:
                pickle.dump(model_data, f)
            
            # Salva anche la storia delle performance
            with open(self.history_file, "w") as f:
                json.dump(self.performance_history, f, indent=2)
                
            print(f"✅ Modello salvato in {self.model_file}")
        except Exception as e:
            print(f"❌ Errore nel salvare il modello: {e}")
    
    def load_model(self):
        """Carica il modello da file"""
        try:
            if os.path.exists(self.model_file):
                with open(self.model_file, "rb") as f:
                    model_data = pickle.load(f)
                
                self.q_table = model_data.get("q_table", {})
                self.experiences = model_data.get("experiences", [])
                
                print(f"✅ Modello caricato da {self.model_file}")
                print(f"   Stati appresi: {len(self.q_table)}")
                print(f"   Esperienze: {len(self.experiences)}")
            
            # Carica storia performance
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    self.performance_history = json.load(f)
        except Exception as e:
            print(f"❌ Errore nel caricare il modello: {e}")
    
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
