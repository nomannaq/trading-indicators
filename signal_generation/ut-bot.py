import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import talib

def preprocess_binance_data(df):
    """
    Preprocess Binance format data
    """
    df = df.copy()
    
    # Convert datetime strings to datetime objects without unit specification
    df['Open Time'] = pd.to_datetime(df['Open Time'])
    df['Close Time'] = pd.to_datetime(df['Close Time'])
    
    df.set_index('Open Time', inplace=True)
    price_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df[price_columns] = df[price_columns].astype(float)
    df.columns = df.columns.str.lower()
    return df

def calculate_ut_bot(df, key_value=3, atr_period=10):
    """
    Calculate the UT Bot indicator values using TALib
    """
    df = df.copy()
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=atr_period)
    n_loss = key_value * df['atr']
    
    df['xATRTrailingStop'] = 0.0
    
    for i in range(1, len(df)):
        prev_stop = df['xATRTrailingStop'].iloc[i-1]
        curr_close = df['close'].iloc[i]
        prev_close = df['close'].iloc[i-1]
        curr_loss = n_loss.iloc[i]
        
        if curr_close > prev_stop and prev_close > prev_stop:
            df['xATRTrailingStop'].iloc[i] = max(prev_stop, curr_close - curr_loss)
        elif curr_close < prev_stop and prev_close < prev_stop:
            df['xATRTrailingStop'].iloc[i] = min(prev_stop, curr_close + curr_loss)
        elif curr_close > prev_stop:
            df['xATRTrailingStop'].iloc[i] = curr_close - curr_loss
        else:
            df['xATRTrailingStop'].iloc[i] = curr_close + curr_loss
    
    df['position'] = 0
    
    for i in range(1, len(df)):
        prev_close = df['close'].iloc[i-1]
        curr_close = df['close'].iloc[i]
        prev_stop = df['xATRTrailingStop'].iloc[i-1]
        
        if prev_close < prev_stop and curr_close > prev_stop:
            df['position'].iloc[i] = 1
        elif prev_close > prev_stop and curr_close < prev_stop:
            df['position'].iloc[i] = -1
        else:
            df['position'].iloc[i] = df['position'].iloc[i-1]
    
    df['buy_signal'] = (df['close'] > df['xATRTrailingStop']) & (df['close'].shift(1) <= df['xATRTrailingStop'].shift(1))
    df['sell_signal'] = (df['close'] < df['xATRTrailingStop']) & (df['close'].shift(1) >= df['xATRTrailingStop'].shift(1))
    
    return df

def plot_signals_plotly(df):
    """
    Create an interactive Plotly chart with price, trailing stop, and signals
    """
    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.03,
                       subplot_titles=('Price & Signals', 'Volume'),
                       row_heights=[0.7, 0.3])

    # Add candlestick
    fig.add_trace(go.Candlestick(x=df.index,
                                open=df['open'],
                                high=df['high'],
                                low=df['low'],
                                close=df['close'],
                                name='OHLC'),
                  row=1, col=1)

    # Add trailing stop
    fig.add_trace(go.Scatter(x=df.index,
                            y=df['xATRTrailingStop'],
                            name='Trailing Stop',
                            line=dict(color='gray', width=1)),
                  row=1, col=1)

    # Add buy signals
    buy_signals = df[df['buy_signal']]
    fig.add_trace(go.Scatter(x=buy_signals.index,
                            y=buy_signals['close'],
                            name='Buy Signal',
                            mode='markers',
                            marker=dict(symbol='triangle-up',
                                      size=12,
                                      color='green',
                                      line=dict(width=1,
                                              color='darkgreen')),
                            ),
                  row=1, col=1)

    # Add sell signals
    sell_signals = df[df['sell_signal']]
    fig.add_trace(go.Scatter(x=sell_signals.index,
                            y=sell_signals['close'],
                            name='Sell Signal',
                            mode='markers',
                            marker=dict(symbol='triangle-down',
                                      size=12,
                                      color='red',
                                      line=dict(width=1,
                                              color='darkred')),
                            ),
                  row=1, col=1)

    # Add volume bars
    fig.add_trace(go.Bar(x=df.index,
                        y=df['volume'],
                        name='Volume',
                        marker_color='lightgray'),
                  row=2, col=1)

    # Update layout
    fig.update_layout(
        title='UT Bot Trading Signals',
        yaxis_title='Price',
        yaxis2_title='Volume',
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    # Update y-axes labels
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig

def calculate_metrics(df):
    """
    Calculate trading metrics
    """
    df = df.copy()
    
    # Calculate returns
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['position'].shift(1) * df['returns']
    
    # Calculate metrics
    total_returns = df['strategy_returns'].sum()
    sharpe_ratio = (df['strategy_returns'].mean() / df['strategy_returns'].std()) * np.sqrt(252) if len(df) > 0 else 0
    
    metrics = {
        'Total Returns': f"{total_returns:.2%}",
        'Sharpe Ratio': f"{sharpe_ratio:.2f}",
        'Total Trades': len(df[df['buy_signal']]) + len(df[df['sell_signal']]),
        'Buy Signals': len(df[df['buy_signal']]),
        'Sell Signals': len(df[df['sell_signal']])
    }
    
    print("\nTrading Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    return metrics

def main(csv_path, key_value=3, atr_period=10):
    """
    Process CSV file and generate UT Bot signals with Plotly visualization
    """
    # Read CSV file
    df = pd.read_csv(csv_path)
    
    # Preprocess data
    df = preprocess_binance_data(df)
    
    # Calculate indicators
    result = calculate_ut_bot(df, key_value, atr_period)
    
    # Calculate metrics
    metrics = calculate_metrics(result)
    
    # Create Plotly chart
    fig = plot_signals_plotly(result)
    
    # Show the plot
    fig.show()
    
    return result, fig

# Example usage:
"""
# Load and process data, get both the DataFrame and Plotly figure
df, fig = main('your_binance_data.csv', key_value=3, atr_period=10)

# If you want to save the plot to HTML
fig.write_html("ut_bot_signals.html")

# If you want to customize the plot further

"""

if __name__ == "__main__":
    csv_path = '/Users/noumanqureshi/Desktop/AutomationScripts/datafetching/1.csv'  # Specify the path to your CSV file
    main(csv_path, key_value=3, atr_period=10)