# server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import json

app = Flask(__name__)
CORS(app)  # Pozwala na zapytania z innych domen (CORS)

# Konfiguracja bazy danych - takie same wartości jak w skrypcie do pobierania danych
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'portfolio_gpw'
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route('/api/indexes')
def get_indexes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM indexes')
    indexes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(indexes)


@app.route('/api/stocks')
def get_stocks():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT s.id, s.ticker, s.name, s.sector, s.index_name, 
               p.price, p.change_percent, p.volume, p.market_cap 
        FROM stocks s
        JOIN (
            SELECT ticker, MAX(timestamp) as max_timestamp
            FROM stock_prices
            GROUP BY ticker
        ) latest ON s.ticker = latest.ticker
        JOIN stock_prices p ON latest.ticker = p.ticker AND latest.max_timestamp = p.timestamp
        ORDER BY s.name
    ''')
    stocks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(stocks)


@app.route('/api/stock-details/<ticker>')
def get_stock_details(ticker):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Pobierz podstawowe dane o akcji
    cursor.execute('''
        SELECT s.id, s.ticker, s.name, s.sector, s.index_name, 
               p.price, p.change_percent, p.volume, p.market_cap, p.pe_ratio, p.dividend_yield, p.eps
        FROM stocks s
        JOIN (
            SELECT ticker, MAX(timestamp) as max_timestamp
            FROM stock_prices
            GROUP BY ticker
        ) latest ON s.ticker = latest.ticker
        JOIN stock_prices p ON latest.ticker = p.ticker AND latest.max_timestamp = p.timestamp
        WHERE s.ticker = %s
    ''', (ticker,))

    stock = cursor.fetchone()

    if not stock:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Nie znaleziono akcji'}), 404

    # Pobierz dane historyczne
    cursor.execute('''
        SELECT date, open_price, high_price, low_price, close_price, volume 
        FROM stock_historical 
        WHERE ticker = %s 
        ORDER BY date
    ''', (ticker,))

    historical_data = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({
        'stock': stock,
        'historical_data': historical_data
    })


@app.route('/api/tickers')
def get_tickers():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM ticker_watchlist ORDER BY ticker')
    tickers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tickers)


@app.route('/api/check-ticker/<ticker>')
def check_ticker(ticker):
    # Poprawna składnia Pythona (zamiast JavaScript)
    suggested_full_ticker = ticker if '.' in ticker else f"{ticker}.WA"
    return jsonify({
        'exists': True,
        'suggestedFullTicker': suggested_full_ticker
    })


@app.route('/api/tickers', methods=['POST'])
def add_ticker():
    data = request.json
    ticker = data.get('ticker')
    full_ticker = data.get('fullTicker')

    if not ticker or not full_ticker:
        return jsonify({'error': 'Wymagane pola: ticker i fullTicker'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Sprawdź czy ticker już istnieje
        cursor.execute('SELECT * FROM ticker_watchlist WHERE ticker = %s', (ticker,))
        existing = cursor.fetchone()

        if existing:
            # Jeśli istnieje, ale jest nieaktywny - aktywuj go
            cursor.execute('UPDATE ticker_watchlist SET is_active = TRUE, full_ticker = %s WHERE ticker = %s',
                           (full_ticker, ticker))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Ticker został ponownie aktywowany', 'ticker': ticker})

        # Dodaj nowy ticker
        cursor.execute(
            'INSERT INTO ticker_watchlist (ticker, full_ticker) VALUES (%s, %s)',
            (ticker, full_ticker)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Ticker dodany pomyślnie', 'ticker': ticker}), 201

    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/tickers/<ticker>', methods=['DELETE'])
def delete_ticker(ticker):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Sprawdź czy ticker istnieje
        cursor.execute('SELECT * FROM ticker_watchlist WHERE ticker = %s', (ticker,))
        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Ticker nie istnieje'}), 404

        # Ustaw ticker jako nieaktywny zamiast go usuwać
        cursor.execute('UPDATE ticker_watchlist SET is_active = FALSE WHERE ticker = %s', (ticker,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Ticker został usunięty z śledzenia', 'ticker': ticker})

    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)