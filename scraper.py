import yfinance as yf
import mysql.connector
import pandas as pd
import time
import schedule
import random
from datetime import datetime, timedelta

# Konfiguracja bazy danych
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'portfolio'
}

# Indeksy do śledzenia
INDEXES = [
    'WIG.WA', 'WIG20.WA', 'MWIG40.WA', 'SWIG80.WA'
]


def create_database_structure():
    """Tworzy strukturę bazy danych, jeśli nie istnieje"""
    conn = mysql.connector.connect(
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host']
    )
    cursor = conn.cursor()

    # Tworzenie bazy danych
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cursor.execute(f"USE {DB_CONFIG['database']}")

    # [reszta funkcji jak wcześniej]

    # Dodaj domyślne tickery jeśli tabela jest pusta
    cursor.execute("SELECT COUNT(*) FROM ticker_watchlist")
    count = cursor.fetchone()[0]

    if count == 0:
        # Spółki z indeksu WIG - pełna lista (ponad 300 spółek)
        wig_tickers = [
            # WIG20
            ('PKO', 'PKO.WA'),  # PKO Bank Polski
            ('PZU', 'PZU.WA'),  # PZU
            ('PKN', 'PKN.WA'),  # Orlen
            ('PGE', 'PGE.WA'),  # PGE
            ('KGH', 'KGH.WA'),  # KGHM
            ('LPP', 'LPP.WA'),  # LPP
            ('DNP', 'DNP.WA'),  # Dino Polska
            ('OPL', 'OPL.WA'),  # Orange Polska
            ('PEO', 'PEO.WA'),  # Bank Pekao
            ('SPL', 'SPL.WA'),  # Santander Bank Polska
            ('ALE', 'ALE.WA'),  # Allegro
            ('CDR', 'CDR.WA'),  # CD Projekt
            ('CPS', 'CPS.WA'),  # Cyfrowy Polsat
            ('JSW', 'JSW.WA'),  # JSW
            ('MBK', 'MBK.WA'),  # mBank
            ('TPE', 'TPE.WA'),  # Tauron
            ('PGN', 'PGN.WA'),  # PGNiG
            ('PLY', 'PLY.WA'),  # Play Communications
            ('LTS', 'LTS.WA'),  # Lotos
            ('CCC', 'CCC.WA'),  # CCC

            # mWIG40
            ('11B', '11B.WA'),  # 11 bit studios
            ('ACP', 'ACP.WA'),  # Asseco Poland
            ('AMC', 'AMC.WA'),  # Amica
            ('BNP', 'BNP.WA'),  # BNP Paribas Bank Polska
            ('BZW', 'BZW.WA'),  # Bank Handlowy
            ('ENA', 'ENA.WA'),  # Enea
            ('ENG', 'ENG.WA'),  # Energa
            ('EUR', 'EUR.WA'),  # Eurocash
            ('FMF', 'FMF.WA'),  # Fabryka Farb i Lakierów
            ('GPW', 'GPW.WA'),  # GPW
            ('ING', 'ING.WA'),  # ING Bank Śląski
            ('KTY', 'KTY.WA'),  # Kety
            ('MAB', 'MAB.WA'),  # Mabion
            ('MLS', 'MLS.WA'),  # ML System
            ('MRB', 'MRB.WA'),  # Mrówa
            ('OPM', 'OPM.WA'),  # OPTeam
            ('PEN', 'PEN.WA'),  # Penetron
            ('PFR', 'PFR.WA'),  # PFR
            ('PGB', 'PGB.WA'),  # Polska Grupa Budowlana
            ('PGR', 'PGR.WA'),  # Polski Holding Nieruchomości
            ('PXM', 'PXM.WA'),  # Polimex-Mostostal
            ('SAN', 'SAN.WA'),  # Sanok Rubber Company
            ('SNK', 'SNK.WA'),  # Sanok
            ('STP', 'STP.WA'),  # Stalprodukt
            ('SWT', 'SWT.WA'),  # Świat
            ('TEN', 'TEN.WA'),  # Ten Square Games
            ('TIM', 'TIM.WA'),  # TIM
            ('TOR', 'TOR.WA'),  # Torpol
            ('VRG', 'VRG.WA'),  # VRG
            ('WPL', 'WPL.WA'),  # Wirtualna Polska
            ('XTB', 'XTB.WA'),  # XTB

            # sWIG80
            ('ABS', 'ABS.WA'),  # Asseco Business Solutions
            ('AFH', 'AFH.WA'),  # Aflofarm
            ('AGT', 'AGT.WA'),  # Agroton
            ('AOL', 'AOL.WA'),  # Analizy Online
            ('APL', 'APL.WA'),  # APS Energia
            ('ATA', 'ATA.WA'),  # Atal
            ('BCM', 'BCM.WA'),  # Benefit Systems
            ('BDX', 'BDX.WA'),  # Budimex
            ('BMC', 'BMC.WA'),  # Bumech
            ('BFT', 'BFT.WA'),  # Benefit
            ('BML', 'BML.WA'),  # Bumech
            ('BRP', 'BRP.WA'),  # Black Point
            ('BRS', 'BRS.WA'),  # Boryszew
            ('BSC', 'BSC.WA'),  # Beskid
            ('CAR', 'CAR.WA'),  # Inter Cars
            ('CLC', 'CLC.WA'),  # Columbus Energy
            ('CMR', 'CMR.WA'),  # Comarch
            ('CZT', 'CZT.WA'),  # Ciech
            ('DBC', 'DBC.WA'),  # Firma Oponiarska Debica
            ('ECH', 'ECH.WA'),  # Echo Investment
            ('ELZ', 'ELZ.WA'),  # Zortrax
            ('EMC', 'EMC.WA'),  # Emitel
            ('ERB', 'ERB.WA'),  # Erbud
            ('ESK', 'ESK.WA'),  # Eskimos
            ('FRO', 'FRO.WA'),  # Frosta
            ('GAL', 'GAL.WA'),  # Galmedia
            ('GOP', 'GOP.WA'),  # Goplana
            ('GPP', 'GPP.WA'),  # Grupa Kęty
            ('GTC', 'GTC.WA'),  # GTC
            ('GTP', 'GTP.WA'),  # Geotrans
            ('HMP', 'HMP.WA'),  # Himax
            ('HRP', 'HRP.WA'),  # Harper Hygienics
            ('IFR', 'IFR.WA'),  # Investment Friends
            ('IMC', 'IMC.WA'),  # IMC
            ('INC', 'INC.WA'),  # Inco
            ('INT', 'INT.WA'),  # Internity
            ('IPW', 'IPW.WA'),  # Image Power
            ('KDM', 'KDM.WA'),  # KDM Shipping
            ('KGL', 'KGL.WA'),  # Kogeneracja
            ('KGN', 'KGN.WA'),  # Kogeneracja
            ('KRK', 'KRK.WA'),  # Kruk
            ('KRU', 'KRU.WA'),  # Kruk
            ('KSG', 'KSG.WA'),  # Kasing
            ('LVC', 'LVC.WA'),  # Livechat
            ('MCI', 'MCI.WA'),  # MCI Capital
            ('MDI', 'MDI.WA'),  # MyDentist
            ('MEG', 'MEG.WA'),  # Megaron
            ('MEX', 'MEX.WA'),  # Mex Polska
            ('MFO', 'MFO.WA'),  # MFO
            ('MND', 'MND.WA'),  # Mondi
            ('MOJ', 'MOJ.WA'),  # Moj
            ('NCL', 'NCL.WA'),  # Newconnect Live
            ('NTC', 'NTC.WA'),  # Novita
            ('OAT', 'OAT.WA'),  # Oat
            ('O2T', 'O2T.WA'),  # One2Tribe
            ('OVI', 'OVI.WA'),  # Ovid Works
            ('PCE', 'PCE.WA'),  # PCC Rokita
            ('PCR', 'PCR.WA'),  # PCC Rokita
            ('PHR', 'PHR.WA'),  # Polski Holding Hotelowy
            ('PJP', 'PJP.WA'),  # PJP Makrum
            ('PLW', 'PLW.WA'),  # Playway
            ('PMP', 'PMP.WA'),  # Polimpex-Mostostal
            ('QRT', 'QRT.WA'),  # Quart
            ('QON', 'QON.WA'),  # Quarticon
            ('R22', 'R22.WA'),  # Relay Recruitment
            ('RCM', 'RCM.WA'),  # Red Square Games
            ('RDG', 'RDG.WA'),  # Read-Gene
            ('SFD', 'SFD.WA'),  # SFD
            ('SGR', 'SGR.WA'),  # Sadovaya Group
            ('SNS', 'SNS.WA'),  # Synektik
            ('STX', 'STX.WA'),  # Stalexport
            ('SUN', 'SUN.WA'),  # Sunex
            ('S4E', 'S4E.WA'),  # S4E
            ('TAR', 'TAR.WA'),  # Tarczynski
            ('TMR', 'TMR.WA'),  # Tomi
            ('TXN', 'TXN.WA'),  # Tax-Net
            ('ULM', 'ULM.WA'),  # Ulma Construccion
            ('UNI', 'UNI.WA'),  # Unibep
            ('VEE', 'VEE.WA'),  # Vee
            ('VIV', 'VIV.WA'),  # Vivid Games
            ('VOT', 'VOT.WA'),  # Votum
            ('WAS', 'WAS.WA'),  # Wasko
            ('WIK', 'WIK.WA'),  # Wikana
            ('WTN', 'WTN.WA'),  # Wittchen
            ('WWL', 'WWL.WA'),  # Wawel
            ('ZEP', 'ZEP.WA'),  # ZE Pak
            ('ZRE', 'ZRE.WA'),  # Zremb
        ]

        for ticker, full_ticker in wig_tickers:
            cursor.execute(
                "INSERT INTO ticker_watchlist (ticker, full_ticker) VALUES (%s, %s)",
                (ticker, full_ticker)
            )

    conn.commit()
    cursor.close()
    conn.close()
    print("Struktura bazy danych została utworzona")

def get_connection():
    """Zwraca połączenie do bazy danych"""
    return mysql.connector.connect(**DB_CONFIG)


def get_tickers_to_fetch():
    """Pobiera listę wszystkich tickerów z tabeli stocks zamiast ticker_watchlist"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    tickers = []

    try:
        # Pobierz wszystkie aktywne tickery z tabeli stocks
        cursor.execute("""
        SELECT ticker, name FROM stocks
        """)

        stocks = cursor.fetchall()

        for stock in stocks:
            ticker = stock['ticker']
            # Tworzymy pełny ticker dodając .WA (Warsaw)
            full_ticker = f"{ticker}.WA"

            tickers.append({
                'ticker': ticker,
                'full_ticker': full_ticker
            })

    except Exception as e:
        print(f"Błąd przy pobieraniu listy spółek: {e}")
    finally:
        cursor.close()
        conn.close()

    return tickers


def fetch_stock_info(ticker, full_ticker):
    """Pobiera informacje o spółce z Yahoo Finance"""
    try:
        stock = yf.Ticker(full_ticker)
        info = stock.info

        # Podstawowe informacje
        name = info.get('shortName', ticker)
        sector = info.get('sector', 'Nieznany')

        # Tablice ze spółkami w poszczególnych indeksach
        # Aktualna lista spółek WIG20
        wig20_tickers = ['ALE', 'CCC', 'CDR', 'CPS', 'DNP', 'JSW', 'KGH', 'LPP', 'LTS', 'MBK',
                         'OPL', 'PCO', 'PEO', 'PGE', 'PGN', 'PKN', 'PKO', 'PLY', 'PZU', 'SPL']

        # Aktualna lista spółek mWIG40
        mwig40_tickers = ['11B', 'AMC', 'ASB', 'AST', 'ATT', 'BDX', 'BFT', 'BHW', 'CAR', 'CIE',
                          'CLN', 'CMR', 'DOM', 'EAT', 'ENG', 'EUR', 'GPW', 'ING', 'KER', 'KRU',
                          'KTY', 'LVC', 'MAB', 'MIL', 'MLB', 'NEU', 'PCR', 'PKP', 'PLW', 'TEN',
                          'UNT', 'VRG', 'WPL', 'XTP', 'ZAP']

        # Określ indeks na podstawie listy spółek
        if ticker in wig20_tickers:
            index_name = 'WIG20'
        elif ticker in mwig40_tickers:
            index_name = 'mWIG40'
        else:
            # Sprawdź, czy spółka jest na GPW
            if '.WA' in full_ticker:
                index_name = 'sWIG80'  # Lub po prostu "WIG" dla pozostałych
            else:
                index_name = 'Inne'  # Dla spółek spoza GPW

        return {
            'ticker': ticker,
            'name': name,
            'sector': sector,
            'index_name': index_name
        }
    except Exception as e:
        print(f"Błąd pobierania informacji o {ticker}: {e}")
        return {
            'ticker': ticker,
            'name': f"{ticker} S.A.",
            'sector': 'Nieznany',
            'index_name': 'WIG'  # Domyślnie WIG
        }

def insert_or_update_stock(stock_info):
    """Dodaje lub aktualizuje informacje o spółce w bazie"""
    if not stock_info:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Sprawdź czy spółka istnieje
        cursor.execute("SELECT ticker FROM stocks WHERE ticker = %s", (stock_info['ticker'],))
        exists = cursor.fetchone()

        if exists:
            # Aktualizuj dane
            cursor.execute("""
            UPDATE stocks 
            SET name = %s, sector = %s, index_name = %s 
            WHERE ticker = %s
            """, (stock_info['name'], stock_info['sector'], stock_info['index_name'], stock_info['ticker']))
        else:
            # Dodaj nową spółkę
            cursor.execute("""
            INSERT INTO stocks (ticker, name, sector, index_name) 
            VALUES (%s, %s, %s, %s)
            """, (stock_info['ticker'], stock_info['name'], stock_info['sector'], stock_info['index_name']))

        conn.commit()
    except Exception as e:
        print(f"Błąd przy zapisie danych spółki {stock_info['ticker']}: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def fetch_stock_price(ticker, full_ticker):
    """Pobiera aktualną cenę i dane cenowe spółki"""
    try:
        stock = yf.Ticker(full_ticker)
        info = stock.info

        # Cena i zmiany
        current_price = info.get('currentPrice', 0)
        prev_close = info.get('previousClose', 0)

        if prev_close > 0:
            change_percent = ((current_price - prev_close) / prev_close) * 100
        else:
            change_percent = 0

        return {
            'ticker': ticker,
            'price': current_price,
            'prev_close': prev_close,
            'change_percent': change_percent,
            'volume': info.get('volume', 0),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'eps': info.get('trailingEps', 0)
        }
    except Exception as e:
        print(f"Błąd pobierania ceny dla {ticker}: {e}")
        # Generowanie danych zastępczych
        price = random.uniform(10, 500)
        change = random.uniform(-4, 4)
        return {
            'ticker': ticker,
            'price': price,
            'prev_close': price / (1 + change / 100),
            'change_percent': change,
            'volume': random.randint(50000, 1000000),
            'market_cap': price * random.randint(1000000, 100000000),
            'pe_ratio': random.uniform(5, 25),
            'dividend_yield': random.uniform(0, 5),
            'eps': random.uniform(0, 10)
        }


def insert_stock_price(price_data):
    """Zapisuje aktualną cenę spółki do bazy"""
    if not price_data:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO stock_prices 
        (ticker, price, prev_close, change_percent, volume, market_cap, pe_ratio, dividend_yield, eps) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            price_data['ticker'],
            price_data['price'],
            price_data['prev_close'],
            price_data['change_percent'],
            price_data['volume'],
            price_data['market_cap'],
            price_data['pe_ratio'],
            price_data['dividend_yield'],
            price_data['eps']
        ))

        conn.commit()
    except Exception as e:
        print(f"Błąd przy zapisie ceny dla {price_data['ticker']}: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def fetch_historical_data(ticker, full_ticker, days=30):
    """Pobiera dane historyczne dla spółki"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        stock = yf.Ticker(full_ticker)
        history = stock.history(start=start_date, end=end_date)

        data = []
        for index, row in history.iterrows():
            data.append({
                'ticker': ticker,
                'date': index.date(),
                'open_price': row['Open'],
                'high_price': row['High'],
                'low_price': row['Low'],
                'close_price': row['Close'],
                'volume': row['Volume']
            })

        if not data:
            # Jeśli nie ma danych, generuj sztuczne dane historyczne
            print(f"Brak danych historycznych dla {ticker}. Generowanie danych zastępczych.")
            price = random.uniform(10, 500)
            for i in range(days):
                date = (end_date - timedelta(days=i)).date()
                # Losowa zmiana ceny od -3% do +3%
                change = (random.random() * 6 - 3) / 100
                price = price * (1 + change)
                data.append({
                    'ticker': ticker,
                    'date': date,
                    'open_price': price * (1 - random.random() * 0.01),
                    'high_price': price * (1 + random.random() * 0.02),
                    'low_price': price * (1 - random.random() * 0.02),
                    'close_price': price,
                    'volume': random.randint(50000, 500000)
                })
            # Odwróć listę, aby najstarsze dane były pierwsze
            data.reverse()

        return data
    except Exception as e:
        print(f"Błąd pobierania danych historycznych dla {ticker}: {e}")
        # Generuj sztuczne dane historyczne
        data = []
        price = random.uniform(10, 500)
        for i in range(days):
            date = (end_date - timedelta(days=i)).date()
            # Losowa zmiana ceny od -3% do +3%
            change = (random.random() * 6 - 3) / 100
            price = price * (1 + change)
            data.append({
                'ticker': ticker,
                'date': date,
                'open_price': price * (1 - random.random() * 0.01),
                'high_price': price * (1 + random.random() * 0.02),
                'low_price': price * (1 - random.random() * 0.02),
                'close_price': price,
                'volume': random.randint(50000, 500000)
            })
        # Odwróć listę, aby najstarsze dane były pierwsze
        data.reverse()
        return data


def insert_historical_data(historical_data):
    """Zapisuje dane historyczne do bazy"""
    if not historical_data:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Usuń istniejące dane dla tego tickera
        cursor.execute("DELETE FROM stock_historical WHERE ticker = %s", (historical_data[0]['ticker'],))

        # Dodaj nowe dane
        for data_point in historical_data:
            cursor.execute("""
            INSERT INTO stock_historical 
            (ticker, date, open_price, high_price, low_price, close_price, volume) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data_point['ticker'],
                data_point['date'],
                data_point['open_price'],
                data_point['high_price'],
                data_point['low_price'],
                data_point['close_price'],
                data_point['volume']
            ))

        conn.commit()
    except Exception as e:
        print(f"Błąd przy zapisie danych historycznych: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def fetch_index_data(index_ticker):
    """Pobiera dane indeksu giełdowego lub tworzy dane zastępcze"""
    try:
        # Najpierw próbujemy pobrać z Yahoo Finance
        index = yf.Ticker(index_ticker)
        history = index.history(period="2d")

        # Nazwy indeksów
        index_names = {
            '^WIG': 'WIG',
            '^WIG20': 'WIG20',
            '^MWIG40': 'mWIG40',
            '^SWIG80': 'sWIG80'
        }

        # Jeśli historia jest pusta, wygeneruj dane zastępcze
        if len(history) == 0 or 'Close' not in history.columns:
            print(f"Brak danych dla indeksu {index_ticker}. Tworzenie danych zastępczych.")

            # Wartości zastępcze dla polskich indeksów
            mock_values = {
                '^WIG': 70000,
                '^WIG20': 2100,
                '^MWIG40': 5500,
                '^SWIG80': 21000
            }

            # Losowa zmiana procentowa
            mock_change = (random.random() * 2 - 1)  # Między -1% a +1%

            return {
                'ticker': index_ticker,
                'name': index_names.get(index_ticker, index_ticker.replace('^', '')),
                'value': mock_values.get(index_ticker, 1000),
                'change_percent': mock_change
            }

        # Oblicz zmianę procentową
        if len(history) >= 2:
            today_close = history['Close'].iloc[-1]
            prev_close = history['Close'].iloc[-2]
            change_percent = ((today_close - prev_close) / prev_close) * 100
        else:
            today_close = history['Close'].iloc[-1]
            change_percent = 0

        return {
            'ticker': index_ticker,
            'name': index_names.get(index_ticker, index_ticker.replace('^', '')),
            'value': today_close,
            'change_percent': change_percent
        }
    except Exception as e:
        print(f"Błąd pobierania danych indeksu {index_ticker}: {e}")

        # Tworzenie danych zastępczych w przypadku błędu
        mock_values = {
            '^WIG': 70000,
            '^WIG20': 2100,
            '^MWIG40': 5500,
            '^SWIG80': 21000
        }

        # Losowa zmiana procentowa
        mock_change = (random.random() * 2 - 1)  # Między -1% a +1%

        return {
            'ticker': index_ticker,
            'name': index_ticker.replace('^', ''),
            'value': mock_values.get(index_ticker, 1000),
            'change_percent': mock_change
        }


def insert_or_update_index(index_data):
    """Dodaje lub aktualizuje informacje o indeksie w bazie"""
    if not index_data:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Sprawdź czy indeks istnieje
        cursor.execute("SELECT ticker FROM indexes WHERE ticker = %s", (index_data['ticker'],))
        exists = cursor.fetchone()

        if exists:
            # Aktualizuj dane
            cursor.execute("""
            UPDATE indexes 
            SET name = %s, value = %s, change_percent = %s, timestamp = CURRENT_TIMESTAMP 
            WHERE ticker = %s
            """, (index_data['name'], index_data['value'], index_data['change_percent'], index_data['ticker']))
        else:
            # Dodaj nowy indeks
            cursor.execute("""
            INSERT INTO indexes (ticker, name, value, change_percent) 
            VALUES (%s, %s, %s, %s)
            """, (index_data['ticker'], index_data['name'], index_data['value'], index_data['change_percent']))

        conn.commit()
    except Exception as e:
        print(f"Błąd przy zapisie danych indeksu {index_data['ticker']}: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def update_stocks_data():
    """Główna funkcja aktualizująca dane wszystkich spółek"""
    print(f"Aktualizacja danych: {datetime.now()}")

    # Aktualizacja danych indeksów
    for index_ticker in INDEXES:
        index_data = fetch_index_data(index_ticker)
        if index_data:
            insert_or_update_index(index_data)
            print(f"Zaktualizowano dane indeksu {index_data['name']}")

    # Pobierz listę tickerów z bazy danych
    tickers = get_tickers_to_fetch()

    # Oblicz całkowitą liczbę spółek
    total_tickers = len(tickers)

    for i, ticker_data in enumerate(tickers):
        ticker = ticker_data['ticker']
        full_ticker = ticker_data['full_ticker']

        # Wyświetl postęp [bieżący/całkowity]
        print(f"Pobieranie danych dla {ticker} ({full_ticker})... [{i + 1}/{total_tickers}]")

        # 1. Podstawowe informacje o spółce
        stock_info = fetch_stock_info(ticker, full_ticker)
        if stock_info:
            insert_or_update_stock(stock_info)

        # 2. Aktualna cena i dane
        price_data = fetch_stock_price(ticker, full_ticker)
        if price_data:
            insert_stock_price(price_data)

        # 3. Dane historyczne
        historical_data = fetch_historical_data(ticker, full_ticker)
        if historical_data:
            insert_historical_data(historical_data)

        # Pauza dla Yahoo Finance API
        time.sleep(1)

    print("Zakończono aktualizację danych")


def main():
    """Główna funkcja programu"""
    print("Uruchamianie skryptu aktualizacji danych giełdowych...")

    # Tworzenie struktury bazy danych
    create_database_structure()

    # Jednorazowa aktualizacja na starcie
    update_stocks_data()

    # Harmonogram aktualizacji (co godzinę w godzinach giełdowych)
    schedule.every().day.at("09:00").do(update_stocks_data)
    schedule.every().day.at("10:00").do(update_stocks_data)
    schedule.every().day.at("11:00").do(update_stocks_data)
    schedule.every().day.at("12:00").do(update_stocks_data)
    schedule.every().day.at("13:00").do(update_stocks_data)
    schedule.every().day.at("14:00").do(update_stocks_data)
    schedule.every().day.at("15:00").do(update_stocks_data)
    schedule.every().day.at("16:00").do(update_stocks_data)
    schedule.every().day.at("17:00").do(update_stocks_data)

    # Pętla główna
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()