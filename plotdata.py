import pandas as pd
import plotly.graph_objects as go

# Load the CSV data
df = pd.read_csv('/Users/noumanqureshi/Desktop/AutomationScripts/datafetching/df5.csv', parse_dates=['Open Time'])

# Make sure the data is sorted by time in ascending order
df.sort_values(by='Open Time', inplace=True)

# Create the candlestick chart using Plotly
fig = go.Figure(data=[go.Candlestick(x=df['Open Time'],
                                     open=df['Open'],
                                     high=df['High'],
                                     low=df['Low'],
                                     close=df['Close'])])

# Update the layout for better presentation
fig.update_layout(
    title='DOGE/USDT Candlestick Chart',
    xaxis_title='Time',
    yaxis_title='Price (USDT)',
    xaxis_rangeslider_visible=False  # Hide the range slider for better visibility
)

# Show the plot
fig.show()
