import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from utils import (
    apply_custom_css, render_header, render_section_header,
    get_stock_data, get_all_stocks_flat
)

st.set_page_config(page_title="مقارنة الأسهم | Al7ebi Pro", page_icon="📊", layout="wide")
apply_custom_css()

render_header("مقارنة الأسهم", "قارن بين أسهم متعددة في شارت واحد")

all_stocks = get_all_stocks_flat()
stock_options = [f"{s['ticker']} - {s['name']}" for s in all_stocks]

selected = st.multiselect(
    "🔍 اختر الأسهم للمقارنة (2-4 أسهم)",
    stock_options,
    default=stock_options[:2] if len(stock_options) >= 2 else stock_options[:1],
    max_selections=4
)

period = st.select_slider("الفترة", options=["1mo", "3mo", "6mo", "1y", "2y"], value="1y")

if len(selected) >= 2:
    tickers = [s.split(' - ')[0] for s in selected]
    names = [s.split(' - ')[1] for s in selected]

    with st.spinner("جاري تحميل البيانات..."):
        fig = go.Figure()
        colors = ['#60a5fa', '#f472b6', '#34d399', '#fbbf24']

        for i, (ticker, name) in enumerate(zip(tickers, names)):
            hist, _ = get_stock_data(ticker, period)
            if hist is not None and not hist.empty:
                normalized = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
                fig.add_trace(go.Scatter(
                    x=hist.index, y=normalized,
                    name=f"{name} ({ticker})",
                    line=dict(color=colors[i % len(colors)], width=2.5)
                ))

        fig.update_layout(
            title="مقارنة الأداء النسبي (% التغيير)",
            xaxis_title="التاريخ",
            yaxis_title="% التغيير",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500,
            font=dict(family="Tajawal"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            hovermode="x unified"
        )
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")

        st.plotly_chart(fig, use_container_width=True)

        render_section_header("جدول المقارنة", "📋")

        comparison_data = []
        for ticker, name in zip(tickers, names):
            hist, info = get_stock_data(ticker, "1y")
            if hist is not None and not hist.empty:
                current = hist['Close'].iloc[-1]
                ytd = ((current - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100) if len(hist) > 1 else 0
                volatility = hist['Close'].pct_change().std() * np.sqrt(252) * 100

                comparison_data.append({
                    'السهم': name,
                    'الرمز': ticker,
                    'السعر الحالي': f"{'ر.س' if ticker.endswith('.SR') else '$'}{current:.2f}",
                    'التغيير السنوي': f"{ytd:.2f}%",
                    'التقلب': f"{volatility:.2f}%",
                    'أعلى سعر': f"{hist['High'].max():.2f}",
                    'أدنى سعر': f"{hist['Low'].min():.2f}",
                })

        if comparison_data:
            df_comp = pd.DataFrame(comparison_data)
            st.dataframe(df_comp, use_container_width=True, hide_index=True)
else:
    st.info("👆 اختر سهمين على الأقل للمقارنة بينهم")
