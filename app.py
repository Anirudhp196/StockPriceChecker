from flask import Flask, render_template, request, redirect, url_for
from markupsafe import Markup
import os
from dotenv import load_dotenv
import requests
from datetime import datetime as dt

from io import StringIO
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
matplotlib.use('Agg')

load_dotenv()
AV_KEY = os.getenv("AV_KEY")

function_mapping = {
   "TIME_SERIES_DAILY": "Time Series (Daily)",
   "TIME_SERIES_WEEKLY": "Weekly Time Series",
   "TIME_SERIES_MONTHLY": "Monthly Time Series"
}

app = Flask(__name__)

@app.route('/')
def index():
    if "error" in request.args:
        return render_template('index.html', error=request.args['error'])
    return render_template("index.html")


@app.route('/info', methods = ['GET', 'POST'])
def info():
    if(request.method == 'GET'):
        return redirect('/')
    form_data = request.form
    print(form_data)
    symbol = form_data["symbol"]
    interval = form_data["interval"]
    print(symbol, interval)

    overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={AV_KEY}"
    company_overview = requests.get(overview_url).json()

    if 'Name' not in company_overview:
        return redirect(url_for('index', error="Invalid ticker symbol"))

    company_name = company_overview["Name"]

    url = f"https://www.alphavantage.co/query?function={interval}&symbol={symbol}&apikey={AV_KEY}"
    stock_data = requests.get(url).json()
    func_key = function_mapping[interval]
    time_series_data = stock_data[func_key]

    dates = []
    prices = []

    for k, v in time_series_data.items():
        formatted_date = dt.strptime(k, "%Y-%m-%d").date()
        dates.append(k)
        prices.append(float(v['2. high']))

    dates.reverse() #To make the oldest date first
    prices.reverse() #TO make the oldest price first

    graph = get_graph(dates, prices, company_name)

    return render_template("info.html", info={
        "company name": company_name,
        "symbol": symbol,
        "graph": Markup(graph)
    })

def get_graph(dates, prices, company_name):
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.xaxis.set_tick_params(rotation=45)
    ax.set_title(f"Stock Price of {company_name}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Price (USD)")
    ax.plot(dates, prices)

    buf = StringIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)

    return buf.getvalue()

if __name__ == '__main__':
    app.run(debug=True)


