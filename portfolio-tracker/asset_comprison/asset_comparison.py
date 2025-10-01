# asset_comparison.py
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import os
import time
from datetime import date, timedelta
import json
from utils.utils import ExitButton

class AssetComparison:
    ticker_path="/Users/hb/Desktop/portfolio_tracker/ticker_names/ticker_names.json"
    with open(ticker_path, "r", encoding="utf-8") as f:
        ticker_names=json.load(f)

    today = date.today()
    one_year_ago = today - timedelta(days=365)
    select_price=["Open", "Close", "High", "Low"] # Close Adj missing

    def __init__(self):
            self.start_date = AssetComparison.one_year_ago
            self.end_date = AssetComparison.today
            self.price_type = AssetComparison.select_price[0]
            self.ticker_input_1 = None 
            self.ticker_input_2 = None
            self.risk_free_rate_1 = None
            self.risk_free_rate_2 = None
            self.metrics=None
            self.plot_metrics=None

    def format_label(self,ticker):
        """ Method to assign tickers """
        return f"{ticker} ({AssetComparison.ticker_names.get(ticker, 'Unknown')})"

    def open_dialog(self):
        """Display pop up for user to add/change values to/in db """
        @st.dialog("Parameters",width="small")
        def pop_up_form():
            """ Dialog method to create the form for user input """
            with st.form("parameter_input"):
                ticker_input_1 = st.selectbox("Asset 1", 
                                            list(AssetComparison.ticker_names.keys()), 
                                            index=0, 
                                            help="Insert ticker of first security",
                                            format_func=self.format_label)
                
                ticker_input_2 = st.selectbox("Asset 2",
                                            list(AssetComparison.ticker_names.keys()),
                                            index=len(AssetComparison.ticker_names)-1,
                                            help="Insert ticker of second security", 
                                            format_func=self.format_label)
                
                start_date = st.date_input("Start date",
                                        value=AssetComparison.one_year_ago,
                                        help="Select start date")
                
                end_date = st.date_input("End date", 
                                        value=AssetComparison.today,
                                        help="Select end date")
                
                price_type = st.selectbox("Price type",
                                        options=AssetComparison.select_price,
                                        help="Select price type. Only Adj Close corrects for dividends & stock splits")
                
                risk_free_rate_1 = st.number_input("Risk free rate (asset 1)",
                                                value=0.0,
                                                step=0.0001,
                                                format="%.5f",
                                                placeholder="",
                                                help="Type average local government bond yield (US Treasury, Bund, etc.) over the whole period as decimal")
                
                risk_free_rate_2 = st.number_input("Risk free rate (asset 2)",
                                                value=0.0,
                                                step=0.0001,
                                                format="%.5f", 
                                                placeholder="", 
                                                help="Type average local government bond yield (US Treasury, Bund, etc.) over the whole period as decimal")

                run = st.form_submit_button("Run",type="secondary",use_container_width=True)
                
                if run: # must save user input in session
                    st.session_state["user_input"]={"ticker_input_1" : ticker_input_1,
                                                        "ticker_input_2" : ticker_input_2,
                                                        "start_date" : start_date,
                                                        "end_date" : end_date,
                                                        "price_type" : price_type,
                                                        "risk_free_rate_1" : risk_free_rate_1,
                                                        "risk_free_rate_2" : risk_free_rate_2}
                    st.session_state["run_analysis"]=True 
                    st.rerun() # must rerun app to exit pop up, but user values are saved!
        pop_up_form()
        
    def calculate_metrics(self):
        tickers = [self.ticker_input_1, self.ticker_input_2]
        risk_free_rates=[self.risk_free_rate_1,self.risk_free_rate_2]
        results_1 = []
        results_2 = []

        for i in range(len(tickers)):
            ticker_object = yf.Ticker(tickers[i])
            name = ticker_object.info.get('shortName', tickers[i])
            ccy = ticker_object.info.get('currency', '')
            asset_all = ticker_object.history(start=self.start_date, end=self.end_date, auto_adjust=False).reset_index()
            asset_all['Date'] = asset_all['Date'].dt.date
            asset = asset_all[["Date", self.price_type]].copy()
            asset["Ccy"] = ccy
            asset["Asset"] = tickers[i]

            returns = asset[self.price_type].pct_change().dropna()
            geo_mean_return = (np.prod(1 + returns)) - 1
            stddev_return = returns.std() * np.sqrt(len(returns))
            dividend = ticker_object.dividends.loc[pd.Timestamp(self.start_date).tz_localize('UTC'):
                                                pd.Timestamp(self.end_date).tz_localize('UTC')]
            dividend_yield = dividend.sum() / asset[self.price_type].iloc[0]
            pe = ticker_object.info.get('trailingPE', np.nan)
            risk_free_rate = risk_free_rates[i]

            if risk_free_rate is None:
                sharpe_ratio=np.nan
            else:
                sharpe_ratio = (geo_mean_return - risk_free_rate) / stddev_return    

            metric_list = [ticker_object, name, ccy, asset, returns, geo_mean_return,stddev_return, dividend, dividend_yield, pe, sharpe_ratio, asset_all]

            if i == 0:
                results_1 = metric_list
            else:
                results_2 = metric_list

        ticker_1, name_1, ccy_1, asset_1, return_1, geo_mean_return_1, stddev_return_1, dividend_1, dividend_yield_1, pe_1, sharpe_ratio_1, asset_all_1 = results_1
        ticker_2, name_2, ccy_2, asset_2, return_2, geo_mean_return_2, stddev_return_2, dividend_2, dividend_yield_2, pe_2, sharpe_ratio_2,asset_all_2 = results_2

        # correlation
        correlation = return_1.corr(return_2)

        if ccy_1 != ccy_2: # currencies dont match -> run fx conversion
            fx_ticker = f"{ccy_2}{ccy_1}=X"
            fx_rate = yf.Ticker(fx_ticker).history(start=self.start_date, end=self.end_date).reset_index()
            fx_rate['Date'] = fx_rate['Date'].dt.date
            asset_2 = asset_2.merge(fx_rate[['Date', self.price_type]], on="Date", how="left")
            asset_2.columns = [asset_2.columns[0], self.price_type, asset_2.columns[2], asset_2.columns[3], fx_ticker]
            asset_2[f"{self.price_type}_{ccy_1}"] = asset_2[self.price_type] * asset_2[fx_ticker]
            assets = pd.DataFrame({f"{self.ticker_names[self.ticker_input_1]}": asset_1[self.price_type], 
                                   f"{self.ticker_names[self.ticker_input_2]}": asset_2[f"{self.price_type}_{ccy_1}"], "Date": asset_1["Date"]})
        else: # currencies match -> no fx conversion needed
            fx_ticker=None
            fx_rate=1
            assets = pd.DataFrame({f"{self.ticker_names[self.ticker_input_1]}": asset_1[self.price_type], 
                                   f"{self.ticker_names[self.ticker_input_2]}": asset_2[self.price_type], "Date": asset_1["Date"]})

        return ticker_1, name_1, ccy_1, asset_1, return_1, geo_mean_return_1, stddev_return_1, dividend_1, dividend_yield_1, pe_1, asset_all_1,\
               ticker_2, name_2, ccy_2, asset_2, return_2, geo_mean_return_2, stddev_return_2, dividend_2, dividend_yield_2, pe_2, asset_all_2,\
               correlation, sharpe_ratio_1, sharpe_ratio_2, fx_ticker, fx_rate, assets    

    def plot_charts_metrics(self):
        """ Method to place the calculated metrics into the page """
        st.text(f'Period ┃ {self.start_date.strftime("%d/%m/%Y")} - {self.end_date.strftime("%d/%m/%Y")}')

        html_template = """<div style="width:100%; height:100px; text-align:center; display:flex; 
                                   flex-direction:column; align-items:center; justify-content:center; 
                                   font-size: 25px; font-weight:bold; background-color:black; color:{color};">
                            <div style="font-size: 11px; margin-bottom: 3px;">{label}</div>
                            <div>{value}</div>
                        </div>"""
        
        col1, col2, col3, col4, col5, col6, col7,col8 = st.columns(8)   
# TO DO: For loop schreiben um das zu vereinfachen 
        with col1:
            st.markdown(html_template.format(label="Asset",value=AssetComparison.ticker_names[self.ticker_input_1], color="white"), unsafe_allow_html=True)
        with col2:
            st.markdown(html_template.format(label="Business days (period)", value=len(self.return_1), color="white"), unsafe_allow_html=True)
        with col3:
            st.markdown(html_template.format(label="Return (period)", value=f"{self.geo_mean_return_1 * 100:.2f} %", color="#107A00"), unsafe_allow_html=True)
        with col4:
            st.markdown(html_template.format(label="Risk (period)", value=f"{self.stddev_return_1 * 100:.2f} %", color="#E10000"), unsafe_allow_html=True)
        with col5:
            st.markdown(html_template.format(label="Dividend yield (period)", value=f"{self.dividend_yield_1 * 100:.2f} %", color="white"), unsafe_allow_html=True) 
        with col6:
            st.markdown(html_template.format(label="P/E ratio (latest)", value=f"{self.pe_1:.2f}", color="white"), unsafe_allow_html=True)
        with col7:
            st.markdown(html_template.format(label="Sharpe ratio (period)", value=f"{self.sharpe_ratio_1:.2f}" , color="white"), unsafe_allow_html=True)
        with col8:        
            st.markdown(html_template.format(label="Correlation (period)", value=f"{self.correlation:.2f}", color="white"), unsafe_allow_html=True)

        col8, col9, col10, col11, col12, col13, col14, col15 = st.columns(8)
        with col8:
            st.markdown(html_template.format(label="", value=AssetComparison.ticker_names[self.ticker_input_2], color="white"), unsafe_allow_html=True)
        with col9:
            st.markdown(html_template.format(label="", value=len(self.return_2), color="white"), unsafe_allow_html=True)
        with col10:
            st.markdown(html_template.format(label="", value=f"{self.geo_mean_return_2 * 100:.2f} %", color="#107A00"), unsafe_allow_html=True)
        with col11:
            st.markdown(html_template.format(label="", value=f"{self.stddev_return_2 * 100:.2f} %", color="#E10000"), unsafe_allow_html=True)
        with col12:
            st.markdown(html_template.format(label="", value=f"{self.dividend_yield_2 * 100:.2f} %", color="white"), unsafe_allow_html=True)
        with col13:
            st.markdown(html_template.format(label="", value=f"{self.pe_2:.2f}", color="white"), unsafe_allow_html=True)
        with col14:
            st.markdown(html_template.format(label="", value=f"{self.sharpe_ratio_2:.2f}", color="white"), unsafe_allow_html=True)
        with col15:
            st.markdown(html_template.format(label="", value=f"{self.correlation:.2f}", color="white"), unsafe_allow_html=True)
      
        # used only for charts !
        traded_volume = pd.DataFrame({f"{self.ticker_names[self.ticker_input_1]}": self.asset_all_1["Volume"],
                                    f"{self.ticker_names[self.ticker_input_2]}": self.asset_all_2["Volume"],
                                    "Date": self.asset_all_1["Date"]})
        # used only for charts !
        returns = pd.DataFrame({f"{self.ticker_names[self.ticker_input_1]}": self.return_1 * 100,
                                f"{self.ticker_names[self.ticker_input_2]}": self.return_2 * 100,
                                "Date": self.asset_1["Date"][1:]}) 

        # charts - asset & return trajectory
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown(f'<div style="text-align: center; font-weight: bold; font-size: 20px;">Prices ({self.ccy_1})</div>', unsafe_allow_html=True)
            st.line_chart(self.assets.round(2), x="Date")
        with col_chart2:
            st.markdown('<div style="text-align: center; font-weight: bold; font-size: 20px;">Returns (%)</div>', unsafe_allow_html=True)
            st.line_chart(returns.round(4), x="Date")

        # charts - risk/return bar chart
        bar_df = pd.DataFrame({"Risk": [self.stddev_return_1 * 100, self.stddev_return_2 * 100],
                            "Return": [self.geo_mean_return_1 * 100, self.geo_mean_return_2 * 100]}, 
                            index=[self.ticker_names[self.ticker_input_1], self.ticker_names[self.ticker_input_2]])

        col_bar1, col_bar2 = st.columns(2)
        with col_bar1:
            st.markdown('<div style="text-align: center; font-weight: bold; font-size: 20px;">Traded volume</div>', unsafe_allow_html=True)
            st.line_chart(traded_volume, x="Date")
        with col_bar2:
            st.markdown('<div style="text-align: center; font-weight: bold; font-size: 20px;">Risk VS Return (%)</div>', unsafe_allow_html=True)
            st.bar_chart(bar_df, color=["#E10000", "#107A00"], stack=False, horizontal=False, use_container_width=True)

    def page_layout(self):
        """ Defines the base layout of page & orchestartes the flow """
         
        col1,empty,col2,col3=st.columns([0.7,0.1,0.1,0.1], vertical_alignment="bottom")
        with col1:
            st.title("Asset comparison", anchor=False)
        with empty:
            st.empty()
        with col2: 
            analyse=st.button("Analyse", type="secondary") # a boolean (True/False) to later trigger the pop up
        with col3:
            ExitButton.exit_button()

        if analyse: # button to open dialog
            self.open_dialog()

        if "user_input" in st.session_state:
            self.ticker_input_1=st.session_state["user_input"]["ticker_input_1"]
            self.ticker_input_2=st.session_state["user_input"]["ticker_input_2"]
            self.start_date=st.session_state["user_input"]["start_date"]
            self.end_date=st.session_state["user_input"]["end_date"]
            self.price_type=st.session_state["user_input"]["price_type"]
            self.risk_free_rate_1=st.session_state["user_input"]["risk_free_rate_1"]
            self.risk_free_rate_2=st.session_state["user_input"]["risk_free_rate_2"]

            ticker_1, name_1, ccy_1, asset_1, return_1, geo_mean_return_1, stddev_return_1, dividend_1, dividend_yield_1, pe_1, asset_all_1, \
            ticker_2, name_2, ccy_2, asset_2, return_2, geo_mean_return_2, stddev_return_2, dividend_2, dividend_yield_2, pe_2, asset_all_2, \
            correlation, sharpe_ratio_1, sharpe_ratio_2, fx_ticker, fx_rate, assets = self.calculate_metrics()

            self.return_1 = return_1
            self.ticker_1=ticker_1
            self.name_1=name_1
            self.ccy_1=ccy_1
            self.geo_mean_return_1 = geo_mean_return_1
            self.stddev_return_1 = stddev_return_1
            self.dividend_1 = dividend_1
            self.dividend_yield_1 = dividend_yield_1
            self.pe_1 = pe_1
            self.asset_all_1=asset_all_1
            self.sharpe_ratio_1 = sharpe_ratio_1
            self.asset_1=asset_1

            self.return_2 = return_2
            self.ticker_2=ticker_2
            self.name_2=name_2
            self.ccy_2=ccy_2
            self.geo_mean_return_2 = geo_mean_return_2
            self.stddev_return_2 = stddev_return_2
            self.dividend_2 = dividend_2
            self.dividend_yield_2 = dividend_yield_2
            self.pe_2 = pe_2
            self.asset_all_2=asset_all_2
            self.asset_2=asset_2            
            self.sharpe_ratio_2 = sharpe_ratio_2

            self.correlation = correlation
            self.fx_ticker = fx_ticker
            self.fx_rate = fx_rate
            self.assets = assets
            
            self.plot_charts_metrics()

if __name__=="__main__": # Needed since we use the st.navigation() so every page must be run as a script
    asset_comparison=AssetComparison()
    asset_comparison.page_layout()
