import streamlit as st
import pandas as pd
import requests

from plotly import graph_objs as go
from prophet.plot import plot_plotly, plot_components_plotly
import yfinance as yf
from mftool import Mftool
import datetime 
import cufflinks as cf
cf.go_offline()
cf.set_config_file(offline=False, world_readable=True)
from yahoo_fin import stock_info as si
import streamlit as st
from cryptocmd import CmcScraper
from plotly import graph_objs as go
import time
from prophet import Prophet
primaryColor="#6eb52f"
backgroundColor="#f0f0f5"
secondaryBackgroundColor="#e0e0ef"
textColor="#262730"
font="sans serif"
pd.options.display.float_format = '{:,.1f}'.format

mf = Mftool()

def get_symbol(symbol):
    x = symbol.upper()
    return x



ticker_lst = []

st.title('Equitopedia by Advik Maniyar')

st.sidebar.title('Options')

ticker = st.sidebar.text_input("Enter Ticker",value="AAPL")




option = st.sidebar.selectbox("Select Dashboard", ('Live Market Price','Company Info','Financials','Quarterly Analysis','Prediction','Mutual Funds','Cryptocurrency'))



st.header(option)

if option == 'Cryptocurrency':
    selected_ticker = st.sidebar.text_input("Select a ticker for prediction (i.e. BTC, ETH, LINK, etc.)", "BTC")

    ### Initialise scraper
    @st.cache
    def load_data(selected_ticker):
    	init_scraper = CmcScraper(selected_ticker)
    	crypto_df= init_scraper.get_dataframe()
    	return crypto_df
    
    ### Load the data
    data_load_state = st.sidebar.text('Loading data...')
    crypto_df = load_data(selected_ticker)
    st.write(crypto_df)
    
    ### Plot functions for regular & log plots
    def plot_raw_data():
    	fig = go.Figure()
    	fig.add_trace(go.Scatter(x=crypto_df['Date'], y=crypto_df['Close'], name="Close"))
    	fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
    	st.plotly_chart(fig)
    
    plot_raw_data()
    

if option =='Mutual Funds':

    m = pd.DataFrame([list(mf.get_scheme_codes().values()),list(mf.get_scheme_codes().keys())]).transpose()
    mf_name = st.selectbox(label = 'Select the mutual Fund' ,options = m[0])
    mf_number = m[1][m[m[0]=='{}'.format(mf_name)].index.values[0]] 
    f_house = mf.get_scheme_details(mf_number)['fund_house']
    s_type = mf.get_scheme_details(mf_number)['scheme_type']
    s_category = mf.get_scheme_details(mf_number)['scheme_category']
    s_start_date = mf.get_scheme_details(mf_number)['scheme_start_date']['date']
    nav = mf.get_scheme_quote(mf_number)['nav']
    last_update = mf.get_scheme_quote(mf_number)['last_updated']
    x_mf = pd.DataFrame(index = ['Fund House','Scheme type','Scheme category','Scheme start date','NAV', 'Last Updated'])
    x_mf[1] = [f_house,s_type,s_category,s_start_date,nav,last_update]
    x_mf.style.set_properties(**{'text-align': 'left'})
    st.subheader(mf_number + ' - ' +mf_name )
    st.text(x_mf.to_string(header=False))
    yz = pd.DataFrame(mf.get_scheme_historical_nav(mf_number)['data'])
    yz = yz.astype({'date': 'datetime64[ns]', 'nav': 'float'}, copy=False)
    yz = yz.set_index(['date'])[:7]
    #fig = plt.plot(yz.set_index(['date'])[:7])
    #plt.show()
    #st.plotly_chart(fig)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yz.index, y=yz['nav'], name="Mutual Funds"))
    fig.layout.update(title_text='Opening & Closing Price Chart', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)
    
if option =='Financials':
    st.subheader("Dividend:")
    st.write(pd.DataFrame(yf.Ticker(ticker).dividends))
    st.subheader("Balance Sheet Of the Company")
    df_bs = pd.DataFrame(yf.Ticker(ticker).balance_sheet)
    st.write(df_bs)
    st.subheader("Cash Flow:")
    st.write(yf.Ticker(ticker).cashflow)
    st.subheader("Financials:")
    st.write(yf.Ticker(ticker).financials)
    

        
if option =='Quarterly Analysis':
    st.subheader("Balancesheet:")
    st.write(yf.Ticker(ticker).quarterly_balance_sheet)
    st.subheader("Cashflow")
    st.write(yf.Ticker(ticker).quarterly_cashflow)
    st.subheader("Financials:")
    st.write(yf.Ticker(ticker).quarterly_financials)

if option == 'Live Market Price':
    now = datetime.datetime.now()
    time1 = now.strftime("%H:%M:%S")
    tickers = yf.Ticker(ticker)
    todays_data = tickers.history()
    time.sleep(2)
    company= get_symbol(ticker)
    st.subheader(company)
    st.text(ticker)
    st.subheader("Current:")
    st.text(todays_data['Close'][0])
    tickers = yf.Ticker(ticker)
    todays_data = tickers.history(period='1y')
    year_old_price = todays_data['Close'][0]
    current = si.get_live_price(ticker)
    st.text("52 week change: {:.2f} %".format(((current - year_old_price)*100)/year_old_price))
    START = "2015-01-01"
    TODAY = datetime.datetime.today().strftime("%Y-%m-%d")
    selected_stock = ticker

    @st.cache
    def load_data(ticker):
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data
    data = load_data(selected_stock)

    st.subheader('Intraday Data')
    st.write(data.tail())
    # Plot raw data
    def plot_raw_data():
    	fig = go.Figure()
    	fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
    	fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
    	fig.layout.update(title_text='Opening & Closing Price Chart', xaxis_rangeslider_visible=True)
    	st.plotly_chart(fig)  	
    plot_raw_data()

if option == 'Company Info':
    company= get_symbol(ticker)
    st.subheader(company)
    st.text("Address:"+str(yf.Ticker(ticker).info['address1']+ ", "+ yf.Ticker(ticker).info['city']+ ", "+ yf.Ticker(ticker).info['country']+ " - "+ yf.Ticker(ticker).info['zip']))
    st.text("Average Revenue for last 4 years(in relevant currency):"+str(yf.Ticker(ticker).info['totalRevenue']))
    st.text("Sector:"+str(str(yf.Ticker(ticker).info['sector'])))
    st.text("Summary:")
    st.write(str(yf.Ticker(ticker).info['longBusinessSummary']))
    st.subheader("Splits offered by the company:")
    st.write(pd.DataFrame(yf.Ticker(ticker).splits))
    st.subheader("Shareholders:")
    st.write(yf.Ticker(ticker).get_institutional_holders().head().drop('Date Reported',axis=1))
    
if option == 'Stocktwits':
    
    r = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json")
    data = r.json()
    for message in data['messages']:
        st.image(message['user']['avatar_url'])
        st.write(message['user']['username'])
        st.write(message['created_at'])
        st.write(message['body'])
        
if option =='Prediction':
    st.subheader('Prediction Dashboard')
    company= get_symbol(ticker)
    st.subheader(company)
    
    
    START = "2015-01-01"
    TODAY = datetime.datetime.today().strftime("%Y-%m-%d")

    selected_stock = ticker
    
    n_years = st.slider('Years of prediction:', 1, 4)
    period = n_years * 365
    
    
    @st.cache
    def load_data(ticker):
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data
    
    data = load_data(selected_stock)

    # Plot raw data
  
    # Predict forecast with Prophet.
    df_train = data[['Date','Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})
    
    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)
    
    # Show and plot forecast
    st.subheader('Forecast data')
    st.write(forecast.tail())

    
    st.write(f'Forecast plot for {n_years} years')
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1)
    
    
    st.write("Forecast components")
    fig2 = m.plot_components(forecast)
    st.write(fig2)
    
