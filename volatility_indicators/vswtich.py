import pandas as pd
import numpy as np
import talib
import matplotlib.pyplot as plt

csv_path = "/Users/noumanqureshi/Desktop/AutomationScripts/datafetching/1.csv"

def volatility_switch(df):
    """
    Calculate the 21-period Volatility Switch indicator using TALib.
    
    Parameters:
    df (pd.DataFrame): DataFrame with 'close' price column
    
    Returns:
    pd.Series: 21-period volatility switch values
    """
    df = df.copy()
    
    # Ensure 'close' column exists
    if 'Close' not in df.columns:
        print("Error: 'close' column is missing in the dataset.")
        return pd.Series()  # Return an empty series if 'close' column is not found
    
    # Calculate ROC with period 1 using TALib
    df['roc'] = talib.ROC(df['Close'], timeperiod=1)
    
    # Calculate 2-period SMA using TALib
    df['sma2'] = talib.SMA(df['Close'], timeperiod=2)
    
    # Calculate dr (ROC divided by SMA)
    df['dr'] = df['roc'] / df['sma2']
    
    # Calculate 21-period standard deviation (volatility)
    df['vola21'] = df['dr'].rolling(window=21).std()
    
    # Calculate volatility switch for 21-period
    switch21 = pd.Series(index=df.index, dtype=float)
    for i in range(len(df)):
        if i < 21:  # Not enough data for calculation
            continue
        
        current_vol = df['vola21'].iloc[i]
        count = 1  # Start with 1 as per original implementation
        
        # Compare current volatility with previous 20 periods
        for j in range(1, 21):
            if df['vola21'].iloc[i-j] <= current_vol:
                count += 1
        
        switch21.iloc[i] = count / 21
    
    # Return calculated switch values
    return switch21

def plot_volatility_switch(csv_path):
    """
    Load CSV data, calculate volatility switch indicator, and create visualization
    
    Parameters:
    csv_path (str): Path to your CSV file
    """
    # Load the CSV file
    print(f"Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Print column names for debugging
    print("\nColumns in CSV:")
    print(df.columns.tolist())
    
    # If your CSV has a date column, set it as index
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    
    # Calculate volatility switch indicator
    volswitch21 = volatility_switch(df)
    
    # Check if we have valid data for plotting
    if volswitch21.isna().all():
        print("\nWarning: No valid switch21 values to plot!")
        return df, volswitch21
    
    # Remove NaN values for plotting
    volswitch21 = volswitch21.dropna()
    
    # Check if we have enough data for plotting
    if len(volswitch21) == 0:
        print("\nWarning: No valid data points to plot!")
        return df, volswitch21
    
    # Create visualization
    plt.figure(figsize=(15, 7))
    plt.plot(volswitch21, label='VOLSWITCH_21', color='red', linewidth=0.5)
    plt.axhline(y=0.5, color='gray', linestyle='--', label='Median')
    plt.title('21-Period Volatility Switch Indicator')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return df, volswitch21

# Example usage:
# Replace 'your_file.csv' with your actual CSV file path
df, volswitch21 = plot_volatility_switch(csv_path)
