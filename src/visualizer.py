import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import webbrowser
import tempfile

logger = logging.getLogger(__name__)

class Visualizer:
    def __init__(self, config):
        self.config = config
        self.output_dir = Path("data/reports")
        self.output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def plot_symbol(self, symbol):
        """Plot charts for a symbol"""
        logger.info(f"Plotting charts for {symbol}")
        
        try:
            # Load data
            data_file = Path(f"data/{symbol}_data.csv")
            if not data_file.exists():
                logger.error(f"No data file found for {symbol}")
                return
                
            df = pd.read_csv(data_file, index_col=0, parse_dates=True)
            
            # Create subplots
            fig = make_subplots(
                rows=3, cols=1,
                subplot_titles=[f'{symbol} Price', 'Volume', 'Technical Indicators'],
                vertical_spacing=0.1,
                row_heights=[0.5, 0.25, 0.25]
            )
            
            # Price chart with candlesticks
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Price'
                ),
                row=1, col=1
            )
            
            # Volume
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['Volume'],
                    name='Volume',
                    marker_color='lightblue'
                ),
                row=2, col=1
            )
            
            # Moving averages
            if len(df) >= 20:
                sma_20 = df['Close'].rolling(20).mean()
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=sma_20,
                        name='SMA 20',
                        line=dict(color='orange')
                    ),
                    row=1, col=1
                )
            
            # RSI
            rsi = self.calculate_rsi(df['Close'])
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=rsi,
                    name='RSI',
                    line=dict(color='purple')
                ),
                row=3, col=1
            )
            
            # Add RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            
            fig.update_layout(
                title=f'{symbol} Technical Analysis',
                xaxis_rangeslider_visible=False,
                height=800
            )
            
            # Save and show
            output_file = self.output_dir / f"{symbol}_chart.html"
            fig.write_html(str(output_file))
            logger.info(f"Chart saved to {output_file}")
            
            # Open in browser
            webbrowser.open(f"file://{output_file.absolute()}")
            
        except Exception as e:
            logger.error(f"Error plotting {symbol}: {e}")
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def launch_dashboard(self):
        """Launch interactive dashboard"""
        logger.info("Launching interactive dashboard...")
        
        try:
            import dash
            from dash import dcc, html, Input, Output
            
            app = dash.Dash(__name__)
            
            app.layout = html.Div([
                html.H1("Stock AI Dashboard"),
                html.Div([
                    html.Label("Select Symbol:"),
                    dcc.Dropdown(
                        id='symbol-dropdown',
                        options=[{'label': s, 'value': s} for s in self.config['data']['symbols']],
                        value=self.config['data']['symbols'][0]
                    )
                ]),
                dcc.Graph(id='price-chart'),
                html.Div(id='portfolio-status')
            ])
            
            @app.callback(
                Output('price-chart', 'figure'),
                Input('symbol-dropdown', 'value')
            )
            def update_chart(symbol):
                return self.create_dashboard_chart(symbol)
            
            logger.info("Dashboard starting on http://127.0.0.1:8050")
            app.run_server(debug=False, port=8050)
            
        except ImportError:
            logger.error("Dash not installed. Install with: pip install dash")
        except Exception as e:
            logger.error(f"Error launching dashboard: {e}")
    
    def create_dashboard_chart(self, symbol):
        """Create chart for dashboard"""
        try:
            data_file = Path(f"data/{symbol}_data.csv")
            if not data_file.exists():
                return go.Figure()
                
            df = pd.read_csv(data_file, index_col=0, parse_dates=True)
            
            fig = go.Figure()
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name=symbol
                )
            )
            
            fig.update_layout(
                title=f'{symbol} Price Chart',
                xaxis_rangeslider_visible=False
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating dashboard chart: {e}")
            return go.Figure()
    
    def save_backtest_report(self, results):
        """Save backtest results as HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Backtest Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 20px; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Backtest Report</h1>
                <p>Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metric">
                <h3>Initial Value</h3>
                <p>${results.get('initial_value', 0):,.2f}</p>
            </div>
            
            <div class="metric">
                <h3>Final Value</h3>
                <p>${results.get('final_value', 0):,.2f}</p>
            </div>
            
            <div class="metric">
                <h3>Total Return</h3>
                <p class="{'positive' if results.get('return', 0) > 0 else 'negative'}">
                    {results.get('return', 0):.2f}%
                </p>
            </div>
            
        </body>
        </html>
        """
        
        report_file = self.output_dir / f"backtest_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_file, 'w') as f:
            f.write(html_content)
            
        logger.info(f"Backtest report saved to {report_file}")
        webbrowser.open(f"file://{report_file.absolute()}")
    
    def save_report_html(self, report_data):
        """Save portfolio report as HTML"""
        if isinstance(report_data, str):
            try:
                import json
                data = json.loads(report_data)
            except:
                data = {"error": "Could not parse report data"}
        else:
            data = report_data
            
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Portfolio Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>📈 Portfolio Report</h1>
            <p>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="section">
                <h2>Portfolio Data</h2>
                <pre>{json.dumps(data, indent=2)}</pre>
            </div>
        </body>
        </html>
        """
        
        report_file = self.output_dir / f"portfolio_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_file, 'w') as f:
            f.write(html_content)
            
        logger.info(f"Portfolio report saved to {report_file}")
        webbrowser.open(f"file://{report_file.absolute()}")
