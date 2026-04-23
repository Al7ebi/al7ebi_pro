import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from utils import (
    apply_custom_css, render_header, render_section_header, render_metric_card, render_ict_zone,
    STOCKS_DATA, TIMEFRAMES, get_stock_data, calculate_technical_indicators,
    detect_market_structure, detect_fvg, detect_order_blocks, detect_liquidity_levels,
    detect_unicorn_model, calculate_ote_zone, 
    get_kill_zone_status, get_session_countdown, get_ny_time,
    calculate_premium_discount, get_premium_discount_signal,
    get_smt_divergence, calculate_position_size, calculate_risk_reward,
    calculate_ict_rating, ict_smart_scanner,
    get_ticker_tape_data, get_rating_from_storage, save_rating,
    get_target_from_storage, save_target, format_number, get_all_stocks_flat, RATING_LABELS
)

st.set_page_config(
    page_title="ICT محلل الأسهم الاحترافي | Al7ebi Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# Session state init
for key in ['ratings', 'targets', 'selected_stock', 'selected_timeframe', 'account_balance', 'risk_percent', 'hide_non_kz']:
    if key not in st.session_state:
        st.session_state[key] = {} if key in ['ratings', 'targets'] else (10000 if key == 'account_balance' else (1 if key == 'risk_percent' else (False if key == 'hide_non_kz' else ('D1' if key == 'selected_timeframe' else None))))

# ============ TOP BAR: TICKER TAPE + KILL ZONE COUNTDOWN ============
active_kz, next_kz, ny_now = get_kill_zone_status()
session_name, countdown = get_session_countdown()

# Ticker Tape
ticker_data = get_ticker_tape_data()
ticker_html = ""
for name, data in ticker_data.items():
    color = "up" if data['change'] >= 0 else "down"
    arrow = "▲" if data['change'] >= 0 else "▼"
    ticker_html += f'<span class="ticker-item {color}">{name}: {data["price"]:.2f} {arrow} {abs(data["change"]):.2f}%</span>'

st.markdown(f"""
<div class="ticker-tape">
    <div style="animation: scroll 30s linear infinite; display: inline-block;">
        {ticker_html}
    </div>
</div>
<style>
@keyframes scroll {{
    0% {{ transform: translateX(100%); }}
    100% {{ transform: translateX(-100%); }}
}}
</style>
""", unsafe_allow_html=True)

# Kill Zone Status Bar
col_kz1, col_kz2, col_kz3, col_kz4 = st.columns([2, 2, 2, 2])
with col_kz1:
    kz_status = "🔥 نشطة" if active_kz else "⏳ غير نشطة"
    kz_color = "#fbbf24" if active_kz else "#64748b"
    st.markdown(f"""
    <div style="background: rgba(30,41,59,0.8); border-radius: 12px; padding: 12px; text-align: center;">
        <p style="color: #64748b; font-size: 0.75rem; margin: 0;">Kill Zones</p>
        <p style="color: {kz_color}; font-weight: 700; font-size: 1rem; margin: 4px 0 0 0;">{kz_status}</p>
    </div>
    """, unsafe_allow_html=True)

with col_kz2:
    hours, remainder = divmod(int(countdown.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    st.markdown(f"""
    <div class="countdown-box">
        <p style="color: #64748b; font-size: 0.7rem; margin: 0;">العد التنازلي لـ {session_name}</p>
        <p class="countdown-value">{hours:02d}:{minutes:02d}:{seconds:02d}</p>
    </div>
    """, unsafe_allow_html=True)

with col_kz3:
    st.markdown(f"""
    <div style="background: rgba(30,41,59,0.8); border-radius: 12px; padding: 12px; text-align: center;">
        <p style="color: #64748b; font-size: 0.75rem; margin: 0;">توقيت نيويورك</p>
        <p style="color: #60a5fa; font-weight: 700; font-size: 1rem; margin: 4px 0 0 0;">{ny_now.strftime('%H:%M:%S')} EST</p>
    </div>
    """, unsafe_allow_html=True)

with col_kz4:
    silver_bullet = "🔥 نشط" if any(z['name'] in ['London Kill Zone', 'New York Kill Zone'] for z in active_kz) else "❌ غير نشط"
    sb_color = "#fbbf24" if "🔥" in silver_bullet else "#64748b"
    st.markdown(f"""
    <div style="background: rgba(30,41,59,0.8); border-radius: 12px; padding: 12px; text-align: center;">
        <p style="color: #64748b; font-size: 0.75rem; margin: 0;">Silver Bullet Window</p>
        <p style="color: {sb_color}; font-weight: 700; font-size: 1rem; margin: 4px 0 0 0;">{silver_bullet}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <div style="font-size: 3rem; margin-bottom: 10px;">📈</div>
        <h2 style="color: #f8fafc; margin: 0; font-weight: 800;">Al7ebi Pro</h2>
        <p style="color: #64748b; font-size: 0.85rem; margin-top: 4px;">ICT محلل الأسهم الاحترافي</p>
        <p style="color: #3b82f6; font-size: 0.7rem; margin-top: 2px;">Inner Circle Trader Methodology</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 🧭 التنقل")
    page = st.radio("", [
        "🏠 الرئيسية - ICT Analysis",
        "🔍 Smart Scanner",
        "📊 السوق",
        "⭐ قائمة المتابعة",
        "⚙️ الإعدادات"
    ], label_visibility="collapsed")

    st.markdown("---")

    # Account Settings
    st.markdown("### 💰 إعدادات الحساب")
    st.session_state['account_balance'] = st.number_input("رصيد الحساب ($)", value=st.session_state['account_balance'], min_value=100, step=100)
    st.session_state['risk_percent'] = st.slider("نسبة المخاطرة (%)", 0.5, 5.0, st.session_state['risk_percent'], 0.5)

    st.markdown("---")

    # Theme Toggle
    st.markdown("### 🎨 الثيم")
    theme = st.selectbox("اختر الثيم", ["Dark (افتراضي)", "Light", "Midnight"])

    st.markdown("---")

    # Quick Stats
    total_rated = len(st.session_state['ratings'])
    total_targets = len(st.session_state['targets'])
    st.markdown(f"""
    <div style="background: rgba(30,41,59,0.6); border-radius: 12px; padding: 16px;">
        <p style="color: #64748b; font-size: 0.8rem; margin-bottom: 8px;">📊 إحصائيات ICT</p>
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

# ============ HOME PAGE - ICT ANALYSIS ============
if page == "🏠 الرئيسية - ICT Analysis":
    render_header("ICT محلل الأسهم الاحترافي", 
                  "Inner Circle Trader • Smart Money Concepts • Precision Analysis")

    # Top Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("إجمالي الأسهم", "60", icon="📊")
    with col2:
        render_metric_card("نماذج ICT", "15+", icon="🎯")
    with col3:
        render_metric_card("الفريمات", "13", icon="⏱️")
    with col4:
        avg_rating = np.mean(list(st.session_state['ratings'].values())) if st.session_state['ratings'] else 0
        render_metric_card("متوسط التقييم", f"{avg_rating:.1f}/5", icon="⭐")

    st.markdown("<br>", unsafe_allow_html=True)

    # Controls
    col_stock, col_tf, col_period, col_hide = st.columns([3, 1, 1, 1])

    with col_stock:
        all_stocks = get_all_stocks_flat()
        stock_options = [f"{s['ticker']} - {s['name']} ({s['category'].split(' ')[0]})" for s in all_stocks]
        selected = st.selectbox("🔍 اختر السهم", stock_options, index=0)
        selected_ticker = selected.split(' - ')[0]
        selected_stock = next(s for s in all_stocks if s['ticker'] == selected_ticker)

    with col_tf:
        tf_display = list(TIMEFRAMES.keys())
        selected_tf = st.selectbox("الفريم", tf_display, index=9)
        st.session_state['selected_timeframe'] = selected_tf

    with col_period:
        period = st.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

    with col_hide:
        st.session_state['hide_non_kz'] = st.toggle("إخفاء خارج KZ", value=st.session_state['hide_non_kz'])

    # Load Data
    with st.spinner("🔬 جاري التحليل ICT..."):
        hist, info = get_stock_data(selected_ticker, period, TIMEFRAMES[selected_tf])

    if hist is not None and not hist.empty:
        hist = calculate_technical_indicators(hist)

        # ICT Detection
        structure_events = detect_market_structure(hist)
        fvgs = detect_fvg(hist)
        obs = detect_order_blocks(hist)
        liquidity = detect_liquidity_levels(hist)
        unicorns = detect_unicorn_model(obs, fvgs)

        # Premium/Discount
        pd_zone, pd_pct, pd_levels = calculate_premium_discount(hist)

        # SMT Divergence
        index_map = {'NDX': '^IXIC', 'SPX': '^GSPC', 'TASI': '^TASI.SR'}
        index_ticker = index_map.get(selected_stock.get('index', 'SPX'), '^GSPC')
        smt_divergence = get_smt_divergence(selected_ticker, index_ticker)

        # Auto Rating
        rating, rating_reasons = calculate_ict_rating(
            structure_events, fvgs, obs, unicorns, 
            len(active_kz) > 0, (pd_zone, pd_pct, pd_levels), smt_divergence
        )

        current_price = hist['Close'].iloc[-1]
        is_saudi = selected_ticker.endswith('.SR')
        currency = "ر.س" if is_saudi else "$"

        # ============ PRICE HEADER WITH PREMIUM/DISCOUNT ============
        pd_color = "#f472b6" if pd_zone == "PREMIUM" else "#22c55e" if pd_zone == "DISCOUNT" else "#94a3b8"
        pd_icon = "🔴" if pd_zone == "PREMIUM" else "🟢" if pd_zone == "DISCOUNT" else "⚪"

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(147,51,234,0.1));
                     border: 1px solid rgba(59,130,246,0.3); border-radius: 20px; padding: 24px; margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <h2 style="margin: 0; color: #f8fafc; font-size: 1.8rem; font-weight: 800;">
                        {selected_ticker}
                    </h2>
                    <p style="color: #94a3b8; margin: 4px 0 0 0;">
                        {info.get('longName', selected_ticker) if info else selected_ticker} | {selected_stock['sector']}
                    </p>
                    <p style="color: #3b82f6; margin: 2px 0 0 0; font-size: 0.85rem;">
                        الفريم: {selected_tf} | التقلب: {selected_stock['volatility']}
                    </p>
                </div>
                <div style="text-align: left;">
                    <div style="font-size: 2.5rem; font-weight: 900; color: #f8fafc;">
                        {currency}{current_price:.2f}
                    </div>
                    <div style="color: {pd_color}; font-weight: 700; font-size: 1rem;">
                        {pd_icon} {pd_zone} ({pd_pct:.0f}%)
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Auto Rating Display
        if rating > 0:
            stars = "⭐" * rating + "☆" * (5 - rating)
            rating_color = "#22c55e" if rating >= 4 else "#eab308" if rating >= 3 else "#f97316"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {rating_color}20, {rating_color}10);
                        border: 2px solid {rating_color}50; border-radius: 16px; padding: 16px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: {rating_color}; font-size: 1.5rem;">{stars}</span>
                        <span style="color: {rating_color}; font-weight: 700; margin-right: 12px;">تقييم ICT: {rating}/5</span>
                    </div>
                    <span style="color: #64748b; font-size: 0.8rem;">{'عالية الاحتمالية' if rating >= 4 else 'متوسطة' if rating >= 3 else 'ضعيفة'}</span>
                </div>
                <div style="margin-top: 8px; color: #94a3b8; font-size: 0.85rem;">
                    {' | '.join(rating_reasons)}
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
            st.metric("P/E", f"{pe:.2f}" if pe else "—")

        # SMT Divergence Alert
        if smt_divergence:
            for div in smt_divergence:
                div_color = "#22c55e" if div['type'] == 'BULLISH' else "#ef4444"
                st.markdown(f"""
                <div style="background: {div_color}15; border: 1px solid {div_color}40; 
                            border-radius: 12px; padding: 12px; margin: 12px 0;">
                    <span style="color: {div_color}; font-weight: 700;">🔄 SMT Divergence Detected!</span>
                    <span style="color: #94a3b8; font-size: 0.85rem;"> {div['description']}</span>
                </div>
                """, unsafe_allow_html=True)

        # ============ TABS ============
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 الشارت ICT",
            "🎯 FVGs",
            "🏛️ Order Blocks",
            "💧 Liquidity",
            "📊 MTF Dashboard",
            "⭐ التقييم + Risk Mgmt"
        ])

        # TAB 1: CHART
        with tab1:
            col_chart, col_zones = st.columns([3, 1])

            with col_chart:
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                   vertical_spacing=0.08, row_heights=[0.7, 0.3])

                fig.add_trace(go.Candlestick(
                    x=hist.index, open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'],
                    name='الشمعداني',
                    increasing_line_color='#22c55e',
                    decreasing_line_color='#ef4444'
                ), row=1, col=1)

                # Premium/Discount zones
                if pd_levels:
                    high, mid, low = pd_levels
                    fig.add_hrect(y0=mid, y1=high, fillcolor="rgba(244,114,182,0.1)", 
                                 line_width=0, opacity=0.5, row=1, col=1)
                    fig.add_hrect(y0=low, y1=mid, fillcolor="rgba(34,197,94,0.1)", 
                                 line_width=0, opacity=0.5, row=1, col=1)
                    fig.add_hline(y=mid, line_dash="dash", line_color="rgba(255,255,255,0.3)", 
                                 line_width=1, row=1, col=1)

                # FVGs
                show_mitigated = st.checkbox("إظهار FVGs المغلقة", value=False)
                for fvg in fvgs:
                    if fvg['status'] == 'MITIGATED' and not show_mitigated:
                        continue
                    color = 'rgba(34,197,94,0.2)' if fvg['type'] == 'BULLISH' else 'rgba(239,68,68,0.2)'
                    fig.add_hrect(y0=fvg['bottom'], y1=fvg['top'], 
                                 fillcolor=color, line_width=0, opacity=0.4, row=1, col=1)

                # Volume
                colors = ['#22c55e' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] else '#ef4444' 
                         for i in range(len(hist))]
                fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='الحجم', 
                                    marker_color=colors, opacity=0.6), row=2, col=1)

                fig.update_layout(
                    title=f"ICT Analysis - {selected_ticker} ({selected_tf})",
                    xaxis_rangeslider_visible=False,
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=600,
                    font=dict(family="Tajawal"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_zones:
                st.markdown("### 🎯 مناطق ICT النشطة")

                if unicorns:
                    st.markdown("#### 🦄 Unicorn Models")
                    for u in unicorns[-2:]:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, rgba(168,85,247,0.2), rgba(236,72,153,0.1));
                                    border: 2px solid rgba(168,85,247,0.5); border-radius: 12px; padding: 12px; margin-bottom: 8px;">
                            <div style="color: #c084fc; font-weight: 700;">🦄 Unicorn Model</div>
                            <div style="color: #e9d5ff; font-size: 0.8rem;">
                                {currency}{u['overlap_bottom']:.2f} - {currency}{u['overlap_top']:.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                fresh_fvgs = [f for f in fvgs if f['status'] == 'FRESH']
                if fresh_fvgs:
                    st.markdown("#### ⚡ FVGs جديدة")
                    for f in fresh_fvgs[-3:]:
                        render_ict_zone(f"FVG {f['type']}", f, status='FRESH')

                active_obs = [o for o in obs if o['status'] == 'ACTIVE']
                if active_obs:
                    st.markdown("#### 🏛️ Order Blocks")
                    for o in active_obs[-3:]:
                        render_ict_zone(f"OB {o['type']}", o, status='ACTIVE')

        # TAB 2: FVGs
        with tab2:
            render_section_header("Fair Value Gaps - التحليل التفصيلي", "🎯")
            col_fvg_stats, col_fvg_list = st.columns([1, 2])

            with col_fvg_stats:
                total = len(fvgs)
                fresh = len([f for f in fvgs if f['status'] == 'FRESH'])
                partial = len([f for f in fvgs if f['status'] == 'PARTIAL'])
                mitigated = len([f for f in fvgs if f['status'] == 'MITIGATED'])

                render_metric_card("إجمالي FVGs", str(total), icon="🎯")
                render_metric_card("جديدة", str(fresh), icon="⚡")
                render_metric_card("جزئية", str(partial), icon="🟡")
                render_metric_card("مغلقة", str(mitigated), icon="✅")

            with col_fvg_list:
                if fvgs:
                    for fvg in reversed(fvgs[-10:]):
                        status_color = {'FRESH': '#22c55e', 'PARTIAL': '#eab308', 'MITIGATED': '#64748b'}.get(fvg['status'], '#94a3b8')
                        st.markdown(f"""
                        <div style="background: rgba(30,41,59,0.8); border: 1px solid {status_color}40; 
                                    border-radius: 12px; padding: 12px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: {status_color}; font-weight: 700;">
                                    {'🟢' if fvg['type'] == 'BULLISH' else '🔴'} {fvg['type']} FVG
                                </span>
                                <span style="color: #64748b; font-size: 0.8rem;">{fvg['status']}</span>
                            </div>
                            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                                النطاق: {currency}{fvg['bottom']:.2f} - {currency}{fvg['top']:.2f} | CE: {currency}{fvg['ce']:.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # TAB 3: Order Blocks
        with tab3:
            render_section_header("Order Blocks & Breaker Blocks", "🏛️")
            col_ob_stats, col_ob_list = st.columns([1, 2])

            with col_ob_stats:
                render_metric_card("إجمالي OBs", str(len(obs)), icon="🏛️")
                render_metric_card("نشطة", str(len([o for o in obs if o['status'] == 'ACTIVE'])), icon="🟢")
                render_metric_card("Breaker", str(len([o for o in obs if o['status'] == 'BROKEN'])), icon="🔨")

            with col_ob_list:
                if obs:
                    for ob in reversed(obs[-10:]):
                        status_color = '#22c55e' if ob['status'] == 'ACTIVE' else '#f472b6'
                        st.markdown(f"""
                        <div style="background: rgba(30,41,59,0.8); border: 1px solid {status_color}40; 
                                    border-radius: 12px; padding: 12px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: {status_color}; font-weight: 700;">
                                    {'🟢' if ob['status'] == 'ACTIVE' else '🔨'} {ob['type']} OB
                                </span>
                                <span style="color: #64748b; font-size: 0.8rem;">{ob['status']}</span>
                            </div>
                            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                                {currency}{ob['bottom']:.2f} - {currency}{ob['top']:.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # TAB 4: Liquidity
        with tab4:
            render_section_header("Liquidity Analysis", "💧")

            if liquidity:
                bsl = [l for l in liquidity if l['type'] == 'BSL']
                ssl = [l for l in liquidity if l['type'] == 'SSL']

                col_liq1, col_liq2 = st.columns(2)
                with col_liq1:
                    st.markdown("### 🟢 Buy-Side Liquidity")
                    for l in bsl[-5:]:
                        distance = ((l['price'] - current_price) / current_price * 100) if current_price else 0
                        st.markdown(f"""
                        <div style="background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); 
                                    border-radius: 8px; padding: 8px; margin-bottom: 6px;">
                            <span style="color: #4ade80; font-weight: 700;">{currency}{l['price']:.2f}</span>
                            <span style="color: #64748b; font-size: 0.75rem;"> ({distance:+.2f}%)</span>
                        </div>
                        """, unsafe_allow_html=True)

                with col_liq2:
                    st.markdown("### 🔴 Sell-Side Liquidity")
                    for l in ssl[-5:]:
                        distance = ((current_price - l['price']) / current_price * 100) if current_price else 0
                        st.markdown(f"""
                        <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); 
                                    border-radius: 8px; padding: 8px; margin-bottom: 6px;">
                            <span style="color: #f87171; font-weight: 700;">{currency}{l['price']:.2f}</span>
                            <span style="color: #64748b; font-size: 0.75rem;"> ({distance:+.2f}%)</span>
                        </div>
                        """, unsafe_allow_html=True)

        # TAB 5: MTF Dashboard
        with tab5:
            render_section_header("Multi-Timeframe Dashboard", "📊")

            mtf_timeframes = ['D1', 'H4', 'H1', 'M15']
            mtf_cols = st.columns(len(mtf_timeframes))

            for idx, tf in enumerate(mtf_timeframes):
                with mtf_cols[idx]:
                    try:
                        mtf_hist, _ = get_stock_data(selected_ticker, "1mo", TIMEFRAMES[tf])
                        if mtf_hist is not None and not mtf_hist.empty:
                            mtf_hist = calculate_technical_indicators(mtf_hist)
                            mtf_structure = detect_market_structure(mtf_hist)
                            mtf_fvgs = detect_fvg(mtf_hist)
                            mtf_pd, mtf_pd_pct, _ = calculate_premium_discount(mtf_hist, lookback=20)

                            current_mtf = mtf_hist['Close'].iloc[-1]
                            prev_mtf = mtf_hist['Close'].iloc[-2] if len(mtf_hist) > 1 else current_mtf
                            change_mtf = ((current_mtf - prev_mtf) / prev_mtf * 100) if prev_mtf else 0

                            trend = "📈" if current_mtf > mtf_hist['SMA_50'].iloc[-1] else "📉"
                            fresh_count = len([f for f in mtf_fvgs if f['status'] == 'FRESH'])

                            pd_color_mtf = "#f472b6" if mtf_pd == "PREMIUM" else "#22c55e" if mtf_pd == "DISCOUNT" else "#94a3b8"

                            st.markdown(f"""
                            <div style="background: rgba(30,41,59,0.9); border: 1px solid rgba(59,130,246,0.2); 
                                        border-radius: 16px; padding: 16px; text-align: center;">
                                <h4 style="color: #60a5fa; margin: 0;">{tf}</h4>
                                <p style="color: #f8fafc; font-size: 1.3rem; font-weight: 800; margin: 8px 0;">
                                    {currency}{current_mtf:.2f}
                                </p>
                                <p style="color: {'#4ade80' if change_mtf >= 0 else '#f87171'}; font-size: 0.9rem;">
                                    {change_mtf:+.2f}%
                                </p>
                                <p style="color: {pd_color_mtf}; font-size: 0.8rem; margin: 4px 0;">
                                    {mtf_pd} ({mtf_pd_pct:.0f}%)
                                </p>
                                <p style="color: #94a3b8; font-size: 0.75rem;">
                                    {trend} {fresh_count} FVGs جديدة
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    except:
                        st.info(f"لا توجد بيانات لـ {tf}")

        # TAB 6: RATING + RISK MANAGEMENT
        with tab6:
            render_section_header("التقييم + إدارة المخاطر", "⭐")

            col_rating, col_risk = st.columns(2)

            with col_rating:
                st.markdown("### ⭐ تقييمك الشخصي")
                current_rating = get_rating_from_storage(selected_ticker)

                rating_cols = st.columns(5)
                for i, col in enumerate(rating_cols, 1):
                    with col:
                        if st.button(f"{'⭐' if current_rating >= i else '☆'}", 
                                   key=f"star_{i}_{selected_ticker}", use_container_width=True):
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

                # Target Price
                st.markdown("### 🎯 السعر المستهدف")
                current_target = get_target_from_storage(selected_ticker)
                target_input = st.number_input("الهدف", 
                    value=float(current_target) if current_target else float(current_price),
                    min_value=0.01, step=0.01, format="%.2f")
                if st.button("💾 حفظ الهدف", use_container_width=True):
                    save_target(selected_ticker, target_input)
                    st.success("تم الحفظ!")
                    st.rerun()

            with col_risk:
                st.markdown("### 🛡️ حاسبة إدارة المخاطر")

                # Find nearest OB for stop loss suggestion
                suggested_stop = None
                if obs:
                    active_obs = [o for o in obs if o['status'] == 'ACTIVE']
                    if active_obs:
                        nearest = min(active_obs, key=lambda o: abs(o['bottom'] - current_price))
                        suggested_stop = nearest['bottom'] if nearest['type'] == 'BULLISH' else nearest['top']

                entry_price = st.number_input("سعر الدخول", value=float(current_price), format="%.2f")
                stop_loss = st.number_input("Stop Loss", 
                    value=float(suggested_stop) if suggested_stop else float(current_price * 0.98),
                    format="%.2f")

                if entry_price > 0 and stop_loss > 0:
                    pos = calculate_position_size(
                        st.session_state['account_balance'], 
                        st.session_state['risk_percent'],
                        entry_price, stop_loss, selected_ticker
                    )

                    if pos:
                        rr = None
                        if current_target:
                            rr = calculate_risk_reward(entry_price, stop_loss, current_target)

                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(147,51,234,0.1));
                                    border: 1px solid rgba(59,130,246,0.3); border-radius: 16px; padding: 20px;">
                            <div style="text-align: center;">
                                <p style="color: #64748b; font-size: 0.85rem;">عدد الأسهم/العقود</p>
                                <p style="color: #60a5fa; font-size: 2rem; font-weight: 800;">{pos['shares']:.0f}</p>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 12px;">
                                <div style="text-align: center;">
                                    <p style="color: #64748b; font-size: 0.75rem;">المخاطرة</p>
                                    <p style="color: #f87171; font-weight: 700;">${pos['risk_amount']:.2f}</p>
                                </div>
                                <div style="text-align: center;">
                                    <p style="color: #64748b; font-size: 0.75rem;">قيمة الصفقة</p>
                                    <p style="color: #f8fafc; font-weight: 700;">${pos['total_value']:.2f}</p>
                                </div>
                                <div style="text-align: center;">
                                    <p style="color: #64748b; font-size: 0.75rem;">R:R</p>
                                    <p style="color: {'#4ade80' if rr and rr >= 2 else '#eab308' if rr and rr >= 1 else '#f87171'}; font-weight: 700;">
                                        {f"1:{rr:.1f}" if rr else "—"}
                                    </p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if rr and rr < 1:
                            st.warning("⚠️ Risk:Reward أقل من 1:1 - الصفقة غير موصى بها")
                        elif rr and rr >= 3:
                            st.success("✅ Risk:Reward ممتاز (1:3+)")

            # OTE Zone
            if len(hist) > 50:
                swing_high = hist['High'].iloc[-50:].max()
                swing_low = hist['Low'].iloc[-50:].min()
                trend = 'bullish' if current_price > hist['SMA_50'].iloc[-1] else 'bearish'
                ote = calculate_ote_zone(swing_high, swing_low, trend)

                st.markdown("---")
                st.markdown("### 🎯 Optimal Trade Entry (OTE) Zone")
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(147,51,234,0.1));
                            border: 1px solid rgba(59,130,246,0.3); border-radius: 16px; padding: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span style="color: #94a3b8;">الاتجاه:</span>
                        <span style="color: {'#22c55e' if trend == 'bullish' else '#ef4444'}; font-weight: 700;">
                            {'📈 صعودي' if trend == 'bullish' else '📉 هبوطي'}
                        </span>
                    </div>
                    <div style="background: rgba(15,23,42,0.6); border-radius: 12px; padding: 16px; text-align: center;">
                        <p style="color: #64748b; font-size: 0.85rem; margin-bottom: 8px;">نطاق OTE (62% - 79% Fib)</p>
                        <p style="color: #60a5fa; font-weight: 800; font-size: 1.8rem;">
                            {currency}{ote['bottom']:.2f} - {currency}{ote['top']:.2f}
                        </p>
                        <p style="color: #a78bfa; font-size: 0.9rem; margin-top: 4px;">المنتصف: {currency}{ote['mid']:.2f}</p>
                    </div>
                    <p style="color: #64748b; font-size: 0.75rem; margin-top: 12px; text-align: center;">
                        💡 نصيحة ICT: ادخل عند منتصف OTE أو عند تقاطع FVG داخل النطاق
                    </p>
                </div>
                """, unsafe_allow_html=True)

# ============ SMART SCANNER PAGE ============
elif page == "🔍 Smart Scanner":
    render_header("Smart Scanner", "مسح السوق لأفضل فرص ICT")

    col_scan1, col_scan2 = st.columns([1, 3])

    with col_scan1:
        st.markdown("### 🔧 إعدادات المسح")
        min_rating = st.slider("الحد الأدنى للتقييم", 1, 5, 3)
        scan_market = st.selectbox("السوق", ["الكل", "🇺🇸 أمريكي", "🇸🇦 سعودي"])

        if st.button("🔍 بدء المسح", use_container_width=True):
            with st.spinner("جاري مسح السوق..."):
                scan_stocks = get_all_stocks_flat()
                if scan_market != "الكل":
                    scan_stocks = [s for s in scan_stocks if ("أمريكية" in s['category'] if scan_market == "🇺🇸 أمريكي" else "سعودية" in s['category'])]

                opportunities = ict_smart_scanner(
                    scan_stocks, 
                    st.session_state['account_balance'],
                    st.session_state['risk_percent']
                )

                st.session_state['scan_results'] = [o for o in opportunities if o['rating'] >= min_rating]

    with col_scan2:
        if 'scan_results' in st.session_state and st.session_state['scan_results']:
            st.markdown(f"### 📊 النتائج ({len(st.session_state['scan_results'])} فرصة)")

            for opp in st.session_state['scan_results'][:10]:
                stars = "⭐" * opp['rating'] + "☆" * (5 - opp['rating'])
                zone_color = "#f472b6" if opp['zone'] == "PREMIUM" else "#22c55e" if opp['zone'] == "DISCOUNT" else "#94a3b8"

                st.markdown(f"""
                <div style="background: rgba(30,41,59,0.9); border: 1px solid rgba(59,130,246,0.3); 
                            border-radius: 16px; padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #f8fafc; font-weight: 800; font-size: 1.2rem;">{opp['name']} ({opp['ticker']})</span>
                            <span style="color: #fbbf24; margin-right: 8px;">{stars}</span>
                        </div>
                        <span style="color: {zone_color}; font-size: 0.9rem; font-weight: 600;">
                            {opp['zone']} ({opp['zone_pct']:.0f}%)
                        </span>
                    </div>
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 8px;">
                        {' | '.join(opp['reasons'])}
                    </div>
                    <div style="display: flex; gap: 16px; margin-top: 8px;">
                        <span style="color: #60a5fa;">السعر: {currency if opp['ticker'].endswith('.SR') else '$'}{opp['price']:.2f}</span>
                        {f'<span style="color: #4ade80;">الهدف: {currency if opp["ticker"].endswith(".SR") else "$"}{opp["target"]:.2f}</span>' if opp['target'] else ''}
                        {f'<span style="color: #f87171;">الستوب: {currency if opp["ticker"].endswith(".SR") else "$"}{opp["stop"]:.2f}</span>' if opp['stop'] else ''}
                        {f'<span style="color: #a78bfa;">الكمية: {opp["position_size"]["shares"]:.0f}</span>' if opp['position_size'] else ''}
                    </div>
                    {f'<div style="margin-top: 8px;"><span style="background: rgba(168,85,247,0.2); color: #c084fc; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem;">🦄 Unicorn Detected</span></div>' if opp['unicorn'] else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("اضغط 'بدء المسح' للعثور على أفضل فرص ICT في السوق")

# ============ MARKET PAGE ============
elif page == "📊 السوق":
    render_header("سوق الأسهم", "تصفح وقارن بين الأسهم")

    col_filter, col_sector = st.columns([2, 1])
    with col_filter:
        market_filter = st.selectbox("🏳️ السوق", ["الكل", "🇺🇸 أمريكي", "🇸🇦 سعودي"])
    with col_sector:
        sector_filter = st.selectbox("🏭 القطاع", ["الكل", "تكنولوجيا", "بنوك", "طاقة", "رعاية صحية", 
                                                  "سلع استهلاكية", "تجارة", "صناعة", "غذاء", "اتصالات"])

    filtered_stocks = []
    for cat, stocks in STOCKS_DATA.items():
        if market_filter == "الكل" or (market_filter == "🇺🇸 أمريكي" and "أمريكية" in cat) or (market_filter == "🇸🇦 سعودي" and "سعودية" in cat):
            for s in stocks:
                if sector_filter == "الكل" or s['sector'] == sector_filter:
                    filtered_stocks.append(s)

    if filtered_stocks:
        cols = st.columns(3)
        for idx, stock in enumerate(filtered_stocks):
            with cols[idx % 3]:
                ticker = stock['ticker']
                hist_s, info_s = get_stock_data(ticker, "5d")

                price = "—"
                change = "—"
                change_color = "#94a3b8"
                sparkline_data = []

                if hist_s is not None and not hist_s.empty and len(hist_s) >= 2:
                    p = hist_s['Close'].iloc[-1]
                    prev = hist_s['Close'].iloc[-2]
                    ch = ((p - prev) / prev * 100)
                    is_saudi = ticker.endswith('.SR')
                    price = f"{'ر.س' if is_saudi else '$'}{p:.2f}"
                    change = f"{'+' if ch >= 0 else ''}{ch:.2f}%"
                    change_color = "#4ade80" if ch >= 0 else "#f87171"
                    sparkline_data = hist_s['Close'].values[-20:]

                rating = get_rating_from_storage(ticker)
                stars = "⭐" * rating + "☆" * (5 - rating) if rating else "غير مقيّم"

                st.markdown(f"""
                <div class="stock-card" style="cursor: pointer;">
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

                if st.button(f"تحليل ICT {ticker}", key=f"btn_{ticker}", use_container_width=True):
                    st.session_state['selected_stock'] = ticker
                    st.rerun()
    else:
        st.info("لا توجد أسهم مطابقة")

# ============ WATCHLIST PAGE ============
elif page == "⭐ قائمة المتابعة":
    render_header("قائمة المتابعة", "الأسهم المقيّمة")

    rated_stocks = []
    for stock in get_all_stocks_flat():
        ticker = stock['ticker']
        if ticker in st.session_state['ratings'] or ticker in st.session_state['targets']:
            rated_stocks.append(stock)

    if rated_stocks:
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("عدد المقيّمة", str(len(st.session_state['ratings'])), icon="⭐")
        with col2:
            render_metric_card("عدد الأهداف", str(len(st.session_state['targets'])), icon="🎯")
        with col3:
            buy_count = sum(1 for r in st.session_state['ratings'].values() if r >= 4)
            render_metric_card("توصيات شراء", str(buy_count), icon="🟢")

        st.markdown("<br>", unsafe_allow_html=True)

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
        st.dataframe(df_watchlist, use_container_width=True, hide_index=True)
    else:
        st.info("لم تقم بتقييم أي سهم بعد")

# ============ SETTINGS PAGE ============
elif page == "⚙️ الإعدادات":
    render_header("الإعدادات", "إدارة البيانات")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🗑️ إدارة البيانات")
        if st.button("🗑️ مسح التقييمات", use_container_width=True):
            st.session_state['ratings'] = {}
            st.success("تم المسح!")
            st.rerun()
        if st.button("🗑️ مسح الأهداف", use_container_width=True):
            st.session_state['targets'] = {}
            st.success("تم المسح!")
            st.rerun()
        if st.button("🗑️ مسح كل البيانات", use_container_width=True):
            st.session_state['ratings'] = {}
            st.session_state['targets'] = {}
            st.success("تم المسح!")
            st.rerun()

    with col2:
        st.markdown("### 📊 إحصائيات")
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.6); border-radius: 16px; padding: 20px;">
            <div style="margin-bottom: 12px;">
                <span style="color: #94a3b8;">التقييمات:</span>
                <span style="color: #60a5fa; font-weight: 700; float: left;">{len(st.session_state['ratings'])}</span>
            </div>
            <div style="margin-bottom: 12px;">
                <span style="color: #94a3b8;">الأهداف:</span>
                <span style="color: #a78bfa; font-weight: 700; float: left;">{len(st.session_state['targets'])}</span>
            </div>
            <div>
                <span style="color: #94a3b8;">المتابعة:</span>
                <span style="color: #22c55e; font-weight: 700; float: left;">{len(rated_stocks)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #64748b;">
        <p>📈 Al7ebi Pro ICT v3.0</p>
        <p style="font-size: 0.8rem;">Inner Circle Trader Methodology | Michael Huddleston Concepts</p>
    </div>
    """, unsafe_allow_html=True)
