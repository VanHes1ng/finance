import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import datetime


#-------------------------------------------------------------------------------------------------------
# Page Configurations
#-------------------------------------------------------------------------------------------------------

st.set_page_config(page_title = "Seasonality", layout="wide", initial_sidebar_state="expanded", 
                   page_icon= "📈")

# Titles
st.header("Seasonality Performance", divider="gray")

st.sidebar.header("Seasonality")


#-------------------------------------------------------------------------------------------------------
# INPUTS
#-------------------------------------------------------------------------------------------------------

ticker = st.sidebar.selectbox(
    'Ticker:', ('^GSPC', 'ETH-USD', 'BTC-USD', "^IXIC"))

max_value = 2035
year = st.slider("Start Year", min_value=1960, max_value=max_value, value=2000, step=1)


#-------------------------------------------------------------------------------------------------------
# GET DATA
#-------------------------------------------------------------------------------------------------------

# Define a function to download data
@st.cache_data
def download_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

data = download_data(ticker, datetime.date(year, 1, 1), datetime.date(max_value, 1, 1))

# Set the app title and sidebar description
if ticker == "^GSPC":
    ticker = "S&P500"
if ticker == "^IXIC":
    ticker = "NASDAQ"


#-------------------------------------------------------------------------------------------------------
# RETURNS
#-------------------------------------------------------------------------------------------------------

log_returns = data["Adj Close"].pct_change()

# Resample to monthly frequency and calculate monthly returns
monthly_returns = log_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)

# Drop the NaN value at the beginning (since there's no previous month)
monthly_returns = monthly_returns.dropna()

y=(1 + log_returns).cumprod()


#-------------------------------------------------------------------------------------------------------
# VISUALIZATION OF DATA
#-------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------
# CUMULATIVE RETURNS CHART
ret = go.Figure()

# Create and style traces for cumulative returns
ret.add_trace(go.Scatter(
                        x       = data.index, 
                        y       = y,
                        mode    = 'lines',
                        name    = 'Cumulative Returns',
                        line    = dict(color='gray', width=2)
                        )
              )

# Highlight the selected with a light gray background
ret.add_trace(go.Scatter(x          = data.index, 
                        y           = y,
                        mode        = 'lines',
                        fill        = 'tozeroy',
                        fillcolor   = 'rgba(220, 220, 220, 0.5)',
                        line        = dict(color='rgba(255, 255, 255, 0)')
                        )
                )

ret.update_layout(title=ticker + " Cumulative Returns Chart")

#-------------------------------------------------------------------------------------------------------
# MONTHLY RETURNS HEAT MAP
# Create a DataFrame for monthly returns
monthly_returns_df = pd.DataFrame({'Date': monthly_returns.index, 'Monthly_Return': monthly_returns.values})

# Extract year and month from the Date column
monthly_returns_df['Year']  = monthly_returns_df['Date'].dt.year
monthly_returns_df['Month'] = monthly_returns_df['Date'].dt.month

# Calculate monthly avg returns
monthly_percentage_changes = monthly_returns_df.groupby('Month')['Monthly_Return'].mean()*100

# Pivot the DataFrame to create a heatmap
heatmap_data = monthly_returns_df.pivot_table(index='Year', columns='Month', values='Monthly_Return')



# Customize the color scale and axis labels for the heatmap
heatmap_data.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
heatmap_data.index.name = "Year"


# Create the heatmap using Plotly Express
heatmap_fig = px.imshow(np.round(heatmap_data*100,2),
                                labels=dict(x        = "Month", 
                                            y        = "Year", 
                                            color    = "Monthly Return"
                                            ),
                                title                       = f"Heatmap of Monthly Returns for {ticker}",
                                color_continuous_scale      = ["red", "white", "green"],
                                color_continuous_midpoint   = 0,
                                text_auto                   = True,
                                height                      = 1000
                                )

# Customize the color scale and axis labels for the heatmap
heatmap_fig.update_xaxes(tickvals=list(range(12)), 
                         ticktext = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
heatmap_fig.update_yaxes(title_text="Year")


#-------------------------------------------------------------------------------------------------------
#AVG MONTHLY RETURNS HISTOGRAM (for defined period)
percentage_changes_fig = go.Figure()

# Add Values to Monthly HeatMap
percentage_changes_fig.add_trace(go.Bar(
                                        x            = heatmap_data.columns, 
                                        y            = np.round(monthly_percentage_changes*100,2), 
                                        orientation  = 'v', 
                                        marker       = go.bar.Marker(
                                                                    color       = monthly_percentage_changes,
                                                                    colorscale  = "rdbu",
                                                                    cmid        = 0,
                                                                    colorbar    = dict(title="value"),
                                                                    line        = dict(color="rgb(0, 0, 0)", width = 1)
                                                                    )
                                        )
                                )

# Update layout
percentage_changes_fig.update_layout(title_text ='Average monthly performance', height=500)

percentage_changes_fig.update_xaxes(title_text = "Avg monthly returns")

percentage_changes_fig.add_hline(y=0)

percentage_changes_fig.add_annotation(
                                        text           = ("@VanHelsing")
                                        , showarrow    = False
                                        , x            = 1
                                        , y            = 0.1
                                        , xref         = 'paper'
                                        , yref         = 'paper' 
                                        , xanchor      = 'right'
                                        , yanchor      = 'bottom'
                                        , font         = dict(size=12, color="grey")
                                        , align        = "left"
                                        )

# Streamlit integration
st.plotly_chart(ret, use_container_width=True)
st.plotly_chart(heatmap_fig, use_container_width=True)
st.plotly_chart(percentage_changes_fig, use_container_width=False)

st.write(
    "About\n",
    "\nSeasonality Performance is not a financial advisor\n",
    "\nCopyright 2023 Snowflake Inc. All rights reserved.\n"
)
