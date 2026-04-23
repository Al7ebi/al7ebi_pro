"""
Al7ebi Pro ICT - Complete Professional Implementation
All concepts based on Michael Huddleston's ICT teachings
Features: Premium/Discount, SMT Divergence, Position Sizing, Kill Zones, Ticker Tape, Smart Scanner
"""
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import requests
import json

# ============ TIMEZONE CONFIG ============
NY_TZ = pytz.timezone('America/New_York')

def get_ny_time():
    """Get current New York time"""
    return datetime.now(NY_TZ)

def get_kill_zone_status():
    """Return active kill zones based on NY time"""
    now = get_ny_time()
    hour = now.hour
    minute = now.minute
    time_val = hour + minute / 60

    zones = {
        'asian': {'name': 'الجلسة الآسيوية', 'start': 0, 'end': 2, 'active': False, 'priority': 1},
        'london': {'name': '🔥 London Kill Zone', 'start': 2, 'end': 5, 'active': False, 'priority': 3},
        'london_close': {'name': 'London Close', 'start': 10, 'end': 12, 'active': False, 'priority': 2},
        'ny': {'name': '🔥 New York Kill Zone', 'start': 7, 'end': 10, 'active': False, 'priority': 3},
        'ny_pm': {'name': 'NY PM Session', 'start': 13, 'end': 16, 'active': False, 'priority': 2},
    }

    active = []
    for key, zone in zones.items():
        if zone['start'] <= time_val < zone['end']:
            zone['active'] = True
            active.append(zone)

    # Countdown to next kill zone
    next_kz = None
    min_time = 24
    for key, zone in zones.items():
        if not zone['active'] and zone['priority'] >= 2:
            time_to = zone['start'] - time_val if zone['start'] > time_val else zone['start'] + 24 - time_val
            if time_to < min_time:
                min_time = time_to
                next_kz = zone

    return active, next_kz, now

def get_session_countdown():
    """Get countdown to next major session"""
    now = get_ny_time()
    hour = now.hour

    sessions = [
        (2, "London Open"),
        (7, "NY Open"),
        (10, "Silver Bullet (NY)"),
        (13, "NY PM Open"),
    ]

    for target_hour, name in sessions:
        if hour < target_hour:
            diff = timedelta(hours=target_hour - hour, minutes=-now.minute, seconds=-now.second)
            return name, diff

    # Next day London
    diff = timedelta(hours=26 - hour, minutes=-now.minute, seconds=-now.second)
    return "London Open (غداً)", diff

# ============ STOCKS DATA ============
STOCKS_DATA = {
    '🇺🇸 الأسهم الأمريكية': [
        {'ticker': 'AAPL', 'name': 'Apple', 'sector': 'تكنولوجيا', 'volatility': 'medium', 'index': 'NDX'},
        {'ticker': 'MSFT', 'name': 'Microsoft', 'sector': 'تكنولوجيا', 'volatility': 'low', 'index': 'NDX'},
        {'ticker': 'GOOGL', 'name': 'Alphabet', 'sector': 'تكنولوجيا', 'volatility': 'medium', 'index': 'NDX'},
        {'ticker': 'AMZN', 'name': 'Amazon', 'sector': 'تجارة إلكترونية', 'volatility': 'medium', 'index': 'NDX'},
        {'ticker': 'NVDA', 'name': 'NVIDIA', 'sector': 'تكنولوجيا', 'volatility': 'high', 'index': 'NDX'},
        {'ticker': 'META', 'name': 'Meta', 'sector': 'تكنولوجيا', 'volatility': 'high', 'index': 'NDX'},
        {'ticker': 'TSLA', 'name': 'Tesla', 'sector': 'سيارات', 'volatility': 'very_high', 'index': 'NDX'},
        {'ticker': 'BRK-B', 'name': 'Berkshire', 'sector': 'تأمين', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'UNH', 'name': 'UnitedHealth', 'sector': 'رعاية صحية', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'JNJ', 'name': 'Johnson & Johnson', 'sector': 'رعاية صحية', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'V', 'name': 'Visa', 'sector': 'خدمات مالية', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'JPM', 'name': 'JPMorgan', 'sector': 'بنوك', 'volatility': 'medium', 'index': 'SPX'},
        {'ticker': 'WMT', 'name': 'Walmart', 'sector': 'تجارة', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'PG', 'name': 'P&G', 'sector': 'سلع استهلاكية', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'MA', 'name': 'Mastercard', 'sector': 'خدمات مالية', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'LLY', 'name': 'Eli Lilly', 'sector': 'رعاية صحية', 'volatility': 'medium', 'index': 'SPX'},
        {'ticker': 'HD', 'name': 'Home Depot', 'sector': 'تجارة', 'volatility': 'medium', 'index': 'SPX'},
        {'ticker': 'CVX', 'name': 'Chevron', 'sector': 'طاقة', 'volatility': 'medium', 'index': 'SPX'},
        {'ticker': 'MRK', 'name': 'Merck', 'sector': 'رعاية صحية', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'ABBV', 'name': 'AbbVie', 'sector': 'رعاية صحية', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'PEP', 'name': 'PepsiCo', 'sector': 'سلع استهلاكية', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'KO', 'name': 'Coca-Cola', 'sector': 'سلع استهلاكية', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'BAC', 'name': 'Bank of America', 'sector': 'بنوك', 'volatility': 'medium', 'index': 'SPX'},
        {'ticker': 'TMO', 'name': 'Thermo Fisher', 'sector': 'رعاية صحية', 'volatility': 'medium', 'index': 'SPX'},
        {'ticker': 'COST', 'name': 'Costco', 'sector': 'تجارة', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'MCD', 'name': "McDonald's", 'sector': 'مطاعم', 'volatility': 'low', 'index': 'SPX'},
        {'ticker': 'AVGO', 'name': 'Broadcom', 'sector': 'تكنولوجيا', 'volatility': 'high', 'index': 'NDX'},
        {'ticker': 'DIS', 'name': 'Disney', 'sector': 'ترفيه', 'volatility': 'medium', 'index': 'SPX'},
        {'ticker': 'NFLX', 'name': 'Netflix', 'sector': 'ترفيه', 'volatility': 'high', 'index': 'NDX'},
        {'ticker': 'AMD', 'name': 'AMD', 'sector': 'تكنولوجيا', 'volatility': 'very_high', 'index': 'NDX'},
    ],
    '🇸🇦 الأسهم السعودية': [
        {'ticker': '2222.SR', 'name': 'أرامكو', 'sector': 'طاقة', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '2010.SR', 'name': 'سابك', 'sector': 'بتروكيماويات', 'volatility': 'medium', 'index': 'TASI'},
        {'ticker': '1120.SR', 'name': 'الراجحي', 'sector': 'بنوك', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '1150.SR', 'name': 'الإنماء', 'sector': 'بنوك', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '1180.SR', 'name': 'الأهلي', 'sector': 'بنوك', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '1050.SR', 'name': 'السعودي الفرنسي', 'sector': 'بنوك', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '1010.SR', 'name': 'الرياض', 'sector': 'بنوك', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '1140.SR', 'name': 'البلاد', 'sector': 'بنوك', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '1020.SR', 'name': 'الجزيرة', 'sector': 'بنوك', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '1060.SR', 'name': 'سامبا', 'sector': 'بنوك', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '7010.SR', 'name': 'STC', 'sector': 'اتصالات', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '7030.SR', 'name': 'زين', 'sector': 'اتصالات', 'volatility': 'medium', 'index': 'TASI'},
        {'ticker': '7040.SR', 'name': 'موبايلي', 'sector': 'اتصالات', 'volatility': 'medium', 'index': 'TASI'},
        {'ticker': '7200.SR', 'name': 'سابتكو', 'sector': 'نقل', 'volatility': 'medium', 'index': 'TASI'},
        {'ticker': '1211.SR', 'name': 'معادن', 'sector': 'تعدين', 'volatility': 'high', 'index': 'TASI'},
        {'ticker': '1301.SR', 'name': 'أسلاك', 'sector': 'صناعة', 'volatility': 'medium', 'index': 'TASI'},
        {'ticker': '2002.SR', 'name': 'مبكو', 'sector': 'صناعة', 'volatility': 'medium', 'index': 'TASI'},
        {'ticker': '2280.SR', 'name': 'المراعي', 'sector': 'غذاء', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '2170.SR', 'name': 'القصيم', 'sector': 'زراعة', 'volatility': 'medium', 'index': 'TASI'},
        {'ticker': '6001.SR', 'name': 'حلواني إخوان', 'sector': 'غذاء', 'volatility': 'medium', 'index': 'TASI'},
        {'ticker': '6010.SR', 'name': 'نادك', 'sector': 'زراعة', 'volatility': 'medium', 'index': 'TASI'},
        {'ticker': '4003.SR', 'name': 'الخزف', 'sector': 'صناعة', 'volatility': 'medium', 'index': 'TASI'},
        {'ticker': '4004.SR', 'name': 'أسمنت اليمامة', 'sector': 'صناعة', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '4005.SR', 'name': 'أسمنت العربية', 'sector': 'صناعة', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '4006.SR', 'name': 'أسمنت الجنوبية', 'sector': 'صناعة', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '4007.SR', 'name': 'أسمنت القصيم', 'sector': 'صناعة', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '4008.SR', 'name': 'أسمنت الشرقية', 'sector': 'صناعة', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '4009.SR', 'name': 'أسمنت تبوك', 'sector': 'صناعة', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '4010.SR', 'name': 'أسمنت الرياض', 'sector': 'صناعة', 'volatility': 'low', 'index': 'TASI'},
        {'ticker': '4190.SR', 'name': 'جارمكو', 'sector': 'صناعة', 'volatility': 'medium', 'index': 'TASI'},
    ]
}

TIMEFRAMES = {
    'M1': '1m', 'M3': '3m', 'M5': '5m', 'M15': '15m', 'M30': '30m',
    'H1': '1h', 'H2': '2h', 'H4': '4h', 'H8': '8h', 'D1': '1d',
    'W1': '1wk', 'MN': '1mo'
}

RATING_LABELS = {
    1: ('🔴 بيع قوي', '#ef4444'),
    2: ('🟠 بيع', '#f97316'),
    3: ('🟡 محايد', '#eab308'),
    4: ('🟢 شراء', '#22c55e'),
    5: ('🟢 شراء قوي', '#16a34a')
}

# ============ Ticker Tape Data ============
TICKER_SYMBOLS = {
    'DXY': 'DX-Y.NYB', 'EURUSD': 'EURUSD=X', 'GBPUSD': 'GBPUSD=X',
    'USDJPY': 'JPY=X', 'US10Y': '^TNX', 'VIX': '^VIX',
    'SPX': '^GSPC', 'NDX': '^IXIC', 'DJI': '^DJI',
    'GOLD': 'GC=F', 'OIL': 'CL=F', 'BTC': 'BTC-USD'
}

@st.cache_data(ttl=60)
def get_ticker_tape_data():
    """Get live data for ticker tape"""
    data = {}
    for name, symbol in TICKER_SYMBOLS.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d", interval="1m")
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                change = ((current - prev) / prev * 100) if prev else 0
                data[name] = {'price': current, 'change': change}
        except:
            pass
    return data

# ============ PREMIUM / DISCOUNT ============
def calculate_premium_discount(df, lookback=50):
    """
    Calculate Premium/Discount zones based on daily range
    Premium = Upper 50% of range (sell zone)
    Discount = Lower 50% of range (buy zone)
    """
    if df is None or len(df) < lookback:
        return None, None, None

    recent = df.iloc[-lookback:]
    high = recent['High'].max()
    low = recent['Low'].min()
    mid = (high + low) / 2

    current = df['Close'].iloc[-1]

    if current > mid:
        zone = 'PREMIUM'
        pct = ((current - mid) / (high - mid)) * 100 if high != mid else 0
    else:
        zone = 'DISCOUNT'
        pct = ((mid - current) / (mid - low)) * 100 if mid != low else 0

    return zone, pct, (high, mid, low)

def get_premium_discount_signal(zone, setup_direction):
    """
    Filter signals based on Premium/Discount
    - No BUY signals in Premium
    - No SELL signals in Discount
    """
    if zone == 'PREMIUM' and setup_direction == 'BUY':
        return False, "❌ ممنوع الشراء في منطقة Premium (غلاء)"
    elif zone == 'DISCOUNT' and setup_direction == 'SELL':
        return False, "❌ ممنوع البيع في منطقة Discount (رخص)"
    return True, "✅ متوافق مع منطقة السعر"

# ============ SMT DIVERGENCE ============
@st.cache_data(ttl=300)
def get_smt_divergence(stock_ticker, index_ticker='^GSPC'):
    """
    Detect SMT Divergence between stock and its index
    Returns: divergence info dict
    """
    try:
        stock = yf.Ticker(stock_ticker).history(period="5d", interval="1h")
        index = yf.Ticker(index_ticker).history(period="5d", interval="1h")

        if stock.empty or index.empty:
            return None

        # Check last swing highs/lows
        stock_high = stock['High'].iloc[-10:].max()
        stock_low = stock['Low'].iloc[-10:].min()
        stock_prev_high = stock['High'].iloc[-20:-10].max() if len(stock) > 20 else stock_high
        stock_prev_low = stock['Low'].iloc[-20:-10].min() if len(stock) > 20 else stock_low

        index_high = index['High'].iloc[-10:].max()
        index_low = index['Low'].iloc[-10:].min()
        index_prev_high = index['High'].iloc[-20:-10].max() if len(index) > 20 else index_high
        index_prev_low = index['Low'].iloc[-20:-10].min() if len(index) > 20 else index_low

        divergences = []

        # Bullish SMT: Stock made lower low, Index made higher low
        if stock_low < stock_prev_low and index_low > index_prev_low:
            divergences.append({
                'type': 'BULLISH',
                'description': f'Bullish SMT: {stock_ticker} Lower Low vs Index Higher Low',
                'strength': 'HIGH'
            })

        # Bearish SMT: Stock made higher high, Index made lower high
        if stock_high > stock_prev_high and index_high < index_prev_high:
            divergences.append({
                'type': 'BEARISH',
                'description': f'Bearish SMT: {stock_ticker} Higher High vs Index Lower High',
                'strength': 'HIGH'
            })

        return divergences
    except:
        return None

# ============ POSITION SIZING ============
def calculate_position_size(account_balance, risk_percent, entry_price, stop_loss, ticker):
    """
    Calculate position size based on risk management
    """
    if entry_price <= 0 or stop_loss <= 0 or account_balance <= 0:
        return None

    risk_amount = account_balance * (risk_percent / 100)
    stop_distance = abs(entry_price - stop_loss)

    if stop_distance == 0:
        return None

    shares = risk_amount / stop_distance

    # For Saudi stocks (whole shares only)
    if ticker.endswith('.SR'):
        shares = int(shares)

    total_value = shares * entry_price

    return {
        'shares': shares,
        'risk_amount': risk_amount,
        'stop_distance': stop_distance,
        'total_value': total_value,
        'risk_reward': None  # Will be calculated if target provided
    }

def calculate_risk_reward(entry, stop, target):
    """Calculate Risk:Reward ratio"""
    risk = abs(entry - stop)
    reward = abs(target - entry)
    if risk == 0:
        return None
    return reward / risk

# ============ AUTO RATING SYSTEM ============
def calculate_ict_rating(structure_events, fvgs, obs, unicorns, kill_zone_active, premium_discount, smt=None):
    """
    Auto-rating system 1-5 stars based on confluence
    """
    score = 0
    reasons = []

    # Market Structure (1 star)
    if structure_events and len([e for e in structure_events if 'BOS' in e['type'] or 'CHOCH' in e['type']]) > 0:
        score += 1
        reasons.append("✅ Market Structure Shift")

    # FVG Present (1 star)
    fresh_fvgs = [f for f in fvgs if f['status'] == 'FRESH']
    if fresh_fvgs:
        score += 1
        reasons.append("✅ Fresh FVG موجود")

    # Kill Zone (1 star)
    if kill_zone_active:
        score += 1
        reasons.append("✅ داخل Kill Zone")

    # Premium/Discount alignment (1 star)
    if premium_discount:
        zone, pct, _ = premium_discount
        if zone in ['PREMIUM', 'DISCOUNT'] and pct > 20:
            score += 1
            reasons.append(f"✅ في منطقة {zone} ({pct:.0f}%)")

    # Unicorn or SMT (1 star)
    if unicorns:
        score += 1
        reasons.append("✅ Unicorn Model Detected")
    elif smt:
        score += 1
        reasons.append("✅ SMT Divergence Detected")

    return score, reasons

# ============ SMART SCANNER ============
def ict_smart_scanner(stock_list, account_balance=10000, risk_percent=1):
    """
    Scan all stocks for high-probability ICT setups
    Returns: list of opportunities with ratings
    """
    opportunities = []

    for stock in stock_list[:15]:  # Scan first 15 for performance
        ticker = stock['ticker']
        try:
            hist, info = get_stock_data(ticker, "1mo", "1h")
            if hist is None or hist.empty or len(hist) < 30:
                continue

            hist = calculate_technical_indicators(hist)

            # Detect ICT concepts
            structure = detect_market_structure(hist)
            fvgs = detect_fvg(hist)
            obs = detect_order_blocks(hist)
            liquidity = detect_liquidity_levels(hist)
            unicorns = detect_unicorn_model(obs, fvgs)

            # Premium/Discount
            pd_zone, pd_pct, pd_levels = calculate_premium_discount(hist)

            # Kill zone
            active_kz, _, _ = get_kill_zone_status()
            kz_active = len(active_kz) > 0

            # Rating
            rating, reasons = calculate_ict_rating(structure, fvgs, obs, unicorns, kz_active, (pd_zone, pd_pct, pd_levels))

            if rating >= 3:  # Only show high-probability setups
                current_price = hist['Close'].iloc[-1]

                # Find nearest FVG for target
                target = None
                stop = None
                if fvgs:
                    fresh = [f for f in fvgs if f['status'] == 'FRESH']
                    if fresh:
                        target = fresh[-1]['top'] if fresh[-1]['type'] == 'BULLISH' else fresh[-1]['bottom']
                        stop = fresh[-1]['bottom'] if fresh[-1]['type'] == 'BULLISH' else fresh[-1]['top']

                # Position sizing
                pos_size = None
                if stop:
                    pos_size = calculate_position_size(account_balance, risk_percent, current_price, stop, ticker)

                opportunities.append({
                    'ticker': ticker,
                    'name': stock['name'],
                    'rating': rating,
                    'reasons': reasons,
                    'price': current_price,
                    'target': target,
                    'stop': stop,
                    'position_size': pos_size,
                    'zone': pd_zone,
                    'zone_pct': pd_pct,
                    'unicorn': len(unicorns) > 0,
                    'kill_zone': kz_active
                })
        except:
            continue

    return sorted(opportunities, key=lambda x: x['rating'], reverse=True)

# ============ ICT DETECTION FUNCTIONS ============
def detect_market_structure(df, min_displacement_atr=1.5):
    """
    Detect BOS, CHoCH, MSS with displacement validation
    """
    if len(df) < 5:
        return []

    events = []
    highs = df['High'].values
    lows = df['Low'].values
    closes = df['Close'].values
    atr = df['ATR'].values if 'ATR' in df.columns else np.ones(len(df))

    for i in range(2, len(df) - 2):
        # Swing High with displacement check
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            if i > 5:
                prev_high = max(highs[max(0,i-10):i-2])
                candle_body = abs(closes[i] - df['Open'].iloc[i])

                if candle_body > atr[i] * min_displacement_atr:
                    if highs[i] > prev_high:
                        events.append({
                            'type': 'BOS_BULLISH',
                            'index': i,
                            'price': highs[i],
                            'time': df.index[i],
                            'displacement': True,
                            'description': 'BOS Bullish - Valid Displacement ✅'
                        })
                    else:
                        events.append({
                            'type': 'CHOCH_BEARISH',
                            'index': i,
                            'price': highs[i],
                            'time': df.index[i],
                            'displacement': True,
                            'description': 'CHoCH Bearish - Structure Break 🔴'
                        })

        # Swing Low
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            if i > 5:
                prev_low = min(lows[max(0,i-10):i-2])
                candle_body = abs(closes[i] - df['Open'].iloc[i])

                if candle_body > atr[i] * min_displacement_atr:
                    if lows[i] < prev_low:
                        events.append({
                            'type': 'BOS_BEARISH',
                            'index': i,
                            'price': lows[i],
                            'time': df.index[i],
                            'displacement': True,
                            'description': 'BOS Bearish - Valid Displacement ✅'
                        })
                    else:
                        events.append({
                            'type': 'CHOCH_BULLISH',
                            'index': i,
                            'price': lows[i],
                            'time': df.index[i],
                            'displacement': True,
                            'description': 'CHoCH Bullish - Structure Break 🟢'
                        })

    return events

def detect_fvg(df):
    """Detect Fair Value Gaps with status tracking"""
    if len(df) < 3:
        return []

    fvgs = []
    highs = df['High'].values
    lows = df['Low'].values

    for i in range(2, len(df)):
        if lows[i] > highs[i-2]:
            fvgs.append({
                'type': 'BULLISH',
                'top': lows[i],
                'bottom': highs[i-2],
                'ce': (lows[i] + highs[i-2]) / 2,
                'index': i,
                'time': df.index[i],
                'status': 'FRESH',
                'description': 'Bullish FVG (BISI)'
            })
        elif highs[i] < lows[i-2]:
            fvgs.append({
                'type': 'BEARISH',
                'top': lows[i-2],
                'bottom': highs[i],
                'ce': (lows[i-2] + highs[i]) / 2,
                'index': i,
                'time': df.index[i],
                'status': 'FRESH',
                'description': 'Bearish FVG (SIBI)'
            })

    # Check mitigation
    for fvg in fvgs:
        idx = fvg['index']
        if idx < len(df) - 1:
            subsequent = df['Close'].iloc[idx+1:].values
            if fvg['type'] == 'BULLISH':
                if any(p <= fvg['bottom'] for p in subsequent):
                    fvg['status'] = 'MITIGATED'
                elif any(p <= fvg['ce'] for p in subsequent):
                    fvg['status'] = 'PARTIAL'
            else:
                if any(p >= fvg['top'] for p in subsequent):
                    fvg['status'] = 'MITIGATED'
                elif any(p >= fvg['ce'] for p in subsequent):
                    fvg['status'] = 'PARTIAL'

    return fvgs

def detect_order_blocks(df, min_body_ratio=0.5):
    """Detect Order Blocks and Breaker Blocks"""
    if len(df) < 5:
        return []

    obs = []
    opens = df['Open'].values
    highs = df['High'].values
    lows = df['Low'].values
    closes = df['Close'].values
    atr = df['ATR'].values if 'ATR' in df.columns else np.ones(len(df))

    for i in range(1, len(df) - 2):
        if closes[i] < opens[i]:  # Bearish candle
            if closes[i+1] > opens[i+1] and closes[i+2] > opens[i+2]:
                displacement = (closes[i+2] - closes[i]) / closes[i]
                candle_body = abs(closes[i] - opens[i])

                if displacement > 0.01 and candle_body > atr[i] * 0.5:
                    obs.append({
                        'type': 'BULLISH',
                        'top': highs[i],
                        'bottom': lows[i],
                        'open': opens[i],
                        'close': closes[i],
                        'index': i,
                        'time': df.index[i],
                        'displacement': displacement,
                        'status': 'ACTIVE',
                        'description': 'Bullish OB - Last bearish before displacement'
                    })

        elif closes[i] > opens[i]:  # Bullish candle
            if closes[i+1] < opens[i+1] and closes[i+2] < opens[i+2]:
                displacement = abs((closes[i+2] - closes[i]) / closes[i])
                candle_body = abs(closes[i] - opens[i])

                if displacement > 0.01 and candle_body > atr[i] * 0.5:
                    obs.append({
                        'type': 'BEARISH',
                        'top': highs[i],
                        'bottom': lows[i],
                        'open': opens[i],
                        'close': closes[i],
                        'index': i,
                        'time': df.index[i],
                        'displacement': displacement,
                        'status': 'ACTIVE',
                        'description': 'Bearish OB - Last bullish before displacement'
                    })

    # Check breaker status
    for ob in obs:
        idx = ob['index']
        if idx < len(df) - 1:
            subsequent = df['Close'].iloc[idx+1:].values
            if ob['type'] == 'BULLISH':
                if any(c < ob['bottom'] for c in subsequent):
                    ob['status'] = 'BROKEN'
                    ob['description'] = 'Breaker Block (Bullish OB broken → Bearish)'
            else:
                if any(c > ob['top'] for c in subsequent):
                    ob['status'] = 'BROKEN'
                    ob['description'] = 'Breaker Block (Bearish OB broken → Bullish)'

    return obs

def detect_liquidity_levels(df, lookback=20):
    """Detect BSL and SSL liquidity levels"""
    if len(df) < lookback * 2:
        return []

    liquidity = []
    highs = df['High'].values
    lows = df['Low'].values

    for i in range(lookback, len(df) - lookback):
        current_high = highs[i]
        tolerance = current_high * 0.001

        for j in range(i - lookback, i):
            if abs(highs[j] - current_high) < tolerance:
                liquidity.append({
                    'type': 'BSL',
                    'price': current_high,
                    'index': i,
                    'time': df.index[i],
                    'description': 'Buy-Side Liquidity (Equal Highs)'
                })
                break

        current_low = lows[i]
        tolerance = current_low * 0.001

        for j in range(i - lookback, i):
            if abs(lows[j] - current_low) < tolerance:
                liquidity.append({
                    'type': 'SSL',
                    'price': current_low,
                    'index': i,
                    'time': df.index[i],
                    'description': 'Sell-Side Liquidity (Equal Lows)'
                })
                break

    return liquidity

def detect_unicorn_model(obs, fvgs):
    """Detect Unicorn Model: Breaker Block + FVG overlap"""
    unicorns = []

    for ob in obs:
        if ob['status'] != 'BROKEN':
            continue

        for fvg in fvgs:
            if fvg['status'] == 'MITIGATED':
                continue

            overlap_top = min(ob['top'], fvg['top'])
            overlap_bottom = max(ob['bottom'], fvg['bottom'])

            if overlap_top > overlap_bottom:
                overlap_size = overlap_top - overlap_bottom
                min_size = min(ob['top'] - ob['bottom'], fvg['top'] - fvg['bottom'])

                if overlap_size / min_size >= 0.1:
                    unicorns.append({
                        'type': 'UNICORN',
                        'overlap_top': overlap_top,
                        'overlap_bottom': overlap_bottom,
                        'ce': (overlap_top + overlap_bottom) / 2,
                        'ob': ob,
                        'fvg': fvg,
                        'description': 'Unicorn Model - Highest Probability Setup 🦄'
                    })

    return unicorns

def calculate_ote_zone(swing_high, swing_low, trend='bullish'):
    """Calculate Optimal Trade Entry zone (62%-79% Fib)"""
    range_size = swing_high - swing_low
    if trend == 'bullish':
        ote_62 = swing_high - (range_size * 0.62)
        ote_79 = swing_high - (range_size * 0.79)
        return {'top': ote_62, 'bottom': ote_79, 'mid': (ote_62 + ote_79) / 2}
    else:
        ote_62 = swing_low + (range_size * 0.62)
        ote_79 = swing_low + (range_size * 0.79)
        return {'top': ote_79, 'bottom': ote_62, 'mid': (ote_62 + ote_79) / 2}

# ============ DATA FUNCTIONS ============
@st.cache_data(ttl=300)
def get_stock_data(ticker, period="1y", interval="1d"):
    """Get stock data from yfinance"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        info = stock.info
        return hist, info
    except Exception as e:
        return None, None

def calculate_technical_indicators(df):
    """Calculate technical indicators"""
    if df is None or df.empty:
        return df

    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()

    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

    df['Volatility'] = df['Close'].pct_change().rolling(window=30).std() * np.sqrt(252) * 100

    df['TR'] = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )
    df['ATR'] = df['TR'].rolling(window=14).mean()

    return df

def get_rating_from_storage(ticker):
    ratings = st.session_state.get('ratings', {})
    return ratings.get(ticker, 0)

def save_rating(ticker, rating):
    if 'ratings' not in st.session_state:
        st.session_state['ratings'] = {}
    st.session_state['ratings'][ticker] = rating

def get_target_from_storage(ticker):
    targets = st.session_state.get('targets', {})
    return targets.get(ticker, None)

def save_target(ticker, target):
    if 'targets' not in st.session_state:
        st.session_state['targets'] = {}
    st.session_state['targets'][ticker] = target

def format_number(num):
    if num is None:
        return "—"
    if abs(num) >= 1e12:
        return f"{num/1e12:.2f}T"
    if abs(num) >= 1e9:
        return f"{num/1e9:.2f}B"
    if abs(num) >= 1e6:
        return f"{num/1e6:.2f}M"
    if abs(num) >= 1e3:
        return f"{num/1e3:.1f}K"
    return f"{num:.2f}"

def get_all_stocks_flat():
    all_stocks = []
    for category, stocks in STOCKS_DATA.items():
        for stock in stocks:
            stock['category'] = category
            all_stocks.append(stock)
    return all_stocks

# ============ STYLING ============
def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap');
    * { font-family: 'Tajawal', sans-serif !important; }
    .main { direction: rtl; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); }

    .ict-zone {
        background: linear-gradient(145deg, rgba(30,41,59,0.95), rgba(15,23,42,0.98));
        border: 1px solid rgba(59,130,246,0.3);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .ict-zone:hover {
        border-color: rgba(59,130,246,0.6);
        box-shadow: 0 8px 24px rgba(59,130,246,0.15);
    }
    .ict-zone.bullish { border-left: 4px solid #22c55e; }
    .ict-zone.bearish { border-left: 4px solid #ef4444; }
    .ict-zone.neutral { border-left: 4px solid #eab308; }
    .ict-zone.premium { border-left: 4px solid #f472b6; }
    .ict-zone.discount { border-left: 4px solid #22c55e; }

    .fvg-fresh { border-color: rgba(34,197,94,0.5) !important; }
    .fvg-partial { border-color: rgba(234,179,8,0.5) !important; }
    .fvg-mitigated { border-color: rgba(100,116,139,0.3) !important; opacity: 0.6; }

    .metric-box {
        background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(147,51,234,0.1));
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 4px;
    }

    .section-header {
        background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(147,51,234,0.1));
        border-right: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 24px 0 16px 0;
    }
    .section-header h3 {
        margin: 0;
        color: #f8fafc;
        font-weight: 700;
    }

    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(37,99,235,0.4) !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a, #1e293b);
        border-left: 1px solid rgba(59,130,246,0.1);
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(30,41,59,0.8) !important;
        border: 1px solid rgba(59,130,246,0.3) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
    }

    .stSelectbox > div > div {
        background: rgba(30,41,59,0.8) !important;
        border: 1px solid rgba(59,130,246,0.3) !important;
        border-radius: 12px !important;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 3px; }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in { animation: fadeInUp 0.5s ease forwards; }

    .status-live {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        background: rgba(34,197,94,0.15);
        border: 1px solid rgba(34,197,94,0.3);
        border-radius: 20px;
        font-size: 0.8rem;
        color: #4ade80;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    .ict-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .ict-badge.bullish { background: rgba(34,197,94,0.2); color: #4ade80; }
    .ict-badge.bearish { background: rgba(239,68,68,0.2); color: #f87171; }
    .ict-badge.neutral { background: rgba(234,179,8,0.2); color: #fbbf24; }
    .ict-badge.premium { background: rgba(244,114,182,0.2); color: #f472b6; }
    .ict-badge.discount { background: rgba(34,197,94,0.2); color: #4ade80; }

    /* Ticker Tape */
    .ticker-tape {
        background: linear-gradient(90deg, #0f172a, #1e293b, #0f172a);
        border-bottom: 1px solid rgba(59,130,246,0.2);
        padding: 8px 0;
        overflow: hidden;
        white-space: nowrap;
    }
    .ticker-item {
        display: inline-block;
        padding: 0 20px;
        font-size: 0.85rem;
        color: #94a3b8;
    }
    .ticker-item.up { color: #4ade80; }
    .ticker-item.down { color: #f87171; }

    /* Sparkline */
    .sparkline {
        display: inline-block;
        width: 60px;
        height: 20px;
    }

    /* Countdown */
    .countdown-box {
        background: rgba(234,179,8,0.1);
        border: 1px solid rgba(234,179,8,0.3);
        border-radius: 12px;
        padding: 12px 16px;
        text-align: center;
    }
    .countdown-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #fbbf24;
    }
    </style>
    """, unsafe_allow_html=True)

def render_header(title, subtitle=""):
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0 30px 0;">
        <h1 style="font-size: 2.5rem; font-weight: 900; 
                   background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   margin-bottom: 8px;">
            {title}
        </h1>
        {f'<p style="color: #94a3b8; font-size: 1.1rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_section_header(title, icon="📊"):
    st.markdown(f"""
    <div class="section-header animate-in">
        <h3>{icon} {title}</h3>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, delta=None, icon="📈"):
    delta_html = f'<span style="color: {"#4ade80" if delta and delta.startswith("+") else "#f87171"}">{delta}</span>' if delta else ''
    st.markdown(f"""
    <div class="metric-box">
        <div style="font-size: 1.5rem; margin-bottom: 8px;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_ict_zone(zone_type, details, status='active'):
    status_class = status.lower().replace(' ', '-')
    direction = 'bullish' if 'BULLISH' in zone_type or 'BUY' in zone_type else 'bearish' if 'BEARISH' in zone_type or 'SELL' in zone_type else 'neutral'

    st.markdown(f"""
    <div class="ict-zone {direction} {status_class}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span class="ict-badge {direction}">{zone_type}</span>
                <span style="color: #94a3b8; font-size: 0.8rem; margin-right: 8px;">{status}</span>
            </div>
            <span style="color: #64748b; font-size: 0.75rem;">{details.get('time', '')}</span>
        </div>
        <div style="margin-top: 8px; color: #cbd5e1; font-size: 0.9rem;">
            {details.get('description', '')}
        </div>
        {f'<div style="margin-top: 6px; color: #60a5fa; font-size: 0.85rem;">النطاق: {details.get("bottom", "")} - {details.get("top", "")}</div>' if 'top' in details and 'bottom' in details else ''}
        {f'<div style="margin-top: 4px; color: #a78bfa; font-size: 0.85rem;">CE (50%): {details.get("ce", "")}</div>' if 'ce' in details else ''}
    </div>
    """, unsafe_allow_html=True)
