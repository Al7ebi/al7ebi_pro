import streamlit as st
from utils import get_stock_data

st.set_page_config(page_title="Al7ebi Pro", layout="wide")
st.title("📊 منصة الحبي للتحليل المالي")

symbol = st.sidebar.text_input("أدخل رمز السهم (مثلاً: 2222.SR أو AAPL)", "2222.SR")

if st.button("تحليل السهم"):
    data = get_stock_data(symbol)
    st.write(f"السعر الحالي لـ {symbol}:")
    st.line_chart(data['Close'])
    st.write("مؤشر القوة النسبية (RSI):")
    st.line_chart(data['RSI'])
