import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from utils import (
    apply_custom_css, render_header, render_section_header, render_metric_card,
    STOCKS_DATA, get_stock_data, calculate_technical_indicators,
    get_rating_from_storage, save_rating, get_target_from_storage, save_target,
    format_number, get_all_stocks_flat, RATING_LABELS
)

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="محلل الأسهم الاحترافي | Al7ebi Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ INIT ============
apply_custom_css()

if 'ratings' not in st.session_state:
    st.session_state['ratings'] = {}
if 'targets' not in st.session_state:
    st.session_state['targets'] = {}
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = []
if 'selected_stock' not in st.session_state:
    st.session_state['selected_stock'] = None

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <div style="font-size: 3rem; margin-bottom: 10px;">📈</div>
        <h2 style="color: #f8fafc; margin: 0; font-weight: 800;">Al7ebi Pro</h2>
        <p style="color: #64748b; font-size: 0.85rem; margin-top: 4px;">محلل الأسهم الاحترافي</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    st.markdown("### 🧭 التنقل")
    page = st.radio("", [
        "🏠 الرئيسية",
        "📊 السوق",
        "⭐ قائمة المتابعة",
        "⚙️ الإعدادات"
    ], label_visibility="collapsed")

    st.markdown("---")

    # Market Status
    st.markdown("""
    <div class="status-live">
        <div class="status-dot"></div>
        <span>السوق مفتوح</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Stats
    total_rated = len(st.session_state['ratings'])
    total_targets = len(st.session_state['targets'])
    st.markdown(f"""
    <div style="background: rgba(30,41,59,0.6); border-radius: 12px; padding: 16px;">
        <p style="color: #64748b; font-size: 0.8rem; margin-bottom: 8px;">📊 إحصائيات سريعة</p>
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
            <span style="color: #94a3b8; font-size: 0.85rem;">مقيّم:</span>
            <span style="color: #60a5fa; font-weight: 700;">{total_rated}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color: #94a3b8; font-size: 0.85rem;">أهداف:</span>
            <span style="color: #a78bfa; font-weight: 700;">{total_targets}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============ HOME PAGE ============
if page == "🏠 الرئيسية":
    render_header("محلل الأسهم الاحترافي", "تحليل فني متقدم • تقييم ذكي • متابعة مباشرة")

    # Top Stats Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("إجمالي الأسهم", "60", icon="📊")
    with col2:
        render_metric_card("الأسهم الأمريكية", "30", icon="🇺🇸")
    with col3:
        render_metric_card("الأسهم السعودية", "30", icon="🇸🇦")
    with col4:
        avg_rating = np.mean(list(st.session_state['ratings'].values())) if st.session_state['ratings'] else 0
        render_metric_card("متوسط التقييم", f"{avg_rating:.1f}/5", icon="⭐")

    st.markdown("<br>", unsafe_allow_html=True)

    # Featured Stock Analysis
    render_section_header("التحليل المباشر", "🔬")

    col_search, col_period = st.columns([3, 1])
    with col_search:
        all_stocks = get_all_stocks_flat()
        stock_options = [f"{s['ticker']} - {s['name']} ({s['category'].split(' ')[0]})" for s in all_stocks]
        selected = st.selectbox("🔍 اختر السهم للتحليل", stock_options, index=0)
        selected_ticker = selected.split(' - ')[0]
    with col_period:
        period = st.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

    # Load Data
    with st.spinner("جاري تحميل البيانات..."):
        hist, info = get_stock_data(selected_ticker, period)

    if hist is not None and not hist.empty:
        hist = calculate_technical_indicators(hist)
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price else 0

        # Price Header
        is_saudi = selected_ticker.endswith('.SR')
        currency = "ر.س" if is_saudi else "$"

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(147,51,234,0.1));
                     border: 1px solid rgba(59,130,246,0.3); border-radius: 20px; padding: 24px; margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <h2 style="margin: 0; color: #f8fafc; font-size: 1.8rem; font-weight: 800;">
                        {selected_ticker}
                    </h2>
                    <p style="color: #94a3b8; margin: 4px 0 0 0;">
                        {info.get('longName', selected_ticker) if info else selected_ticker}
                    </p>
                </div>
                <div style="text-align: left;">
                    <div style="font-size: 2.5rem; font-weight: 900; color: #f8fafc;">
                        {currency}{current_price:.2f}
                    </div>
                    <div style="color: {'#4ade80' if change_pct >= 0 else '#f87171'}; font-weight: 700; font-size: 1.1rem;">
                        {'▲' if change_pct >= 0 else '▼'} {abs(change_pct):.2f}%
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Key Metrics
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        with col_m1:
            st.metric("أعلى 52 أسبوع", f"{currency}{info.get('fiftyTwoWeekHigh', 0):.2f}" if info else "—")
        with col_m2:
            st.metric("أدنى 52 أسبوع", f"{currency}{info.get('fiftyTwoWeekLow', 0):.2f}" if info else "—")
        with col_m3:
            st.metric("حجم التداول", format_number(info.get('volume', 0)) if info else "—")
        with col_m4:
            st.metric("القيمة السوقية", format_number(info.get('marketCap', 0)) if info else "—")
        with col_m5:
            pe = info.get('trailingPE', None) if info else None
            st.metric("P/E Ratio", f"{pe:.2f}" if pe else "—")

        # Tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["📈 الشارت", "📊 المؤشرات الفنية", "⭐ التقييم والأهداف", "📋 المعلومات"])

        with tab1:
            # Candlestick Chart
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                               vertical_spacing=0.08, row_heights=[0.7, 0.3])

            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name='الشمعداني',
                increasing_line_color='#22c55e',
                decreasing_line_color='#ef4444'
            ), row=1, col=1)

            # Moving Averages
            fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], name='SMA 20', 
                                    line=dict(color='#60a5fa', width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_50'], name='SMA 50', 
                                    line=dict(color='#f472b6', width=1.5)), row=1, col=1)

            # Volume
            colors = ['#22c55e' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else '#ef4444' 
                     for i in range(len(hist))]
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='الحجم', 
                                marker_color=colors, opacity=0.6), row=2, col=1)

            fig.update_layout(
                title="",
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=600,
                font=dict(family="Tajawal, sans-serif"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            col_rsi, col_macd = st.columns(2)

            with col_rsi:
                # RSI Chart
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name='RSI',
                                            line=dict(color='#a78bfa', width=2)))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ef4444", annotation_text="Overbought")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="#22c55e", annotation_text="Oversold")
                fig_rsi.update_layout(
                    title="مؤشر القوة النسبية (RSI)", template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    height=350, font=dict(family="Tajawal")
                )
                st.plotly_chart(fig_rsi, use_container_width=True)

            with col_macd:
                # MACD Chart
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=hist.index, y=hist['MACD'], name='MACD',
                                             line=dict(color='#60a5fa', width=2)))
                fig_macd.add_trace(go.Scatter(x=hist.index, y=hist['MACD_Signal'], name='Signal',
                                             line=dict(color='#f472b6', width=2)))
                fig_macd.add_trace(go.Bar(x=hist.index, y=hist['MACD']-hist['MACD_Signal'], 
                                         name='Histogram', marker_color='#94a3b8', opacity=0.5))
                fig_macd.update_layout(
                    title="مؤشر MACD", template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    height=350, font=dict(family="Tajawal")
                )
                st.plotly_chart(fig_macd, use_container_width=True)

            # Bollinger Bands
            fig_bb = go.Figure()
            fig_bb.add_trace(go.Scatter(x=hist.index, y=hist['BB_Upper'], name='Upper Band',
                                       line=dict(color='#f472b6', width=1, dash='dash')))
            fig_bb.add_trace(go.Scatter(x=hist.index, y=hist['BB_Middle'], name='Middle Band',
                                       line=dict(color='#60a5fa', width=1.5)))
            fig_bb.add_trace(go.Scatter(x=hist.index, y=hist['BB_Lower'], name='Lower Band',
                                       line=dict(color='#f472b6', width=1, dash='dash')))
            fig_bb.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='السعر',
                                       line=dict(color='#f8fafc', width=2)))
            fig_bb.update_layout(
                title="نطاقات بولينجر (Bollinger Bands)", template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=400, font=dict(family="Tajawal")
            )
            st.plotly_chart(fig_bb, use_container_width=True)

            # Volatility
            latest_vol = hist['Volatility'].dropna().iloc[-1] if not hist['Volatility'].dropna().empty else 0
            st.markdown(f"""
            <div style="background: rgba(147,51,234,0.1); border: 1px solid rgba(147,51,234,0.3); 
                        border-radius: 12px; padding: 16px; margin-top: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #94a3b8;">📊 التقلب السنوي (الانحراف المعياري):</span>
                    <span style="color: #a78bfa; font-weight: 800; font-size: 1.3rem;">{latest_vol:.2f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab3:
            col_rating, col_target = st.columns(2)

            with col_rating:
                st.markdown("### ⭐ تقييمك للسهم")
                current_rating = get_rating_from_storage(selected_ticker)

                rating_cols = st.columns(5)
                for i, col in enumerate(rating_cols, 1):
                    with col:
                        is_active = current_rating >= i
                        btn_style = "background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #000;" if is_active else "background: rgba(30,41,59,0.8); color: #64748b;"
                        if st.button(f"{'⭐' if is_active else '☆'}", key=f"star_{i}_{selected_ticker}", 
                                    use_container_width=True):
                            save_rating(selected_ticker, i)
                            st.rerun()

                if current_rating > 0:
                    label, color = RATING_LABELS[current_rating]
                    st.markdown(f"""
                    <div style="text-align: center; padding: 12px; background: {color}20; 
                                border: 1px solid {color}50; border-radius: 12px; margin-top: 12px;">
                        <span style="color: {color}; font-weight: 700; font-size: 1.1rem;">{label}</span>
                    </div>
                    """, unsafe_allow_html=True)

            with col_target:
                st.markdown("### 🎯 السعر المستهدف")
                current_target = get_target_from_storage(selected_ticker)
                target_input = st.number_input("السعر المستهدف", 
                                              value=float(current_target) if current_target else float(current_price),
                                              min_value=0.01, step=0.01,
                                              format="%.2f")
                if st.button("💾 حفظ الهدف", use_container_width=True):
                    save_target(selected_ticker, target_input)
                    st.success("تم حفظ الهدف بنجاح!")
                    st.rerun()

                if current_target and current_price > 0:
                    expected_return = ((current_target - current_price) / current_price) * 100
                    ret_color = "#4ade80" if expected_return >= 0 else "#f87171"
                    st.markdown(f"""
                    <div style="text-align: center; padding: 12px; margin-top: 12px;">
                        <p style="color: #94a3b8; margin-bottom: 4px;">الربح المتوقع</p>
                        <p style="color: {ret_color}; font-weight: 800; font-size: 1.5rem;">
                            {'+' if expected_return >= 0 else ''}{expected_return:.2f}%
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

            # Confidence Interval
            if not hist.empty:
                std_30d = hist['Close'].pct_change().dropna().tail(30).std()
                if std_30d and not pd.isna(std_30d):
                    ci_upper = current_price * (1 + 1.96 * std_30d)
                    ci_lower = current_price * (1 - 1.96 * std_30d)
                    st.markdown(f"""
                    <div style="background: rgba(20,184,166,0.1); border: 1px solid rgba(20,184,166,0.3);
                                border-radius: 16px; padding: 20px; margin-top: 20px;">
                        <h4 style="color: #2dd4bf; margin-bottom: 12px;">📐 نطاق الثقة 95% (بناءً على 30 يوم)</h4>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="text-align: center;">
                                <p style="color: #94a3b8; font-size: 0.85rem;">الحد الأدنى</p>
                                <p style="color: #f87171; font-weight: 800; font-size: 1.3rem;">{currency}{ci_lower:.2f}</p>
                            </div>
                            <div style="flex: 1; margin: 0 20px; height: 4px; background: linear-gradient(90deg, #f87171, #fbbf24, #22c55e); border-radius: 2px; position: relative;">
                                <div style="position: absolute; left: 50%; top: -6px; transform: translateX(-50%); width: 16px; height: 16px; background: #f8fafc; border-radius: 50%; box-shadow: 0 0 10px rgba(255,255,255,0.3);"></div>
                            </div>
                            <div style="text-align: center;">
                                <p style="color: #94a3b8; font-size: 0.85rem;">الحد الأقصى</p>
                                <p style="color: #4ade80; font-weight: 800; font-size: 1.3rem;">{currency}{ci_upper:.2f}</p>
                            </div>
                        </div>
                        <p style="text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 8px;">
                            السعر الحالي: {currency}{current_price:.2f} (النقطة البيضاء = السعر الحالي)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

        with tab4:
            if info:
                col_info1, col_info2 = st.columns(2)

                with col_info1:
                    st.markdown("#### 📋 معلومات الشركة")
                    info_data = {
                        "الاسم الكامل": info.get('longName', '—'),
                        "القطاع": info.get('sector', '—'),
                        "الصناعة": info.get('industry', '—'),
                        "البلد": info.get('country', '—'),
                        "الموقع الإلكتروني": info.get('website', '—'),
                        "عدد الموظفين": format_number(info.get('fullTimeEmployees', 0)),
                    }
                    for k, v in info_data.items():
                        st.markdown(f"**{k}:** {v}")

                with col_info2:
                    st.markdown("#### 💰 البيانات المالية")
                    financial_data = {
                        "الإيرادات": format_number(info.get('totalRevenue', 0)),
                        "صافي الربح": format_number(info.get('netIncomeToCommon', 0)),
                        "هامش الربح": f"{info.get('profitMargins', 0)*100:.2f}%" if info.get('profitMargins') else "—",
                        "الديون/الأصول": f"{info.get('debtToEquity', 0):.2f}" if info.get('debtToEquity') else "—",
                        "العائد على حقوق الملكية": f"{info.get('returnOnEquity', 0)*100:.2f}%" if info.get('returnOnEquity') else "—",
                        "EPS": f"{info.get('trailingEps', 0):.2f}" if info.get('trailingEps') else "—",
                    }
                    for k, v in financial_data.items():
                        st.markdown(f"**{k}:** {v}")
            else:
                st.info("لا توجد معلومات تفصيلية متاحة لهذا السهم")

# ============ MARKET PAGE ============
elif page == "📊 السوق":
    render_header("سوق الأسهم", "تصفح وقارن بين الأسهم")

    # Filter
    col_filter, col_sector = st.columns([2, 1])
    with col_filter:
        market_filter = st.selectbox("🏳️ السوق", ["الكل", "🇺🇸 أمريكي", "🇸🇦 سعودي"])
    with col_sector:
        sector_filter = st.selectbox("🏭 القطاع", ["الكل", "تكنولوجيا", "بنوك", "طاقة", "رعاية صحية", 
                                                  "سلع استهلاكية", "تجارة", "صناعة", "غذاء", "اتصالات"])

    # Get filtered stocks
    filtered_stocks = []
    for cat, stocks in STOCKS_DATA.items():
        if market_filter == "الكل" or (market_filter == "🇺🇸 أمريكي" and "أمريكية" in cat) or (market_filter == "🇸🇦 سعودي" and "سعودية" in cat):
            for s in stocks:
                if sector_filter == "الكل" or s['sector'] == sector_filter:
                    filtered_stocks.append(s)

    # Display as cards
    if filtered_stocks:
        cols = st.columns(3)
        for idx, stock in enumerate(filtered_stocks):
            with cols[idx % 3]:
                ticker = stock['ticker']
                hist_s, info_s = get_stock_data(ticker, "5d")

                price = "—"
                change = "—"
                change_color = "#94a3b8"

                if hist_s is not None and not hist_s.empty and len(hist_s) >= 2:
                    p = hist_s['Close'].iloc[-1]
                    prev = hist_s['Close'].iloc[-2]
                    ch = ((p - prev) / prev * 100)
                    is_saudi = ticker.endswith('.SR')
                    price = f"{'ر.س' if is_saudi else '$'}{p:.2f}"
                    change = f"{'+' if ch >= 0 else ''}{ch:.2f}%"
                    change_color = "#4ade80" if ch >= 0 else "#f87171"

                rating = get_rating_from_storage(ticker)
                stars = "⭐" * rating + "☆" * (5 - rating) if rating else "غير مقيّم"

                st.markdown(f"""
                <div class="stock-card" style="cursor: pointer;" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: '{ticker}'}}, '*')">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                        <div>
                            <div style="font-weight: 800; color: #f8fafc; font-size: 1.1rem;">{stock['name']}</div>
                            <div style="color: #64748b; font-size: 0.85rem; font-family: monospace;">{ticker}</div>
                        </div>
                        <span style="background: rgba(59,130,246,0.2); color: #60a5fa; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem;">{stock['sector']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: end;">
                        <div>
                            <div style="font-size: 1.6rem; font-weight: 800; color: #f8fafc;">{price}</div>
                            <div style="color: {change_color}; font-weight: 600; font-size: 0.9rem;">{change}</div>
                        </div>
                        <div style="text-align: left;">
                            <div style="font-size: 1rem;">{stars}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"تحليل {ticker}", key=f"btn_{ticker}", use_container_width=True):
                    st.session_state['selected_stock'] = ticker
                    st.switch_page("Home.py")
    else:
        st.info("لا توجد أسهم مطابقة للفلاتر المحددة")

# ============ WATCHLIST PAGE ============
elif page == "⭐ قائمة المتابعة":
    render_header("قائمة المتابعة", "الأسهم التي قيّمتها وحددت أهدافها")

    rated_stocks = []
    for stock in get_all_stocks_flat():
        ticker = stock['ticker']
        if ticker in st.session_state['ratings'] or ticker in st.session_state['targets']:
            rated_stocks.append(stock)

    if rated_stocks:
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("عدد المقيّمة", str(len(st.session_state['ratings'])), icon="⭐")
        with col2:
            render_metric_card("عدد الأهداف", str(len(st.session_state['targets'])), icon="🎯")
        with col3:
            buy_count = sum(1 for r in st.session_state['ratings'].values() if r >= 4)
            render_metric_card("توصيات شراء", str(buy_count), icon="🟢")

        st.markdown("<br>", unsafe_allow_html=True)

        # Table
        watchlist_data = []
        for stock in rated_stocks:
            ticker = stock['ticker']
            hist_w, info_w = get_stock_data(ticker, "5d")

            price = "—"
            change = "—"
            if hist_w is not None and not hist_w.empty and len(hist_w) >= 2:
                p = hist_w['Close'].iloc[-1]
                prev = hist_w['Close'].iloc[-2]
                ch = ((p - prev) / prev * 100)
                is_saudi = ticker.endswith('.SR')
                price = f"{'ر.س' if is_saudi else '$'}{p:.2f}"
                change = f"{'+' if ch >= 0 else ''}{ch:.2f}%"

            rating = st.session_state['ratings'].get(ticker, 0)
            target = st.session_state['targets'].get(ticker, None)

            watchlist_data.append({
                'الرمز': ticker,
                'الاسم': stock['name'],
                'السوق': '🇸🇦 سعودي' if ticker.endswith('.SR') else '🇺🇸 أمريكي',
                'السعر': price,
                'التغيير': change,
                'التقييم': '⭐' * rating,
                'الهدف': f"{'ر.س' if ticker.endswith('.SR') else '$'}{target:.2f}" if target else "—",
                'القطاع': stock['sector']
            })

        df_watchlist = pd.DataFrame(watchlist_data)
        st.dataframe(df_watchlist, use_container_width=True, hide_index=True,
                    column_config={
                        'التقييم': st.column_config.TextColumn(width="medium"),
                        'التغيير': st.column_config.TextColumn(width="small")
                    })
    else:
        st.info("لم تقم بتقييم أي سهم بعد. اذهب إلى صفحة السوق وقيّم الأسهم التي تهمك!")
        st.markdown("""
        <div style="text-align: center; padding: 40px;">
            <div style="font-size: 4rem; margin-bottom: 16px;">⭐</div>
            <h3 style="color: #94a3b8;">ابدأ بإضافة تقييماتك</h3>
            <p style="color: #64748b;">قيّم الأسهم وحدد أهدافك لبناء قائمة متابعة شخصية</p>
        </div>
        """, unsafe_allow_html=True)

# ============ SETTINGS PAGE ============
elif page == "⚙️ الإعدادات":
    render_header("الإعدادات", "إدارة بياناتك وتفضيلاتك")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🗑️ إدارة البيانات")

        if st.button("🗑️ مسح جميع التقييمات", use_container_width=True):
            st.session_state['ratings'] = {}
            st.success("تم مسح التقييمات!")
            st.rerun()

        if st.button("🗑️ مسح جميع الأهداف", use_container_width=True):
            st.session_state['targets'] = {}
            st.success("تم مسح الأهداف!")
            st.rerun()

        if st.button("🗑️ مسح كل البيانات", use_container_width=True):
            st.session_state['ratings'] = {}
            st.session_state['targets'] = {}
            st.success("تم مسح كل البيانات!")
            st.rerun()

    with col2:
        st.markdown("### 📊 إحصائيات")
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.6); border-radius: 16px; padding: 20px;">
            <div style="margin-bottom: 12px;">
                <span style="color: #94a3b8;">التقييمات المحفوظة:</span>
                <span style="color: #60a5fa; font-weight: 700; float: left;">{len(st.session_state['ratings'])}</span>
            </div>
            <div style="margin-bottom: 12px;">
                <span style="color: #94a3b8;">الأهداف المحفوظة:</span>
                <span style="color: #a78bfa; font-weight: 700; float: left;">{len(st.session_state['targets'])}</span>
            </div>
            <div>
                <span style="color: #94a3b8;">قائمة المتابعة:</span>
                <span style="color: #22c55e; font-weight: 700; float: left;">{len([s for s in get_all_stocks_flat() if s['ticker'] in st.session_state['ratings'] or s['ticker'] in st.session_state['targets']])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #64748b;">
        <p>📈 Al7ebi Pro — محلل الأسهم الاحترافي</p>
        <p style="font-size: 0.8rem;">v2.0 | بني بـ Streamlit + Python</p>
    </div>
    """, unsafe_allow_html=True)
