"""
الح utilities المشتركة لمنصة محلل الأسهم الاحترافية
"""
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests

# ============ CONSTANTS ============
STOCKS_DATA = {
    '🇺🇸 الأسهم الأمريكية': [
        {'ticker': 'AAPL', 'name': 'Apple', 'sector': 'تكنولوجيا'},
        {'ticker': 'MSFT', 'name': 'Microsoft', 'sector': 'تكنولوجيا'},
        {'ticker': 'GOOGL', 'name': 'Alphabet', 'sector': 'تكنولوجيا'},
        {'ticker': 'AMZN', 'name': 'Amazon', 'sector': 'تجارة إلكترونية'},
        {'ticker': 'NVDA', 'name': 'NVIDIA', 'sector': 'تكنولوجيا'},
        {'ticker': 'META', 'name': 'Meta', 'sector': 'تكنولوجيا'},
        {'ticker': 'TSLA', 'name': 'Tesla', 'sector': 'سيارات'},
        {'ticker': 'BRK-B', 'name': 'Berkshire', 'sector': 'تأمين'},
        {'ticker': 'UNH', 'name': 'UnitedHealth', 'sector': 'رعاية صحية'},
        {'ticker': 'JNJ', 'name': 'J&J', 'sector': 'رعاية صحية'},
        {'ticker': 'V', 'name': 'Visa', 'sector': 'خدمات مالية'},
        {'ticker': 'JPM', 'name': 'JPMorgan', 'sector': 'بنوك'},
        {'ticker': 'WMT', 'name': 'Walmart', 'sector': 'تجارة'},
        {'ticker': 'PG', 'name': 'P&G', 'sector': 'سلع استهلاكية'},
        {'ticker': 'MA', 'name': 'Mastercard', 'sector': 'خدمات مالية'},
        {'ticker': 'LLY', 'name': 'Eli Lilly', 'sector': 'رعاية صحية'},
        {'ticker': 'HD', 'name': 'Home Depot', 'sector': 'تجارة'},
        {'ticker': 'CVX', 'name': 'Chevron', 'sector': 'طاقة'},
        {'ticker': 'MRK', 'name': 'Merck', 'sector': 'رعاية صحية'},
        {'ticker': 'ABBV', 'name': 'AbbVie', 'sector': 'رعاية صحية'},
        {'ticker': 'PEP', 'name': 'PepsiCo', 'sector': 'سلع استهلاكية'},
        {'ticker': 'KO', 'name': 'Coca-Cola', 'sector': 'سلع استهلاكية'},
        {'ticker': 'BAC', 'name': 'Bank of America', 'sector': 'بنوك'},
        {'ticker': 'TMO', 'name': 'Thermo Fisher', 'sector': 'رعاية صحية'},
        {'ticker': 'COST', 'name': 'Costco', 'sector': 'تجارة'},
        {'ticker': 'MCD', 'name': "McDonald's", 'sector': 'مطاعم'},
        {'ticker': 'AVGO', 'name': 'Broadcom', 'sector': 'تكنولوجيا'},
        {'ticker': 'DIS', 'name': 'Disney', 'sector': 'ترفيه'},
        {'ticker': 'NFLX', 'name': 'Netflix', 'sector': 'ترفيه'},
        {'ticker': 'AMD', 'name': 'AMD', 'sector': 'تكنولوجيا'},
    ],
    '🇸🇦 الأسهم السعودية': [
        {'ticker': '2222.SR', 'name': 'أرامكو', 'sector': 'طاقة'},
        {'ticker': '2010.SR', 'name': 'سابك', 'sector': 'بتروكيماويات'},
        {'ticker': '1120.SR', 'name': 'الراجحي', 'sector': 'بنوك'},
        {'ticker': '1150.SR', 'name': 'الإنماء', 'sector': 'بنوك'},
        {'ticker': '1180.SR', 'name': 'الأهلي', 'sector': 'بنوك'},
        {'ticker': '1050.SR', 'name': 'السعودي الفرنسي', 'sector': 'بنوك'},
        {'ticker': '1010.SR', 'name': 'الرياض', 'sector': 'بنوك'},
        {'ticker': '1140.SR', 'name': 'البلاد', 'sector': 'بنوك'},
        {'ticker': '1020.SR', 'name': 'الجزيرة', 'sector': 'بنوك'},
        {'ticker': '1060.SR', 'name': 'سامبا', 'sector': 'بنوك'},
        {'ticker': '7010.SR', 'name': 'STC', 'sector': 'اتصالات'},
        {'ticker': '7030.SR', 'name': 'زين', 'sector': 'اتصالات'},
        {'ticker': '7040.SR', 'name': 'موبايلي', 'sector': 'اتصالات'},
        {'ticker': '7200.SR', 'name': 'سابتكو', 'sector': 'نقل'},
        {'ticker': '1211.SR', 'name': 'معادن', 'sector': 'تعدين'},
        {'ticker': '1301.SR', 'name': 'أسلاك', 'sector': 'صناعة'},
        {'ticker': '2002.SR', 'name': 'مبكو', 'sector': 'صناعة'},
        {'ticker': '2280.SR', 'name': 'المراعي', 'sector': 'غذاء'},
        {'ticker': '2170.SR', 'name': 'القصيم', 'sector': 'زراعة'},
        {'ticker': '6001.SR', 'name': 'حلواني إخوان', 'sector': 'غذاء'},
        {'ticker': '6010.SR', 'name': 'نادك', 'sector': 'زراعة'},
        {'ticker': '4003.SR', 'name': 'الخزف', 'sector': 'صناعة'},
        {'ticker': '4004.SR', 'name': 'أسمنت اليمامة', 'sector': 'صناعة'},
        {'ticker': '4005.SR', 'name': 'أسمنت العربية', 'sector': 'صناعة'},
        {'ticker': '4006.SR', 'name': 'أسمنت الجنوبية', 'sector': 'صناعة'},
        {'ticker': '4007.SR', 'name': 'أسمنت القصيم', 'sector': 'صناعة'},
        {'ticker': '4008.SR', 'name': 'أسمنت الشرقية', 'sector': 'صناعة'},
        {'ticker': '4009.SR', 'name': 'أسمنت تبوك', 'sector': 'صناعة'},
        {'ticker': '4010.SR', 'name': 'أسمنت الرياض', 'sector': 'صناعة'},
        {'ticker': '4190.SR', 'name': 'جارمكو', 'sector': 'صناعة'},
    ]
}

RATING_LABELS = {
    1: ('🔴 بيع قوي', '#ef4444'),
    2: ('🟠 بيع', '#f97316'),
    3: ('🟡 محايد', '#eab308'),
    4: ('🟢 شراء', '#22c55e'),
    5: ('🟢 شراء قوي', '#16a34a')
}

# ============ STYLING ============
def apply_custom_css():
    """تطبيق CSS احترافي مخصص"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap');

    * { font-family: 'Tajawal', sans-serif !important; }

    .main { direction: rtl; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); }

    /* Cards */
    .stock-card {
        background: linear-gradient(145deg, rgba(30,41,59,0.9), rgba(15,23,42,0.95));
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    .stock-card:hover {
        transform: translateY(-4px);
        border-color: rgba(59,130,246,0.5);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }

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

    /* Rating stars */
    .rating-container {
        display: flex;
        gap: 8px;
        justify-content: center;
        padding: 10px 0;
    }
    .rating-star {
        font-size: 2rem;
        cursor: pointer;
        transition: all 0.2s ease;
        filter: grayscale(1);
        opacity: 0.4;
    }
    .rating-star:hover, .rating-star.active {
        filter: grayscale(0);
        opacity: 1;
        transform: scale(1.2);
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

    /* Tables */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
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

# ============ DATA FUNCTIONS ============
@st.cache_data(ttl=300)
def get_stock_data(ticker, period="1y"):
    """جلب بيانات السهم من yfinance"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
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
