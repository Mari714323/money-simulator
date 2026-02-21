# app.py
import streamlit as st
import pandas as pd
# 自作ロジックのインポート
from src.logic import calculate_life_plan, calculate_required_savings, get_side_hustle_suggestion

# --- ページ設定 ---
st.set_page_config(page_title="Future Design", page_icon="💎", layout="wide")

# CSS設定 (省略して記載していますが、前回のものをそのまま使えます)
st.markdown("""<style>div[data-testid="stMetric"] {background-color: #ffffff; border: 1px solid #e6e6e6; padding: 15px; border-radius: 10px;}</style>""", unsafe_allow_html=True)

# セッションステート初期化
if "current_savings" not in st.session_state: st.session_state["current_savings"] = 0.0

st.title("💎 Future Design: 人生設計シミュレーター")

tab1, tab2, tab3 = st.tabs(["📝 家計診断", "👴 老後シミュレーション", "🎯 キャリア逆算"])

# --- Tab 1: 家計診断 ---
with tab1:
    st.header("1. 家計診断")
    c1, c2 = st.columns(2)
    with c1:
        income = st.number_input("手取り月収 (万円)", value=25.0)
        fixed_cost = st.number_input("固定費合計 (万円)", value=12.0)
    with c2:
        remainder = income - fixed_cost
        ratio = st.slider("投資に回す割合 (%)", 0, 100, 20)
        saving_amount = remainder * (ratio / 100)
        st.session_state["current_savings"] = saving_amount
        st.metric("毎月の投資可能額", f"{saving_amount:.1f}万円")

# --- Tab 2: 老後シミュレーション ---
with tab2:
    st.header("2. 老後シミュレーション")
    col_in, col_out = st.columns([1, 2])
    with col_in:
        years = st.slider("運用期間 (年)", 10, 50, 30)
        rate = st.slider("想定利回り (%)", 1.0, 10.0, 5.0)
        # Tab1の結果を使用
        m_save = st.session_state["current_savings"]
        
    df = calculate_life_plan(30, 65, 95, 100, m_save, 20, rate, 0, True)
    with col_out:
        st.metric("将来の資産額", f"¥{df.iloc[-1]['資産額']:,.0f}")
        st.area_chart(df.set_index("年齢")["資産額"])

# --- Tab 3: キャリア逆算 ---
with tab3:
    st.header("3. キャリア逆算")
    target_asset = st.number_input("目標資産 (万円)", value=3000)
    req_monthly = calculate_required_savings(target_asset, 20, 5.0, 100)
    gap = req_monthly - st.session_state["current_savings"]
    
    st.metric("必要な積立額", f"{req_monthly:.1f}万円/月")
    title, msg, type_ = get_side_hustle_suggestion(gap)
    if type_ == "success": st.success(f"{title}\n{msg}")
    elif type_ == "info": st.info(f"{title}\n{msg}")
    elif type_ == "warning": st.warning(f"{title}\n{msg}")
    else: st.error(f"{title}\n{msg}")