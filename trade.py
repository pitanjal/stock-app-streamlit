import streamlit as st
import requests
import os
import sys
import subprocess

# check if the library folder already exists, to avoid building everytime you load the pahe
if not os.path.isdir("/tmp/ta-lib"):

    # Download ta-lib to disk
    with open("/tmp/ta-lib-0.4.0-src.tar.gz", "wb") as file:
        response = requests.get(
            "http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz"
        )
        file.write(response.content)
    # get our current dir, to configure it back again. Just house keeping
    default_cwd = os.getcwd()
    os.chdir("/tmp")
    # untar
    os.system("tar -zxvf ta-lib-0.4.0-src.tar.gz")
    os.chdir("/tmp/ta-lib")
    os.system("ls -la /app/equity/")
    # build
    os.system("./configure --prefix=/home/appuser")
    os.system("make")
    # install
    os.system("make install")
    # back to the cwd
    os.chdir(default_cwd)
    sys.stdout.flush()

# add the library to our current environment
from ctypes import *

lib = CDLL("/home/appuser/lib/libta_lib.so.0.0.0")
# import library
try:
    import talib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--global-option=build_ext", "--global-option=-L/home/appuser/lib/", "--global-option=-I/home/appuser/include/", "ta-lib"])
finally:
    import talib

# here goes your code
import streamlit as st
import numpy as np
import pandas as pd
import sqlite3
import time
# Raw Package
import talib
#Data Source
import yfinance as yf
#Data viz
#import plotly.graph_objs as go
from alice_blue import *
import logging
logging.basicConfig(level=logging.DEBUG)
import requests


st.set_page_config(page_title = 'TraDatAnalytix',
    layout='wide',
    page_icon='💹')

user = st.secrets["user"]
pwd = st.secrets["pwd"]
secret = st.secrets["secret"]
app = st.secrets["app"]





access_token = AliceBlue.login_and_get_access_token(username=user,
                                                    password=pwd,
                                                    twoFA='pit',
                                                    api_secret=secret,
                                                    app_id=app)

alice = AliceBlue(username=user, password=pwd, access_token=access_token)

st.title('TRADATANALYTIX')
strategy_select = st.sidebar.radio(
     "SELECT YOUR TRADING STRATEGY",
     ('Mean Reversion', 'Trend Following', 'Open Range Breakout'))

#st.sidebar.info("Upload Excel Sheet from ChartInk")


#uploaded_file = st.sidebar.file_uploader("Choose a file", type=["xlsx", "csv", "xls"])

left_column, middle_column, right_column = st.sidebar.beta_columns(3)
button1 = left_column.button("Trade Plan")
button2 = middle_column.button("Place Orders")
button3 = right_column.button("Cancel Orders")

#st.warning("Please Upload the Data")

expander = st.sidebar.beta_expander("HOW TO USE?")
expander.write("Go to: https://chartink.com/screener/copy-intraday-mean-reversion-85")
expander.write("Download Excel Sheet")
expander.write("Upload it and Click Generate")



m = st.markdown("""
<style>
div.stButton > button:first-child {
    color: white;
    background-color: SlateBlue;

}
</style>""", unsafe_allow_html=True)



#if uploaded_file is None:
#    st.warning("Please make sure that you enter the excel file and click generate")

data2 = pd.DataFrame()
def watchlist1():
    global data2
    
    df = pd.read_excel("C:\\Users\\pitan\\Downloads\\F&O_NSE.xlsx")
    

    #symbols = ['INFY.NS', 'BEL.NS']
    watchlist = []
    #watchlist.columns =['Name', 'Code', 'Age', 'Weight']
    #watchlist.columns = ['Stock', 'Entry Price', 'S/L', 'Qty', 'Max Day Loss']

    for S in df['SYMBOLS']:
    # Download Data
        data = yf.download(tickers=S, period='250d', interval='1d')
        data['sma_200'] = talib.SMA(data['Close'], timeperiod=200)
        data['RSI_2'] = talib.RSI(data['Close'], timeperiod = 2)
    
        df_today = data.tail(2)
        #df_today
    
        if ((df_today.Close[1] > df_today.Close[0]*1.03) & (df_today.RSI_2[1] > 50)  & (df_today.Close[1] > df_today.sma_200[1]) ):
            #symbol = s
            # Just added round(---, 1)
            close_watchlist = round(df_today.Close[1]*1.01, 1)
            sl_watchlist = round(df_today.Close[1]*1.01*1.03,1)
            quantity = round(60/(sl_watchlist - close_watchlist))
            max_dayloss = round((sl_watchlist - close_watchlist)*quantity)
            #print(s, "Go Short Tomorrow at:", df_today.Close[1]*1.01)
            #print(s, "Stop Loss is", df_today.Close[1]*1.01*1.03)
            watchlist.append([S, close_watchlist, sl_watchlist, quantity, max_dayloss])
            #print("Quantity", (60/((df_today.Close[1]*1.01*1.03)-(df_today.Close[1]*1.01))
    
    data2 = pd.DataFrame(watchlist, columns=['Stock', 'Entry Price', 'S/L', 'Qty', 'Max Day Loss'])
    data2 = data2.assign(Stock=[x[:-3] for x in data2['Stock']])
    
    
    return(data2)


    #watchlist
    #watchlist.columns = ['Stock', 'Entry Price', 'S/L', 'Qty', 'Max Day Loss']




    #for index, row in data2.iterrows():
    #stocknames = data2[row]['Stock']

if button1:

    with st.spinner("Takes exactly 2 minutes! We are getting you the best stocks to trade under Mean Reversion Strategy"):

        watchlist1()
        
        st.write(data2)
        maxday_loss = data2['Max Day Loss'].sum()
        n = data2['Stock'].count()
    

        left_column, right_column = st.beta_columns(2)

        with left_column:
            st.markdown("**Expected Number of trades**")
            st.markdown(f"<h1 style='text-align: center; color: white; background-color:SlateBlue'>{n}</h1>", unsafe_allow_html=True)

        with right_column:
            st.markdown("**Maximum Day Loss**")
            st.markdown(f"<h1 style='text-align: center; color: white;background-color:Tomato'>{round(maxday_loss)}</h1>", unsafe_allow_html=True)


if button2:
    with st.spinner("Hold on for 2 mins! We are placing the Order for you with your connected broker"):
        from PIL import Image
        image = Image.open("C:\\Users\\pitan\\Downloads\\Algo Trade Python\\algo_trade-3.png")

  
        watchlist1()
        for stock_name, price, quantity_trade in zip(data2['Stock'], data2['Entry Price'], data2['Qty']):
            print(
                alice.place_order(transaction_type=TransactionType.Sell,
                                  instrument=alice.get_instrument_by_symbol('NSE', stock_name),
                                  quantity=quantity_trade,
                                  order_type=OrderType.Limit,
                                  product_type=ProductType.Intraday,
                                  price=price,
                                  trigger_price=price,
                                  # trigger_price Here the trigger_price is taken as stop loss (provide stop loss in actual amount)
                                 stop_loss=None,
                                 square_off=None,
                                 trailing_sl=None,
                                 is_amo=True)
           )

        st.balloons()
        st.success("Trades Placed, check your ALICE BLUE order book")
        st.image(image, caption='DONE!')
        #st.image("C:\\Users\\pitan\\Downloads\\Green and Cream Minimal Refined Family Father's Day Flat Card.png", width = 500, caption = "Done")


if button3:        
    with st.spinner("Takes exactly 2 minutes! We are getting you the best stocks to trade under Mean Reversion Strategy"):
        watchlist1()
        st.write(data2)


    

    #print(
    #    alice.cancel_order()
    #)

