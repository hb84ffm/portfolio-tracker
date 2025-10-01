import streamlit as st
import time
from datetime import date, timedelta
import os
from asset_comparison.asset_comparison import AssetComparison

class MainPage:
    version = "0.0.1"
    copyright_year = date.today().strftime("%Y")
    mailto = "mail@mail.com?subject=Portfolio Tracker"

    def __init__(self):
        pass

    def mainpage_layout(self):
        """ Layout of mainpage with custom html """
        
        st.set_page_config(page_title="Portfolio Tracker", layout="wide", page_icon="")

        st.markdown("""<style>.block-container {padding-top: 0rem;}
                               header, .stAppHeader {padding-top: 0rem;
                                                     margin-top: 0rem;}
                        </style>""", unsafe_allow_html=True)
        
        st.markdown("""<style>div.stButton > button {border-radius: 100px !important;
                                                     font-size:1px !important;
                                                     margin-top: 0rem !important;
                                                     margin-bottom: 0rem !important;
                                                     padding-top: 0rem;
                                                     padding-bottom: 0rem;}
                        </style>""", unsafe_allow_html=True)

        st.markdown(f"""<div style="position: fixed; 
                                    left: 0; 
                                    right: 0; 
                                    bottom: 0; 
                                    width: 100%; 
                                    display: flex; 
                                    justify-content: space-between; 
                                    align-items: center; 
                                    padding: 0.5rem 1rem; 
                                    z-index: 9999; 
                                    background: black; 
                                    font-size: 0.6rem;">
                        <span style="color:#856C00;"> 
                            © Analytics Lab {MainPage.copyright_year}  
                        </span>
                        <span style="margin: 0 auto; 
                            color: #888; 
                            text-align: center;">
                            Version {MainPage.version}
                        </span>
                        <a href="mailto:{MainPage.mailto}" style="text-decoration: none;">
                            Contact
                        </a>
                        </div>""", unsafe_allow_html=True)

        pages = {"Analytics":     [st.Page("asset_comparison/asset_comparison.py", title="asset comparison")],
                "Recommendation": [st.Page("recommendation/recommendation.py", title="Name missing")]}

        pg = st.navigation(pages, position="top")
        pg.run()

if __name__=="__main__": # necessary to directly run the script!
    mainpage=MainPage()
    mainpage.mainpage_layout()
