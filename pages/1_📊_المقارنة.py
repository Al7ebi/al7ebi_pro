import streamlit as st
import pandas as pd
import numpy as np

from utils import (
    apply_custom_css, render_header, render_section_header,
    get_stock_data, calculate_technical_indicators, 
    detect_market_structure, detect_fvg, detect_order_blocks,
    calculate_premium_discount, STOCKS_DATA
)

st.set_page_config(page_title="ICT سكرينر | Al7ebi Pro", page_icon="🔍", layout="wide")
apply_custom_css()

render_header("ICT سكرينر متقدم", "صفّي الأسهم حسب معايير ICT")

st.markdown("### 🔧 فلاتر ICT")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    market_filter = st.selectbox("السوق", ["الكل", "أمريكي", "سعودي"])
with col2:
    min_rating = st.slider("الحد الأدنى للتقييم", 1, 5, 3)
with col3:
    require_fvg = st.checkbox("FVG جديد فقط", value=True)
with col4:
    require_zone = st.selectbox("المنطقة", ["الكل", "Premium", "Discount"])
with col5:
    min_rr = st.slider("R:R Min", 1.0, 5.0, 2.0, 0.5)

if st.button("🔍 مسح ICT", use_container_width=True):
    results = []
    progress_bar = st.progress(0)

    all_stocks = []
    for cat, stocks in STOCKS_DATA.items():
        if market_filter == "الكل" or (market_filter == "أمريكي" and "أمريكية" in cat) or (market_filter == "سعودي" and "سعودية" in cat):
            all_stocks.extend(stocks)

    total = len(all_stocks)
    for idx, stock in enumerate(all_stocks[:20]):  # Limit for performance
        ticker = stock['ticker']
        try:
            hist, info = get_stock_data(ticker, "1mo", "1h")
            if hist is not None and not hist.empty and len(hist) >= 30:
                hist = calculate_technical_indicators(hist)

                structure = detect_market_structure(hist)
                fvgs = detect_fvg(hist)
                obs = detect_order_blocks(hist)
                pd_zone, pd_pct, _ = calculate_premium_discount(hist)

                current = hist['Close'].iloc[-1]

                # Filters
                fresh_fvgs = [f for f in fvgs if f['status'] == 'FRESH']
                if require_fvg and not fresh_fvgs:
                    continue
                if require_zone != "الكل" and pd_zone != require_zone:
                    continue

                # Calculate potential R:R
                rr = None
                if fresh_fvgs and obs:
                    target = fresh_fvgs[-1]['top'] if fresh_fvgs[-1]['type'] == 'BULLISH' else fresh_fvgs[-1]['bottom']
                    stop = obs[-1]['bottom'] if obs[-1]['type'] == 'BULLISH' else obs[-1]['top']
                    if stop != current:
                        rr = abs(target - current) / abs(stop - current)

                if rr and rr < min_rr:
                    continue

                # Auto rating
                rating = 0
                if structure:
                    rating += 1
                if fresh_fvgs:
                    rating += 1
                if pd_zone in ['PREMIUM', 'DISCOUNT']:
                    rating += 1
                if len([o for o in obs if o['status'] == 'ACTIVE']) > 0:
                    rating += 1

                if rating >= min_rating:
                    results.append({
                        'الرمز': ticker,
                        'الاسم': stock['name'],
                        'السعر': f"{'ر.س' if ticker.endswith('.SR') else '$'}{current:.2f}",
                        'التقييم': '⭐' * rating,
                        'المنطقة': f"{pd_zone} ({pd_pct:.0f}%)",
                        'FVGs': len(fresh_fvgs),
                        'OBs': len([o for o in obs if o['status'] == 'ACTIVE']),
                        'R:R': f"1:{rr:.1f}" if rr else "—",
                        'القطاع': stock['sector']
                    })
        except:
            pass

        progress_bar.progress((idx + 1) / min(total, 20))

    progress_bar.empty()

    render_section_header(f"النتائج ({len(results)} سهم)", "📋")

    if results:
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True, hide_index=True)
    else:
        st.warning("لا توجد أسهم مطابقة")
