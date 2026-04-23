"""
ICT (Inner Circle Trader) Methodology - Professional Implementation
All concepts based on Michael Huddleston's teachings
"""
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests

# ============ ICT CONCEPTS ENUMS ============
class ICTConcepts:
    """All ICT concepts organized by category"""

    # Market Structure
    BOS = "Break of Structure (BOS)"
    CHOCH = "Change of Character (CHoCH)"
    MSS = "Market Structure Shift (MSS)"

    # Liquidity
    BSL = "Buy-Side Liquidity"
    SSL = "Sell-Side Liquidity"
    EQH = "Equal Highs"
    EQL = "Equal Lows"
    LIQUIDITY_SWEEP = "Liquidity Sweep"
    LIQUIDITY_VOID = "Liquidity Void"

    # Order Blocks
    OB_BULLISH = "Bullish Order Block"
    OB_BEARISH = "Bearish Order Block"
    BREAKER_BLOCK = "Breaker Block"
    MITIGATION_BLOCK = "Mitigation Block"
    REJECTION_BLOCK = "Rejection Block"

    # Fair Value Gaps
    FVG_BULLISH = "Bullish FVG (BISI)"
    FVG_BEARISH = "Bearish FVG (SIBI)"
    FVG_INVERSION = "FVG Inversion (IFVG)"
    CONSEQUENT_ENCROACHMENT = "Consequent Encroachment (CE)"

    # Volume Imbalances
    VI = "Volume Imbalance"
    GAP = "Gap"

    # Time & Context
    KILL_ZONE_LONDON = "London Kill Zone (2-5 AM EST)"
    KILL_ZONE_NY = "New York Kill Zone (7-10 AM EST)"
    KILL_ZONE_LONDON_CLOSE = "London Close (10-12 PM EST)"
    ASIAN_RANGE = "Asian Range"

    # Entry Models
    SILVER_BULLET = "Silver Bullet Model"
    UNICORN_MODEL = "Unicorn Model (Breaker + FVG)"
    OTE = "Optimal Trade Entry (62%-79% Fib)"
    POWER_OF_3 = "Power of 3 (AMD)"

    # Confluence
    SMT = "Smart Money Tool (SMT Divergence)"
    CISD = "Change in State of Delivery"
    DISPLACEMENT = "Displacement"
    INDUCEMENT = "Inducement (IDM)"

# ============ TIMEFRAMES ============
TIMEFRAMES = {
    'M1': '1m', 'M3': '3m', 'M5': '5m', 'M15': '15m', 'M30': '30m',
    'H1': '1h', 'H2': '2h', 'H4': '4h', 'H8': '8h', 'D1': '1d',
    'W1': '1wk', 'MN': '1mo'
}

# ============ STOCKS DATA ============
STOCKS_DATA = {
    '🇺🇸 الأسهم الأمريكية': [
        {'ticker': 'AAPL', 'name': 'Apple', 'sector': 'تكنولوجيا', 'volatility': 'medium'},
        {'ticker': 'MSFT', 'name': 'Microsoft', 'sector': 'تكنولوجيا', 'volatility': 'low'},
        {'ticker': 'GOOGL', 'name': 'Alphabet', 'sector': 'تكنولوجيا', 'volatility': 'medium'},
        {'ticker': 'AMZN', 'name': 'Amazon', 'sector': 'تجارة إلكترونية', 'volatility': 'medium'},
        {'ticker': 'NVDA', 'name': 'NVIDIA', 'sector': 'تكنولوجيا', 'volatility': 'high'},
        {'ticker': 'META', 'name': 'Meta', 'sector': 'تكنولوجيا', 'volatility': 'high'},
        {'ticker': 'TSLA', 'name': 'Tesla', 'sector': 'سيارات', 'volatility': 'very_high'},
        {'ticker': 'BRK-B', 'name': 'Berkshire', 'sector': 'تأمين', 'volatility': 'low'},
        {'ticker': 'UNH', 'name': 'UnitedHealth', 'sector': 'رعاية صحية', 'volatility': 'low'},
        {'ticker': 'JNJ', 'name': 'Johnson & Johnson', 'sector': 'رعاية صحية', 'volatility': 'low'},
        {'ticker': 'V', 'name': 'Visa', 'sector': 'خدمات مالية', 'volatility': 'low'},
        {'ticker': 'JPM', 'name': 'JPMorgan', 'sector': 'بنوك', 'volatility': 'medium'},
        {'ticker': 'WMT', 'name': 'Walmart', 'sector': 'تجارة', 'volatility': 'low'},
        {'ticker': 'PG', 'name': 'Procter & Gamble', 'sector': 'سلع استهلاكية', 'volatility': 'low'},
        {'ticker': 'MA', 'name': 'Mastercard', 'sector': 'خدمات مالية', 'volatility': 'low'},
        {'ticker': 'LLY', 'name': 'Eli Lilly', 'sector': 'رعاية صحية', 'volatility': 'medium'},
        {'ticker': 'HD', 'name': 'Home Depot', 'sector': 'تجارة', 'volatility': 'medium'},
        {'ticker': 'CVX', 'name': 'Chevron', 'sector': 'طاقة', 'volatility': 'medium'},
        {'ticker': 'MRK', 'name': 'Merck', 'sector': 'رعاية صحية', 'volatility': 'low'},
        {'ticker': 'ABBV', 'name': 'AbbVie', 'sector': 'رعاية صحية', 'volatility': 'low'},
        {'ticker': 'PEP', 'name': 'PepsiCo', 'sector': 'سلع استهلاكية', 'volatility': 'low'},
        {'ticker': 'KO', 'name': 'Coca-Cola', 'sector': 'سلع استهلاكية', 'volatility': 'low'},
        {'ticker': 'BAC', 'name': 'Bank of America', 'sector': 'بنوك', 'volatility': 'medium'},
        {'ticker': 'TMO', 'name': 'Thermo Fisher', 'sector': 'رعاية صحية', 'volatility': 'medium'},
        {'ticker': 'COST', 'name': 'Costco', 'sector': 'تجارة', 'volatility': 'low'},
        {'ticker': 'MCD', 'name': "McDonald's", 'sector': 'مطاعم', 'volatility': 'low'},
        {'ticker': 'AVGO', 'name': 'Broadcom', 'sector': 'تكنولوجيا', 'volatility': 'high'},
        {'ticker': 'DIS', 'name': 'Disney', 'sector': 'ترفيه', 'volatility': 'medium'},
        {'ticker': 'NFLX', 'name': 'Netflix', 'sector': 'ترفيه', 'volatility': 'high'},
        {'ticker': 'AMD', 'name': 'AMD', 'sector': 'تكنولوجيا', 'volatility': 'very_high'},
    ],
    '🇸🇦 الأسهم السعودية': [
        {'ticker': '2222.SR', 'name': 'أرامكو', 'sector': 'طاقة', 'volatility': 'low'},
        {'ticker': '2010.SR', 'name': 'سابك', 'sector': 'بتروكيماويات', 'volatility': 'medium'},
        {'ticker': '1120.SR', 'name': 'الراجحي', 'sector': 'بنوك', 'volatility': 'low'},
        {'ticker': '1150.SR', 'name': 'الإنماء', 'sector': 'بنوك', 'volatility': 'low'},
        {'ticker': '1180.SR', 'name': 'الأهلي', 'sector': 'بنوك', 'volatility': 'low'},
        {'ticker': '1050.SR', 'name': 'السعودي الفرنسي', 'sector': 'بنوك', 'volatility': 'low'},
        {'ticker': '1010.SR', 'name': 'الرياض', 'sector': 'بنوك', 'volatility': 'low'},
        {'ticker': '1140.SR', 'name': 'البلاد', 'sector': 'بنوك', 'volatility': 'low'},
        {'ticker': '1020.SR', 'name': 'الجزيرة', 'sector': 'بنوك', 'volatility': 'low'},
        {'ticker': '1060.SR', 'name': 'سامبا', 'sector': 'بنوك', 'volatility': 'low'},
        {'ticker': '7010.SR', 'name': 'STC', 'sector': 'اتصالات', 'volatility': 'low'},
        {'ticker': '7030.SR', 'name': 'زين', 'sector': 'اتصالات', 'volatility': 'medium'},
        {'ticker': '7040.SR', 'name': 'موبايلي', 'sector': 'اتصالات', 'volatility': 'medium'},
        {'ticker': '7200.SR', 'name': 'سابتكو', 'sector': 'نقل', 'volatility': 'medium'},
        {'ticker': '1211.SR', 'name': 'معادن', 'sector': 'تعدين', 'volatility': 'high'},
        {'ticker': '1301.SR', 'name': 'أسلاك', 'sector': 'صناعة', 'volatility': 'medium'},
        {'ticker': '2002.SR', 'name': 'مبكو', 'sector': 'صناعة', 'volatility': 'medium'},
        {'ticker': '2280.SR', 'name': 'المراعي', 'sector': 'غذاء', 'volatility': 'low'},
        {'ticker': '2170.SR', 'name': 'القصيم', 'sector': 'زراعة', 'volatility': 'medium'},
        {'ticker': '6001.SR', 'name': 'حلواني إخوان', 'sector': 'غذاء', 'volatility': 'medium'},
        {'ticker': '6010.SR', 'name': 'نادك', 'sector': 'زراعة', 'volatility': 'medium'},
        {'ticker': '4003.SR', 'name': 'الخزف', 'sector': 'صناعة', 'volatility': 'medium'},
        {'ticker': '4004.SR', 'name': 'أسمنت اليمامة', 'sector': 'صناعة', 'volatility': 'low'},
        {'ticker': '4005.SR', 'name': 'أسمنت العربية', 'sector': 'صناعة', 'volatility': 'low'},
        {'ticker': '4006.SR', 'name': 'أسمنت الجنوبية', 'sector': 'صناعة', 'volatility': 'low'},
        {'ticker': '4007.SR', 'name': 'أسمنت القصيم', 'sector': 'صناعة', 'volatility': 'low'},
        {'ticker': '4008.SR', 'name': 'أسمنت الشرقية', 'sector': 'صناعة', 'volatility': 'low'},
        {'ticker': '4009.SR', 'name': 'أسمنت تبوك', 'sector': 'صناعة', 'volatility': 'low'},
        {'ticker': '4010.SR', 'name': 'أسمنت الرياض', 'sector': 'صناعة', 'volatility': 'low'},
        {'ticker': '4190.SR', 'name': 'جارمكو', 'sector': 'صناعة', 'volatility': 'medium'},
    ]
}

RATING_LABELS = {
    1: ('🔴 بيع قوي', '#ef4444'),
    2: ('🟠 بيع', '#f97316'),
    3: ('🟡 محايد', '#eab308'),
    4: ('🟢 شراء', '#22c55e'),
    5: ('🟢 شراء قوي', '#16a34a')
}

# ============ ICT DETECTION FUNCTIONS ============

def detect_market_structure(df):
    """
    Detect BOS, CHoCH, MSS based on swing highs/lows
    Returns: list of structure events
    """
    if len(df) < 5:
        return []

    events = []
    highs = df['High'].values
    lows = df['Low'].values
    closes = df['Close'].values

    # Find swing points (simplified)
    for i in range(2, len(df) - 2):
        # Swing High
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            # Check for BOS (higher high in uptrend)
            if i > 5:
                prev_high = max(highs[max(0,i-10):i-2])
                if highs[i] > prev_high:
                    events.append({
                        'type': 'BOS_BULLISH',
                        'index': i,
                        'price': highs[i],
                        'time': df.index[i],
                        'description': 'Break of Structure - Bullish (Higher High)'
                    })

        # Swing Low
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            if i > 5:
                prev_low = min(lows[max(0,i-10):i-2])
                if lows[i] < prev_low:
                    events.append({
                        'type': 'BOS_BEARISH',
                        'index': i,
                        'price': lows[i],
                        'time': df.index[i],
                        'description': 'Break of Structure - Bearish (Lower Low)'
                    })

    # Detect CHoCH (Change of Character)
    if len(events) >= 2:
        for i in range(1, len(events)):
            prev = events[i-1]
            curr = events[i]

            if prev['type'] == 'BOS_BULLISH' and curr['type'] == 'BOS_BEARISH':
                # Bullish to Bearish CHoCH
                if curr['price'] < prev['price']:
                    events.insert(i, {
                        'type': 'CHOCH_BEARISH',
                        'index': curr['index'],
                        'price': curr['price'],
                        'time': curr['time'],
                        'description': 'Change of Character - Bearish (Bullish trend broken)'
                    })
            elif prev['type'] == 'BOS_BEARISH' and curr['type'] == 'BOS_BULLISH':
                # Bearish to Bullish CHoCH
                if curr['price'] > prev['price']:
                    events.insert(i, {
                        'type': 'CHOCH_BULLISH',
                        'index': curr['index'],
                        'price': curr['price'],
                        'time': curr['time'],
                        'description': 'Change of Character - Bullish (Bearish trend broken)'
                    })

    return events

def detect_fvg(df):
    """
    Detect Fair Value Gaps (FVG) - 3 candle pattern
    Bullish FVG: Low[0] > High[2] (BISI)
    Bearish FVG: High[0] < Low[2] (SIBI)
    """
    if len(df) < 3:
        return []

    fvgs = []
    highs = df['High'].values
    lows = df['Low'].values
    opens = df['Open'].values
    closes = df['Close'].values

    for i in range(2, len(df)):
        # Bullish FVG (BISI - Buy Side Imbalance / Sell Side Inefficiency)
        if lows[i] > highs[i-2]:
            fvgs.append({
                'type': 'BULLISH',
                'top': lows[i],
                'bottom': highs[i-2],
                'ce': (lows[i] + highs[i-2]) / 2,  # Consequent Encroachment 50%
                'index': i,
                'time': df.index[i],
                'status': 'FRESH',
                'description': 'Bullish FVG (BISI) - Price skipped up aggressively'
            })

        # Bearish FVG (SIBI - Sell Side Imbalance / Buy Side Inefficiency)
        elif highs[i] < lows[i-2]:
            fvgs.append({
                'type': 'BEARISH',
                'top': lows[i-2],
                'bottom': highs[i],
                'ce': (lows[i-2] + highs[i]) / 2,
                'index': i,
                'time': df.index[i],
                'status': 'FRESH',
                'description': 'Bearish FVG (SIBI) - Price dropped aggressively'
            })

    # Check mitigation status
    for fvg in fvgs:
        idx = fvg['index']
        if idx < len(df) - 1:
            subsequent_prices = df['Close'].iloc[idx+1:].values
            if fvg['type'] == 'BULLISH':
                if any(p <= fvg['bottom'] for p in subsequent_prices):
                    fvg['status'] = 'MITIGATED'
                elif any(p <= fvg['ce'] for p in subsequent_prices):
                    fvg['status'] = 'PARTIAL'
            else:
                if any(p >= fvg['top'] for p in subsequent_prices):
                    fvg['status'] = 'MITIGATED'
                elif any(p >= fvg['ce'] for p in subsequent_prices):
                    fvg['status'] = 'PARTIAL'

    return fvgs

def detect_order_blocks(df, min_body_ratio=0.5):
    """
    Detect Order Blocks (OB)
    Bullish OB: Last bearish candle before aggressive bullish move
    Bearish OB: Last bullish candle before aggressive bearish move
    """
    if len(df) < 5:
        return []

    obs = []
    opens = df['Open'].values
    highs = df['High'].values
    lows = df['Low'].values
    closes = df['Close'].values

    for i in range(1, len(df) - 2):
        # Bullish Order Block
        if closes[i] < opens[i]:  # Bearish candle
            # Check if followed by strong bullish displacement
            if closes[i+1] > opens[i+1] and closes[i+2] > opens[i+2]:
                displacement = (closes[i+2] - closes[i]) / closes[i]
                if displacement > 0.01:  # 1% minimum displacement
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
                        'description': 'Bullish Order Block - Last bearish candle before bullish displacement'
                    })

        # Bearish Order Block
        elif closes[i] > opens[i]:  # Bullish candle
            if closes[i+1] < opens[i+1] and closes[i+2] < opens[i+2]:
                displacement = abs((closes[i+2] - closes[i]) / closes[i])
                if displacement > 0.01:
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
                        'description': 'Bearish Order Block - Last bullish candle before bearish displacement'
                    })

    # Check if OBs are broken (Breaker Blocks)
    for ob in obs:
        idx = ob['index']
        if idx < len(df) - 1:
            subsequent_closes = df['Close'].iloc[idx+1:].values
            if ob['type'] == 'BULLISH':
                if any(c < ob['bottom'] for c in subsequent_closes):
                    ob['status'] = 'BROKEN'
                    ob['description'] = 'Breaker Block (was Bullish OB, now Bearish)'
            else:
                if any(c > ob['top'] for c in subsequent_closes):
                    ob['status'] = 'BROKEN'
                    ob['description'] = 'Breaker Block (was Bearish OB, now Bullish)'

    return obs

def detect_liquidity_levels(df, lookback=20):
    """
    Detect liquidity levels (Equal Highs/Lows)
    BSL: Equal Highs
    SSL: Equal Lows
    """
    if len(df) < lookback * 2:
        return []

    liquidity = []
    highs = df['High'].values
    lows = df['Low'].values

    # Find equal highs (Buy-Side Liquidity)
    for i in range(lookback, len(df) - lookback):
        current_high = highs[i]
        tolerance = current_high * 0.001  # 0.1% tolerance

        # Check if there are equal highs nearby
        for j in range(i - lookback, i):
            if abs(highs[j] - current_high) < tolerance:
                liquidity.append({
                    'type': 'BSL',
                    'price': current_high,
                    'index': i,
                    'time': df.index[i],
                    'description': 'Buy-Side Liquidity (Equal Highs) - Stops above highs'
                })
                break

    # Find equal lows (Sell-Side Liquidity)
    for i in range(lookback, len(df) - lookback):
        current_low = lows[i]
        tolerance = current_low * 0.001

        for j in range(i - lookback, i):
            if abs(lows[j] - current_low) < tolerance:
                liquidity.append({
                    'type': 'SSL',
                    'price': current_low,
                    'index': i,
                    'time': df.index[i],
                    'description': 'Sell-Side Liquidity (Equal Lows) - Stops below lows'
                })
                break

    return liquidity

def calculate_ote_zone(swing_high, swing_low, trend='bullish'):
    """
    Calculate Optimal Trade Entry (OTE) zone
    ICT OTE: 62% - 79% Fibonacci retracement of displacement leg
    """
    if trend == 'bullish':
        range_size = swing_high - swing_low
        ote_62 = swing_high - (range_size * 0.62)
        ote_79 = swing_high - (range_size * 0.79)
        return {'top': ote_62, 'bottom': ote_79, 'mid': (ote_62 + ote_79) / 2}
    else:
        range_size = swing_high - swing_low
        ote_62 = swing_low + (range_size * 0.62)
        ote_79 = swing_low + (range_size * 0.79)
        return {'top': ote_79, 'bottom': ote_62, 'mid': (ote_62 + ote_79) / 2}

def detect_unicorn_model(obs, fvgs):
    """
    Detect Unicorn Model: Breaker Block + FVG overlap
    One of the highest-conviction setups in ICT
    """
    unicorns = []

    for ob in obs:
        if ob['status'] != 'BROKEN':
            continue

        for fvg in fvgs:
            if fvg['status'] == 'MITIGATED':
                continue

            # Check for overlap
            overlap_top = min(ob['top'], fvg['top'])
            overlap_bottom = max(ob['bottom'], fvg['bottom'])

            if overlap_top > overlap_bottom:
                overlap_size = overlap_top - overlap_bottom
                ob_size = ob['top'] - ob['bottom']
                fvg_size = fvg['top'] - fvg['bottom']

                # Minimum 10% overlap
                min_size = min(ob_size, fvg_size)
                if overlap_size / min_size >= 0.1:
                    unicorns.append({
                        'type': 'UNICORN',
                        'overlap_top': overlap_top,
                        'overlap_bottom': overlap_bottom,
                        'ce': (overlap_top + overlap_bottom) / 2,
                        'ob': ob,
                        'fvg': fvg,
                        'description': 'Unicorn Model - Breaker Block + FVG overlap (highest probability zone)'
                    })

    return unicorns

def calculate_kill_zone_times():
    """Return current Kill Zone status"""
    now = datetime.now()
    hour = now.hour

    # EST times (approximate for Saudi timezone +7)
    zones = {
        'asian': (0, 8),      # 12 AM - 8 AM EST
        'london': (2, 5),     # 2 AM - 5 AM EST
        'ny': (7, 10),        # 7 AM - 10 AM EST
        'london_close': (10, 12)  # 10 AM - 12 PM EST
    }

    active = []
    for name, (start, end) in zones.items():
        if start <= hour < end:
            active.append(name)

    return active

# ============ STYLING ============
def apply_custom_css():
    """تطبيق CSS احترافي مخصص"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap');

    * { font-family: 'Tajawal', sans-serif !important; }

    .main { direction: rtl; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); }

    /* ICT Zone Cards */
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

    /* FVG specific */
    .fvg-fresh { border-color: rgba(34,197,94,0.5) !important; }
    .fvg-partial { border-color: rgba(234,179,8,0.5) !important; }
    .fvg-mitigated { border-color: rgba(100,116,139,0.3) !important; opacity: 0.6; }

    /* Metric cards */
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

    /* Section headers */
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

    /* Custom buttons */
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

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a, #1e293b);
        border-left: 1px solid rgba(59,130,246,0.1);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(30,41,59,0.8) !important;
        border: 1px solid rgba(59,130,246,0.3) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: rgba(30,41,59,0.8) !important;
        border: 1px solid rgba(59,130,246,0.3) !important;
        border-radius: 12px !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 3px; }

    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in { animation: fadeInUp 0.5s ease forwards; }

    /* Status indicators */
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

    /* ICT Badge */
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
    </style>
    """, unsafe_allow_html=True)

def render_header(title, subtitle=""):
    """عرض الهيدر الاحترافي"""
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
    """عرض عنوان قسم"""
    st.markdown(f"""
    <div class="section-header animate-in">
        <h3>{icon} {title}</h3>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, delta=None, icon="📈"):
    """عرض كارت ميتريك"""
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
    """عرض منطقة ICT"""
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

# ============ DATA FUNCTIONS ============
@st.cache_data(ttl=300)
def get_stock_data(ticker, period="1y", interval="1d"):
    """جلب بيانات السهم من yfinance"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        info = stock.info
        return hist, info
    except Exception as e:
        st.error(f"خطأ في جلب بيانات {ticker}: {str(e)}")
        return None, None

def calculate_technical_indicators(df):
    """حساب المؤشرات الفنية"""
    if df is None or df.empty:
        return df

    # Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()

    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

    # Standard Deviation (Volatility)
    df['Volatility'] = df['Close'].pct_change().rolling(window=30).std() * np.sqrt(252) * 100

    # ATR for displacement detection
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
    """جلب التقييم من التخزين"""
    ratings = st.session_state.get('ratings', {})
    return ratings.get(ticker, 0)

def save_rating(ticker, rating):
    """حفظ التقييم"""
    if 'ratings' not in st.session_state:
        st.session_state['ratings'] = {}
    st.session_state['ratings'][ticker] = rating

def get_target_from_storage(ticker):
    """جلب السعر المستهدف"""
    targets = st.session_state.get('targets', {})
    return targets.get(ticker, None)

def save_target(ticker, target):
    """حفظ السعر المستهدف"""
    if 'targets' not in st.session_state:
        st.session_state['targets'] = {}
    st.session_state['targets'][ticker] = target

def format_number(num):
    """تنسيق الأرقام الكبيرة"""
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
    """الحصول على قائمة مسطحة من جميع الأسهم"""
    all_stocks = []
    for category, stocks in STOCKS_DATA.items():
        for stock in stocks:
            stock['category'] = category
            all_stocks.append(stock)
    return all_stocks
