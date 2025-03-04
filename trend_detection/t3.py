import pandas as pd
import talib as ta
import plotly.graph_objects as go

def t3_indicator(df, lengtht3=140, factort3=0.7, highlight_movements=True):
    close = df['Close']

    # Function to calculate gd (using EMA and factor)
    def gd(src, length, factor):
        ema1 = ta.EMA(src, timeperiod=length)
        ema2 = ta.EMA(ema1, timeperiod=length)
        return ema1 * (1 + factor) - ema2 * factor

    # Calculate t3 using gd recursively
    t3 = gd(gd(gd(close, lengtht3, factort3), lengtht3, factort3), lengtht3, factort3)
    
    # Calculate color (based on price movement)
    if highlight_movements:
        t3_color = ['green' if t3[i] > t3[i-1] else 'red' for i in range(1, len(t3))]
        t3_color = ['#6d1e7f'] + t3_color  # first value has no comparison
    else:
        t3_color = ['#6d1e7f'] * len(t3)  # no color change
    
    df['t3'] = t3
    df['t3_color'] = t3_color
    
    return df

# Load the CSV file
df = pd.read_csv('/Users/noumanqureshi/Desktop/AutomationScripts/datafetching/df5.csv')

# Convert 'Open Time' to a datetime index
df['Open Time'] = pd.to_datetime(df['Open Time'])  # Convert 'Open Time' to datetime
df.set_index('Open Time', inplace=True)

# Ensure the CSV contains 'Open', 'High', 'Low', 'Close' columns
required_columns = ['Open', 'High', 'Low', 'Close']
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"The CSV file must contain {required_columns} columns.")

# Apply the T3 indicator
result_df = t3_indicator(df)

# Create the candlestick chart
candlestick = go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name='Candlestick'
)

# Create the T3 indicator plot
t3_plot = go.Scatter(
    x=result_df.index,
    y=result_df['t3'],
    mode='lines',
    name='T3 Indicator',
    line=dict(color='blue', width=2)
)

# Combine the candlestick chart and T3 plot
fig = go.Figure(data=[candlestick, t3_plot])

# Customize the layout
fig.update_layout(
    title='Candlestick Chart with T3 Indicator',
    xaxis_title='Time',
    yaxis_title='Price',
    xaxis_rangeslider_visible=False  # Disable the range slider
)

# Show the plot
fig.show()
