from flask import Flask, render_template, request
import os
from datetime import datetime
import yfinance as yf

app = Flask(__name__)

def get_stock_data(symbol, timeframe='daily'):
    try:
        if timeframe == 'intraday':
            data = yf.download(tickers=symbol, period='1d', interval='5m')
        else:
            data = yf.download(tickers=symbol, period='1mo')
        
        if data.empty:
            return {
                'symbol': symbol,
                'data': [],
                'meta': {'error': 'No data available for this symbol'}
            }
            
        processed_data = []
        for date, row in data.iterrows():
            processed_data.append({
                'date': date.strftime('%Y-%m-%d %H:%M:%S'),
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume']
            })
            
        return {
            'symbol': symbol,
            'data': processed_data,
            'meta': {'source': 'Yahoo Finance'}
        }
        
    except Exception as e:
        return {
            'symbol': symbol,
            'data': [],
            'meta': {'error': str(e)}
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    symbol = request.form.get('symbol', 'AAPL').upper()
    timeframe = request.form.get('time_frame', 'daily')
    stock_data = get_stock_data(symbol, timeframe)
    return render_template('index.html',
                         stock_data=stock_data,
                         symbol=symbol,
                         time_frame=timeframe,
                         current_year=datetime.now().year)

# Vercel requires this handler
def vercel_handler(request):
    with app.app_context():
        response = app.full_dispatch_request()
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }

if __name__ == '__main__':
    app.run(debug=True)