import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from utils import (
    apply_custom_css, render_header, render_section_header, render_metric_card, render_ict_zone,
    STOCKS_DATA, TIMEFRAMES, get_stock_data, calculate_technical_indicators,
    detect_market_structure, detect_fvg, detect_order_blocks, detect_liquidity_levels,
    detect_unicorn_model, calculate_ote_zone, calculate_kill_zone_times,
    get_rating_from_storage, save_rating, get_target_from_storage, save_target,
    format_number, get_all_stocks_flat, RATING_LABELS, ICTConcepts
)

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="ICT محلل الأسهم الاحترافي | Al7ebi Pro",
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
if 'selected_stock' not in st.session_state:
    st.session_state['selected_stock'] = None
if 'selected_timeframe' not in st.session_state:
    st.session_state['selected_timeframe'] = 'D1'

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

    # Navigation
    st.markdown("### 🧭 التنقل")
    page = st.radio("", [
        "🏠 الرئيسية - ICT Analysis",
        "📊 السوق",
        "⭐ قائمة المتابعة",
        "⚙️ الإعدادات"
    ], label_visibility="collapsed")

    st.markdown("---")

    # Kill Zone Status
    active_zones = calculate_kill_zone_times()
    zone_names = {
        'asian': 'الجلسة الآسيوية',
        'london': '🔥 London Kill Zone',
        'ny': '🔥 New York Kill Zone',
        'london_close': 'London Close'
    }

    if active_zones:
        st.markdown("""
        <div style="background: rgba(234,179,8,0.15); border: 1px solid rgba(234,179,8,0.4); 
                    border-radius: 12px; padding: 12px; margin-bottom: 12px;">
            <p style="color: #fbbf24; font-weight: 700; margin: 0; font-size: 0.9rem;">⏰ Kill Zones نشطة</p>
        </div>
        """, unsafe_allow_html=True)
        for z in active_zones:
            if z in zone_names:
                st.markdown(f"<span style='color: #fbbf24; font-size: 0.8rem;'>• {zone_names[z]}</span>", unsafe_allow_html=True)

    # Market Status
    st.markdown("""
    <div class="status-live" style="margin-top: 12px;">
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

    # Top Stats Row
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

    # Stock & Timeframe Selection
    col_stock, col_tf, col_period = st.columns([3, 1, 1])

    with col_stock:
        all_stocks = get_all_stocks_flat()
        stock_options = [f"{s['ticker']} - {s['name']} ({s['category'].split(' ')[0]})" for s in all_stocks]
        selected = st.selectbox("🔍 اختر السهم للتحليل ICT", stock_options, index=0)
        selected_ticker = selected.split(' - ')[0]
        selected_stock = next(s for s in all_stocks if s['ticker'] == selected_ticker)

    with col_tf:
        tf_display = list(TIMEFRAMES.keys())
        selected_tf = st.selectbox("الفريم", tf_display, index=9)  # Default D1
        st.session_state['selected_timeframe'] = selected_tf

    with col_period:
        period = st.selectbox("الفترة", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)

    # Load Data
    with st.spinner("🔬 جاري تحليل البيانات بمنهجية ICT..."):
        hist, info = get_stock_data(selected_ticker, period, TIMEFRAMES[selected_tf])

    if hist is not None and not hist.empty:
        hist = calculate_technical_indicators(hist)

        # ============ ICT DETECTION ============
        structure_events = detect_market_structure(hist)
        fvgs = detect_fvg(hist)
        obs = detect_order_blocks(hist)
        liquidity = detect_liquidity_levels(hist)
        unicorns = detect_unicorn_model(obs, fvgs)

        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price else 0

        is_saudi = selected_ticker.endswith('.SR')
        currency = "ر.س" if is_saudi else "$"

        # ============ PRICE HEADER ============
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
            st.metric("P/E", f"{pe:.2f}" if pe else "—")

        # ============ ICT TABS ============
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 الشارت + ICT Zones",
            "🎯 Fair Value Gaps",
            "🏛️ Order Blocks",
            "💧 Liquidity",
            "⭐ التقييم والأهداف"
        ])

        # ============ TAB 1: CHART + ICT ZONES ============
        with tab1:
            col_chart, col_zones = st.columns([3, 1])

            with col_chart:
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                   vertical_spacing=0.08, row_heights=[0.7, 0.3])

                # Candlestick
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

                # SMAs
                fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_20'], name='SMA 20', 
                                        line=dict(color='#60a5fa', width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_50'], name='SMA 50', 
                                        line=dict(color='#f472b6', width=1.5)), row=1, col=1)

                # FVG Zones on chart
                for fvg in fvgs[-5:]:  # Show last 5 FVGs
                    if fvg['status'] != 'MITIGATED':
                        color = 'rgba(34,197,94,0.2)' if fvg['type'] == 'BULLISH' else 'rgba(239,68,68,0.2)'
                        fig.add_hrect(y0=fvg['bottom'], y1=fvg['top'], 
                                     fillcolor=color, line_width=0, opacity=0.5, row=1, col=1)
                        # CE line
                        fig.add_hline(y=fvg['ce'], line_dash="dot", 
                                     line_color='#a78bfa', line_width=1, opacity=0.7, row=1, col=1)

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
                    font=dict(family="Tajawal, sans-serif"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig, use_container_width=True)

                # Structure Events
                if structure_events:
                    render_section_header("أحداث بنية السوق (Market Structure)", "🏛️")
                    for event in structure_events[-3:]:
                        event_type = "BOS" if "BOS" in event['type'] else "CHoCH"
                        direction = "bullish" if "BULLISH" in event['type'] else "bearish"
                        render_ict_zone(event_type, event, status='confirmed')

            with col_zones:
                st.markdown("### 🎯 مناطق ICT النشطة")

                # Unicorn Models
                if unicorns:
                    st.markdown("#### 🦄 Unicorn Models (أعلى احتمالية)")
                    for u in unicorns[-3:]:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, rgba(168,85,247,0.2), rgba(236,72,153,0.1));
                                    border: 2px solid rgba(168,85,247,0.5); border-radius: 12px; padding: 12px; margin-bottom: 8px;">
                            <div style="color: #c084fc; font-weight: 700; font-size: 0.9rem;">🦄 Unicorn Model</div>
                            <div style="color: #e9d5ff; font-size: 0.8rem; margin-top: 4px;">
                                النطاق: {currency}{u['overlap_bottom']:.2f} - {currency}{u['overlap_top']:.2f}
                            </div>
                            <div style="color: #f0abfc; font-size: 0.75rem; margin-top: 2px;">
                                CE: {currency}{u['ce']:.2f}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # Fresh FVGs
                fresh_fvgs = [f for f in fvgs if f['status'] == 'FRESH']
                if fresh_fvgs:
                    st.markdown("#### ⚡ FVGs جديدة")
                    for f in fresh_fvgs[-3:]:
                        direction = "bullish" if f['type'] == 'BULLISH' else "bearish"
                        render_ict_zone(f"FVG {f['type']}", f, status='FRESH')

                # Active OBs
                active_obs = [o for o in obs if o['status'] == 'ACTIVE']
                if active_obs:
                    st.markdown("#### 🏛️ Order Blocks نشطة")
                    for o in active_obs[-3:]:
                        direction = "bullish" if o['type'] == 'BULLISH' else "bearish"
                        render_ict_zone(f"OB {o['type']}", o, status='ACTIVE')

        # ============ TAB 2: FVG DETAILS ============
        with tab2:
            render_section_header("Fair Value Gaps - التحليل التفصيلي", "🎯")

            col_fvg_stats, col_fvg_list = st.columns([1, 2])

            with col_fvg_stats:
                total_fvgs = len(fvgs)
                fresh_count = len([f for f in fvgs if f['status'] == 'FRESH'])
                partial_count = len([f for f in fvgs if f['status'] == 'PARTIAL'])
                mitigated_count = len([f for f in fvgs if f['status'] == 'MITIGATED'])

                render_metric_card("إجمالي FVGs", str(total_fvgs), icon="🎯")
                render_metric_card("جديدة", str(fresh_count), icon="⚡")
                render_metric_card("جزئية", str(partial_count), icon="🟡")
                render_metric_card("مغلقة", str(mitigated_count), icon="✅")

            with col_fvg_list:
                if fvgs:
                    for fvg in reversed(fvgs[-10:]):
                        status_color = {
                            'FRESH': '#22c55e',
                            'PARTIAL': '#eab308',
                            'MITIGATED': '#64748b'
                        }.get(fvg['status'], '#94a3b8')

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
                                النطاق: {currency}{fvg['bottom']:.2f} - {currency}{fvg['top']:.2f} | 
                                CE: {currency}{fvg['ce']:.2f}
                            </div>
                            <div style="color: #64748b; font-size: 0.75rem; margin-top: 2px;">
                                {fvg['description']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("لا توجد FVGs في الفترة المحددة")

        # ============ TAB 3: ORDER BLOCKS ============
        with tab3:
            render_section_header("Order Blocks & Breaker Blocks", "🏛️")

            col_ob_stats, col_ob_list = st.columns([1, 2])

            with col_ob_stats:
                total_obs = len(obs)
                active_count = len([o for o in obs if o['status'] == 'ACTIVE'])
                broken_count = len([o for o in obs if o['status'] == 'BROKEN'])

                render_metric_card("إجمالي OBs", str(total_obs), icon="🏛️")
                render_metric_card("نشطة", str(active_count), icon="🟢")
                render_metric_card("Breaker", str(broken_count), icon="🔨")

            with col_ob_list:
                if obs:
                    for ob in reversed(obs[-10:]):
                        status_color = '#22c55e' if ob['status'] == 'ACTIVE' else '#f472b6'
                        status_icon = '🟢' if ob['status'] == 'ACTIVE' else '🔨'

                        st.markdown(f"""
                        <div style="background: rgba(30,41,59,0.8); border: 1px solid {status_color}40; 
                                    border-radius: 12px; padding: 12px; margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: {status_color}; font-weight: 700;">
                                    {status_icon} {ob['type']} OB
                                </span>
                                <span style="color: #64748b; font-size: 0.8rem;">{ob['status']}</span>
                            </div>
                            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                                النطاق: {currency}{ob['bottom']:.2f} - {currency}{ob['top']:.2f}
                            </div>
                            <div style="color: #64748b; font-size: 0.75rem; margin-top: 2px;">
                                {ob['description']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("لا توجد Order Blocks في الفترة المحددة")

        # ============ TAB 4: LIQUIDITY ============
        with tab4:
            render_section_header("Liquidity Analysis - تحليل السيولة", "💧")

            if liquidity:
                col_liq_bsl, col_liq_ssl = st.columns(2)

                bsl = [l for l in liquidity if l['type'] == 'BSL']
                ssl = [l for l in liquidity if l['type'] == 'SSL']

                with col_liq_bsl:
                    st.markdown("### 🟢 Buy-Side Liquidity (Equal Highs)")
                    st.markdown("<p style='color: #64748b; font-size: 0.85rem;'>السيولة الشرائية - أهداف البيع</p>", unsafe_allow_html=True)
                    for l in bsl[-5:]:
                        st.markdown(f"""
                        <div style="background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); 
                                    border-radius: 8px; padding: 8px; margin-bottom: 6px;">
                            <span style="color: #4ade80; font-weight: 700;">{currency}{l['price']:.2f}</span>
                            <span style="color: #64748b; font-size: 0.75rem;"> - {l['description']}</span>
                        </div>
                        """, unsafe_allow_html=True)

                with col_liq_ssl:
                    st.markdown("### 🔴 Sell-Side Liquidity (Equal Lows)")
                    st.markdown("<p style='color: #64748b; font-size: 0.85rem;'>السيولة البيعية - أهداف الشراء</p>", unsafe_allow_html=True)
                    for l in ssl[-5:]:
                        st.markdown(f"""
                        <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); 
                                    border-radius: 8px; padding: 8px; margin-bottom: 6px;">
                            <span style="color: #f87171; font-weight: 700;">{currency}{l['price']:.2f}</span>
                            <span style="color: #64748b; font-size: 0.75rem;"> - {l['description']}</span>
                        </div>
                        """, unsafe_allow_html=True)

                # Liquidity sweep analysis
                if len(hist) > 20:
                    recent_high = hist['High'].iloc[-20:].max()
                    recent_low = hist['Low'].iloc[-20:].min()
                    current = hist['Close'].iloc[-1]

                    st.markdown("---")
                    st.markdown("### 📊 تحليل السحب (Liquidity Sweep Analysis)")

                    if current > recent_high * 0.99:
                        st.markdown("""
                        <div style="background: rgba(234,179,8,0.15); border: 1px solid rgba(234,179,8,0.4); 
                                    border-radius: 12px; padding: 16px;">
                            <p style="color: #fbbf24; font-weight: 700;">⚠️ محتمل: Buy-Side Liquidity Sweep</p>
                            <p style="color: #94a3b8; font-size: 0.85rem;">السعر قريب من أعلى مستويات السيولة. احتمالية انعكاس هبوطي.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif current < recent_low * 1.01:
                        st.markdown("""
                        <div style="background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.4); 
                                    border-radius: 12px; padding: 16px;">
                            <p style="color: #4ade80; font-weight: 700;">✅ محتمل: Sell-Side Liquidity Sweep</p>
                            <p style="color: #94a3b8; font-size: 0.85rem;">السعر قريب من أدنى مستويات السيولة. احتمالية انعكاس صعودي.</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("لم يتم العثور على مستويات سيولة واضحة في الفترة المحددة")

        # ============ TAB 5: RATING & TARGETS ============
        with tab5:
            render_section_header("التقييم والأهداف", "⭐")

            col_rating, col_target = st.columns(2)

            with col_rating:
                st.markdown("### ⭐ تقييمك للسهم")
                current_rating = get_rating_from_storage(selected_ticker)

                rating_cols = st.columns(5)
                for i, col in enumerate(rating_cols, 1):
                    with col:
                        is_active = current_rating >= i
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
                                              min_value=0.01, step=0.01, format="%.2f")
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

            # OTE Zone calculation
            if len(hist) > 50:
                swing_high = hist['High'].iloc[-50:].max()
                swing_low = hist['Low'].iloc[-50:].min()

                # Determine trend
                trend = 'bullish' if hist['Close'].iloc[-1] > hist['SMA_50'].iloc[-1] else 'bearish'
                ote = calculate_ote_zone(swing_high, swing_low, trend)

                st.markdown("---")
                st.markdown("### 🎯 Optimal Trade Entry (OTE) Zone")
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(147,51,234,0.1));
                            border: 1px solid rgba(59,130,246,0.3); border-radius: 16px; padding: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span style="color: #94a3b8;">الاتجاه المحدد:</span>
                        <span style="color: {'#22c55e' if trend == 'bullish' else '#ef4444'}; font-weight: 700;">
                            {'📈 صعودي' if trend == 'bullish' else '📉 هبوطي'}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #94a3b8;">أعلى swing:</span>
                        <span style="color: #f8fafc; font-weight: 700;">{currency}{swing_high:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span style="color: #94a3b8;">أدنى swing:</span>
                        <span style="color: #f8fafc; font-weight: 700;">{currency}{swing_low:.2f}</span>
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
        st.info("لم تقم بتقييم أي سهم بعد. اذهب إلى صفحة السوق وقيّم الأسهم التي تهمك!")

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
        st.markdown("### 📊 إحصائيات ICT")
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
                <span style="color: #22c55e; font-weight: 700; float: left;">{len(rated_stocks)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #64748b;">
        <p>📈 Al7ebi Pro ICT — محلل الأسهم الاحترافي</p>
        <p style="font-size: 0.8rem;">v3.0 ICT | Inner Circle Trader Methodology | Michael Huddleston Concepts</p>
    </div>
    """, unsafe_allow_html=True)
