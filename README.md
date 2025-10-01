# portfolio-tracker

A Python package to track liquid assets from yfinance across several KPIs & KRIs. 

### FEATURES
- Side by side comparison of two (liquid) assets with selectiona cross:
  - stocks:
    - US, JP, FR, DE, SU
  - crypto:
    - BTC, ETH, SOL
  - ETFs:
    - US
- UI with follwoing features:
  - Tab "asset comparison" to benchmark two assets (soon to follow other tabs with more functionality)
  - Variable start_date, end_date selection
  - Price type selection by OPEN, CLOSE, HIGH, LOW
  - Risk free rate as input field for both selected assets (if given) to calcualte Sharpe ratio
  - Analyse button to open a pop up for user entry
  - Exit button to quit the app
- Analytics with follwoing features:
  - KPIs:
    - Return of both assets
    - Dividend yield of both assets (if given)
    - Price earnings ratio of both assets
    - Sharpe ratio of both assets (if risk free rate is provided)
  - KRIs:
    - Risk (volatility based on selected timespan from start_date, end_date)
    - Correlation of both assets
  - Charts:
    - Comparison of price trajectory for both assets (in ccy of first asset!)
    - Comparison of return trajectory for both assets (in %)
    - Comparison of volume trajectory for both assets (in traded units)
    - Comparison of risk/return profile for both assets (in %)
- JSON file with latest tickers and friendly names for identification

### REQUIREMENTS - WEITER !
- Python 3.11+ (tested with 3.11.9)
- Required dependencies (see requirements.txt for details):<br>
    streamlit==1.24.1<br>
    pandas==2.0.3<br>
    numpy==1.25.2<br>
    yfinance==0.2.25<br>

### INSTALLATION
1. Clone the repository:<br>
       git clone https://github.com/hb84ffm/portfolio-tracker.git<br>
       cd portfolio-tracker<br>

2. Create & activate your virtual environment:<br>
       python3 -m venv venv<br>
       source venv/bin/activate      # On Mac/Linux<br>
       venv\Scripts\activate         # On Windows

3. Install dependencies:<br>
       pip install -r requirements.txt

### USAGE
1. Open the app via termins/zsh by command streamlit run "path_to_app/app.py" 

2. Press "Analyse" button to select assets & specify paramneters, then press "Run"
3. 
### PACKAGE STRUCTURE

<pre>portfolio_tracker/
├─── __init__.py
├─── main.py                        # Orchestrates all modules
├─── streamlit./                    # Hidden folder with config.toml file  
     ├─── config.toml               # config.toml for app layout & format
├─── asset_comparison/
     ├─── __init__.py
     ├─── asset_comparison.py       # Module to pull data and run analytics
├─── utils/
     ├─── __init__.py
     ├─── utils.py                  # Module with utils (exit button, logout) needed across all other 
├─── ticker_names/                        
     ├─── ticker_names.json         # JSON file with ticker names (can be adjusted if needed!)

### EXAMPLE WORKFLOW
See provided Jupyter notebook [example](https://github.com/) for explanation.

### AUTHOR
For questions or feedback reach out to me via: [GitHub](https://github.com/hb84ffm).
