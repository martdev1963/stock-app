from flask import Flask, render_template, request
from datetime import datetime
import yfinance as yf

app = Flask(__name__)

def get_stock_data(symbol, timeframe='daily'):
    try:
        data = yf.download(
            tickers=symbol,
            period='1d' if timeframe == 'intraday' else '1mo',
            interval='5m' if timeframe == 'intraday' else '1d'
        )
        
        if data.empty:
            return {'symbol': symbol, 'data': [], 'meta': {'error': 'No data'}}
            
        return {
            'symbol': symbol,
            'data': [{
                'date': date.strftime('%Y-%m-%d %H:%M:%S'),
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close'],
                'volume': row['Volume']
            } for date, row in data.iterrows()],
            'meta': {'source': 'Yahoo Finance'}
        }
        
    except Exception as e:
        return {'symbol': symbol, 'data': [], 'meta': {'error': str(e)}}

@app.route('/', methods=['GET', 'POST'])
def index():
    symbol = request.form.get('symbol', 'AAPL').upper()
    timeframe = request.form.get('time_frame', 'daily')
    return render_template(
        'index.html',
        stock_data=get_stock_data(symbol, timeframe),
        symbol=symbol,
        time_frame=timeframe,
        current_year=datetime.now().year
    )

# Vercel handler remains the same
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