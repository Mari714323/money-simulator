# app.py
import streamlit as st
import pandas as pd
from src.logic import calculate_life_plan, calculate_required_savings, get_side_hustle_suggestion

# --- ページ設定 ---
st.set_page_config(page_title="Future Design", page_icon="💎", layout="wide")

# CSS設定 (カード風デザイン)
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# セッションステート初期化
if "current_savings" not in st.session_state:
    st.session_state["current_savings"] = 0.0

st.title("💎 Future Design: 人生設計シミュレーター")

tab1, tab2, tab3 = st.tabs(["📝 家計診断", "👴 老後シミュレーション", "🎯 キャリア逆算"])

# --- Tab 1: 家計診断 ---
with tab1:
    st.header("1. 家計診断")
    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input("手取り月収 (万円)", value=25.0, step=1.0)
        fixed_cost = st.number_input("固定費合計 (万円)", value=12.0, step=1.0)
    with col2:
        remainder = income - fixed_cost
        ratio = st.slider("投資に回す割合 (%)", 0, 100, 20)
        saving_amount = remainder * (ratio / 100)
        st.session_state["current_savings"] = saving_amount
        st.metric("毎月の投資可能額", f"{saving_amount:.1f}万円")

# --- Tab 2: 老後シミュレーション ---
with tab2:
    st.header("2. 老後シミュレーション")
    c_in, c_graph = st.columns([1, 2])
    
    with c_in:
        c_age = st.number_input("現在年齢", 18, 80, 30)
        r_age = st.number_input("引退年齢", 40, 80, 65)
        d_age = st.number_input("想定寿命", 70, 120, 95)
        initial_asset = st.number_input("現在の貯蓄 (万円)", 0, 5000, 100)
        m_save = st.session_state["current_savings"]
        m_withdraw = st.number_input("老後の月額生活費 (万円)", 5, 100, 20)
        rate = st.slider("想定利回り (%)", 0.0, 10.0, 5.0)
        inflation = st.slider("インフレ率 (%)", 0.0, 5.0, 0.0)
        is_nisa = st.toggle("NISAを使用 (非課税)", value=True)

    # 計算（標準と貯金のみの比較）
    df_std = calculate_life_plan(c_age, r_age, d_age, initial_asset, m_save, m_withdraw, rate, inflation, is_nisa)
    df_cash = calculate_life_plan(c_age, r_age, d_age, initial_asset, m_save, m_withdraw, 0.01, inflation, False)

    with c_graph:
        final_amt = df_std.iloc[-1]["資産額"]
        # 目標達成判定
        if final_amt > 0:
            st.success(f"資産寿命は {d_age} 歳以上持続します！")
        else:
            ruin_age = df_std[df_std["資産額"] == 0].iloc[0]["年齢"]
            st.warning(f"資産は {ruin_age} 歳で底をつく可能性があります。")

        m1, m2 = st.columns(2)
        m1.metric("将来の資産総額", f"¥{final_amt:,.0f}")
        m2.metric("貯金のみとの差", f"+¥{final_amt - df_cash.iloc[-1]['資産額']:,.0f}")

        chart_data = pd.DataFrame({
            "運用あり": df_std.set_index("年齢")["資産額"],
            "貯金のみ": df_cash.set_index("年齢")["資産額"]
        })
        st.area_chart(chart_data, color=["#00CC96", "#FF4B4B"])

# --- Tab 3: キャリア逆算 ---
with tab3:
    st.header("3. キャリア逆算")
    col_t, col_r = st.columns(2)
    with col_t:
        target_asset = st.number_input("目標資産 (万円)", value=3000, step=100)
        target_years = st.number_input("達成期間 (年)", value=20, step=1)
        current_assets = st.number_input("現在の資産 (万円)", value=100, step=10)
        
    req_monthly = calculate_required_savings(target_asset, target_years, 5.0, current_assets)
    gap = req_monthly - st.session_state["current_savings"]

    with col_r:
        st.metric("目標に必要な積立額", f"{req_monthly:.1f}万円/月")
        title, msg, type_ = get_side_hustle_suggestion(gap)
        
        if type_ == "success": st.success(f"### {title}\n{msg}")
        elif type_ == "info": st.info(f"### {title}\n{msg}")
        elif type_ == "warning": st.warning(f"### {title}\n{msg}")
        else: st.error(f"### {title}\n{msg}")