import streamlit as st
import numpy as np
import pandas as pd


user = st.secrets["user"]
pwd = st.secrets["pwd"]
secret = st.secrets["secret"]
app = st.secrets["app"]

import logging
logging.basicConfig(level=logging.DEBUG)

from alice_blue import *

access_token = AliceBlue.login_and_get_access_token(username=user,
                                                    password=pwd,
                                                    twoFA='pit',
                                                    api_secret=secret,
                                                    app_id=app)

alice = AliceBlue(username=user, password=pwd, access_token=access_token)

st.title('WATCHLIST')

st.sidebar.info("Upload Excel Sheet from ChartInk")

uploaded_file = st.sidebar.file_uploader("Choose a file", type=["xlsx", "csv", "xls"])

left_column, middle_column, right_column = st.sidebar.beta_columns(3)
button1 = left_column.button("Trade Plan")
button2 = middle_column.button("Place Orders")
button3 = right_column.button("Cancel Orders")

#st.warning("Please Upload the Data")

expander = st.sidebar.beta_expander("HOW TO USE?")
expander.write("Go to: https://chartink.com/screener/copy-intraday-mean-reversion-85")
expander.write("Download Excel Sheet")
expander.write("Upload it and Click Generate")

if uploaded_file is None:
    st.warning("Please make sure that you enter the excel file and click generate")


else:

    df = pd.read_excel(uploaded_file, header=1)

    data2 = pd.DataFrame()

    df['Stock Pick'] = df['Symbol']
    df['Short Price'] = df['Price'] + (1/100*df['Price'])
    df['Stop Loss'] = df['Short Price'] + (3/100*df['Short Price'])
    df['Quantity'] = round(60/(df['Stop Loss'] - df['Short Price']))
    df['Max Loss'] = df['Quantity']*(df['Stop Loss'] - df['Short Price'])

    data2['Stock'] = df['Stock Pick']
    data2['Entry Price'] = df['Short Price']
    data2['S/L'] = df['Stop Loss']
    data2['Qty'] = df['Quantity']
    data2['Max Day Loss'] = df['Max Loss']
    if button1:
        st.write(data2)

    maxday_loss = data2['Max Day Loss'].sum()

    left_column, right_column = st.beta_columns(2)

    if button1:
        #left_column.subheader('Estimated Capital Required')
        left_column.info("Maximum Loss: " + "Rs:")
        #left_column.subheader('Maximum Loss')
        right_column.warning(round(maxday_loss))

    if button2:
        print(
            alice.place_order(transaction_type=TransactionType.Sell,
                              instrument=alice.get_instrument_by_symbol('NSE', 'TATAPOWER'),
                              quantity=1,
                              order_type=OrderType.Limit,
                              product_type=ProductType.CoverOrder,
                              price=127.20,
                              trigger_price=127.25,
                              # trigger_price Here the trigger_price is taken as stop loss (provide stop loss in actual amount)
                              stop_loss=131.00,
                              square_off=None,
                              trailing_sl=None,
                              is_amo=True)
           )


    if button3:
        print(
            alice.cancel_order()
        )
