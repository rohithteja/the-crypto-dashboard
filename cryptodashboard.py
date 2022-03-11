#-------------------
# Imports
#-------------------
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from bs4 import BeautifulSoup
import requests
from datetime import datetime

# today's date
today = datetime.today().strftime('%d %B %Y')

st.set_page_config(layout="wide") 


#-------------------
# Web scraping Yahoo Finance
#-------------------
dic = {}
url = 'https://finance.yahoo.com/cryptocurrencies?offset=0&count=100'
soup = BeautifulSoup(requests.get(url).text)

# store values in separate lists and then in a dictionary
for listing in soup.find_all('div', attrs={'id':'fin-scr-res-table'}):
    symbol_list = []
    name_list = []
    price_list = []
    change_list = []
    mcap_list = []
for symbol in listing.find_all('td', attrs={'aria-label':'Symbol'}):
    symbol_list.append(symbol.text)
    dic['Symbol'] = symbol_list
for name in listing.find_all('td', attrs={'aria-label':'Name'}):
    name_list.append(name.text)
    dic['Name'] = name_list
for price in listing.find_all('td', attrs={'aria-label':'Price (Intraday)'}):
    price_list.append(price.text)
    dic['Price'] = price_list
for change in listing.find_all('td', attrs={'aria-label':'% Change'}):
    change_list.append(change.text)
    dic['% Change'] = change_list
for mcap in listing.find_all('td', attrs={'aria-label':'Market Cap'}):
    mcap_list.append(mcap.text)
    dic['Market Cap'] = mcap_list
      
# create a dataframe from dictionary 
df_scrape = pd.DataFrame(dic)
df_scrape.Symbol = df_scrape.Symbol.str.replace('-USD','')
df_scrape.Name = df_scrape.Name.str.replace(' USD','')
dic1 = dict(zip(df_scrape.Symbol,df_scrape.Name))


#-------------------
# Streamlit Sidebar
#-------------------
fiat = ['USD','EUR','GBP']
tokens = df_scrape.Symbol.values 

# filters selectbox
st.sidebar.title("Filters")
select_token = st.sidebar.selectbox('Tokens', tokens)
select_fiat = st.sidebar.selectbox('Fiat', fiat)

# special expander objects
st.sidebar.markdown('***')
with st.sidebar.expander('Help'):
    st.markdown('''
                    - Select token and fiat of your choice.
                    - Interactive plots can be zoomed or hovered to retrieve more info.
                    - Plots can be downloaded using Plotly tools.''')

with st.sidebar.expander('Sources'):
    st.markdown('''
    - Python Libraries: yfinance, BeautifulSoup, Plotly, Pandas, Streamlit
    - Prices: https://finance.yahoo.com
    - Logos: https://cryptologos.cc/
    ''')

# Links to socials
st.sidebar.markdown('## Reach Me')
col1, col2, col3, col4 = st.sidebar.columns([2,2,2,3])
with col1:
    link = '[Medium](https://medium.com/@rohithtejam)'
    st.markdown(link, unsafe_allow_html=True)
with col2:
    link = '[LinkedIn](https://www.linkedin.com/in/rohithteja/)'
    st.markdown(link, unsafe_allow_html=True)
with col3:
    link = '[Twitter](https://twitter.com/rohithtejam)'
    st.markdown(link, unsafe_allow_html=True)
with col4:
    link = '[GitHub](https://github.com/rohithteja)'
    st.markdown(link, unsafe_allow_html=True)
    


#-------------------
# Title Image
#-------------------
col1, col2, col3 = st.columns([1,6,1])
with col1:
    st.write("")
with col2:
    st.image('title.png',width=600)
with col3:
    st.write("")
    
st.markdown('***')

#-------------------
# Add crypto logo and name
#-------------------
col1, col2 = st.columns([1,10])
with col1:
    try:
        st.image(f'logos/{select_token}.png',width=70)
    except:
        pass
with col2:
    st.markdown(f'''## {dic1[select_token]}''')


#-------------------
# Candlestick chart with moving averages
#-------------------    
st.markdown('''
- The following is an interactive Candlestick chart for the price fluctuations over the past 5 years. 
- Simple moving averages were computed for 20, 50 and 100 day frequencies.
- Aids in trading strategy and to better interpret the price fluctuations.''')

# download 5 year crypto prices from Yahoo Finance
df = yf.download(tickers=f'{select_token}-{select_fiat}', period = '5y', interval = '1d')

# compute moving averages
df['MA100'] = df.Close.rolling(100).mean()
df['MA50'] = df.Close.rolling(50).mean()
df['MA20'] = df.Close.rolling(20).mean()

# Plotly candlestick chart
fig = go.Figure(data=
                [go.Candlestick(x=df.index,
                                open=df.Open, 
                                high=df.High,
                                low=df.Low,
                                close=df.Close,
                                name=f'{select_token}'), 
                go.Scatter(x=df.index, y=df.MA20, 
                            line=dict(color='yellow',width=1),name='MA20'),
                go.Scatter(x=df.index, y=df.MA50, 
                            line=dict(color='green',width=1),name='MA50'),
                go.Scatter(x=df.index, y=df.MA100, 
                            line=dict(color='red',width=1),name='MA100')])
    
fig.update_layout(go.Layout(xaxis = {'showgrid': False},
                  yaxis = {'showgrid': False}),
                  title=f'{dic1[select_token]} Price Fluctuation with Moving Averages',
                    yaxis_title=f'Price ({select_fiat})', 
                    xaxis_rangeslider_visible=False)

st.plotly_chart(fig, use_container_width=True)

#-------------------
# Line Chart with daily trends
#-------------------
st.markdown('## Daily Trends')
st.markdown(f'''
- Line graph below shows the price fluctuation of {dic1[select_token]} every minute for today's date ({today}).
- The data is automatically updated for the current day.
- The horizontal line shows the current day's open price.
- Green portion indicates the price greater than open price and red for lower.
''')

# download daily crypto prices from Yahoo Finance
df = yf.download(tickers=f'{select_token}-{select_fiat}', period = '1d', interval = '1m')

# Plotly line chart
fig = go.Figure()
fig.add_scattergl(x=df.index, y=df.Close, 
                  line={'color': 'green'},name='Up trend')
fig.add_scattergl(x=df.index, y=df.Close.where(df.Close <= df.Open[0]), 
                  line={'color': 'red'},name='Down trend')
fig.add_hline(y=df.Open[0])
fig.update_layout(go.Layout(xaxis = {'showgrid': False},
                  yaxis = {'showgrid': False}),
                  title=f'{dic1[select_token]} Daily Trends in Comparison to Open Price',
                    yaxis_title=f'Price ({select_fiat})',template='plotly_dark',
                    xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

#-------------------
# Table showing top 25 cryptos
#-------------------
st.markdown('## Top 25 Cryptocurrency Prices and Stats')
st.markdown('''
- Realtime price changes (in USD).
- Values updated every few minutes.
- Colour coded column indicates the increase or decrease in price.
''')

# create table from webscraped data
df_scrape = df_scrape.rename(columns={'Symbol':'Token'})
df_scrape['% Change'] = df_scrape['% Change'].str.replace('%','').astype(float)

df_scrape["color"] = df_scrape["% Change"].map(lambda x:'red' if x<0 else 'green')
cols_to_show = ['Name','Token', 'Price', '% Change', 'Market Cap']

# to change color of "% change" column
fill_color = []
n = len(df_scrape)
for col in cols_to_show:
    if col!='% Change':
        fill_color.append(['black']*n)
    else:
        fill_color.append(df_scrape["color"].to_list())

# Plotly Table
data=[go.Table(columnwidth = [20,15,15,15,15],
                header=dict(values=[f"<b>{col}</b>" for col in cols_to_show],
                font=dict(color='white', size=20),
                height=30,
                line_color='black',
                fill_color='dimgrey',
                align=['left','left', 'right','right','right']),
                cells=dict(values=df_scrape[cols_to_show].values.T,
               fill_color=fill_color,
               font=dict(color='white', size=20),
               height=30,
               line_color='black',
               align=['left','left', 'right','right','right']))]

fig = go.Figure(data=data)
fig.update_layout(go.Layout(xaxis = {'showgrid': False},
                  yaxis = {'showgrid': False}))
st.plotly_chart(fig, use_container_width=True)

