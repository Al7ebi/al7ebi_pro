import streamlit as st
import pandas as pd
import numpy as np

from utils import (
    apply_custom_css, render_header, render_section_header,
    get_stock_data, calculate_technical_indicators, STOCKS_DATA, RATING_LABELS
)

st.set_page_config(page_title="سكرينر الأسهم | Al7ebi Pro", page_icon="🔍", layout="wide")
apply_custom_css()

render_header("سكرينر الأسهم", "صفّي الأسهم حسب المعايير الفنية")

# Filters
st.markdown("### 🔧 الفلاتر")
col1, col2, col3, col4 = st.columns(4)

with col1:
    market_filter = st.selectbox("السوق", ["الكل", "أمريكي", "سعودي"])
with col2:
    rsi_min = st.slider("RSI Min", 0, 100, 0)
with col3:
    rsi_max = st.slider("RSI Max", 0, 100, 100)
with col4:
    min_change = st.slider("التغيير اليومي Min %", -10, 10, -5)

# Screening
results = []
progress_bar = st.progress(0)

all_stocks = []
for cat, stocks in STOCKS_DATA.items():
    if market_filter == "الكل" or (market_filter == "أمريكي" and "أمريكية" in cat) or (market_filter == "سعودي" and "سعودية" in cat):
        all_stocks.extend(stocks)

total = len(all_stocks)
for idx, stock in enumerate(all_stocks):
    ticker = stock['ticker']
    hist, info = get_stock_data(ticker, "3mo")

    if hist is not None and not hist.empty and len(hist) >= 30:
        hist = calculate_technical_indicators(hist)

        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        change = ((current - prev) / prev * 100)
        rsi = hist['RSI'].iloc[-1] if not hist['RSI'].isna().all() else 50
        vol = hist['Volatility'].iloc[-1] if not hist['Volatility'].isna().all() else 0
        sma20 = hist['SMA_20'].iloc[-1] if not hist['SMA_20'].isna().all() else current
        sma50 = hist['SMA_50'].iloc[-1] if not hist['SMA_50'].isna().all() else current

        # Apply filters
        if rsi_min <= rsi <= rsi_max and change >= min_change:
            trend = "📈 صاعد" if current > sma20 > sma50 else "📉 هابط" if current < sma20 < sma50 else "↔️ جانبي"

            results.append({
                'الرمز': ticker,
                'الاسم': stock['name'],
                'السعر': f"{'ر.س' if ticker.endswith('.SR') else '$'}{current:.2f}",
                'التغيير': f"{change:+.2f}%",
                'RSI': f"{rsi:.1f}",
                'التقلب': f"{vol:.1f}%",
                'الاتجاه': trend,
                'القطاع': stock['sector']
            })

    progress_bar.progress((idx + 1) / total)

progress_bar.empty()

# Results
render_section_header(f"النتائج ({len(results)} سهم)", "📋")

if results:
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True, hide_index=True)
else:
    st.warning("لا توجد أسهم مطابقة للمعايير المحددة. جرّب تعديل الفلاتر.")
