# app.py
import streamlit as st
import pandas as pd
from src.logic import calculate_life_plan, calculate_required_savings, get_side_hustle_suggestion

# --- 1. ページ設定 (OGP/Favicon) ---
st.set_page_config(
    page_title="Future Design | 資産運用シミュレーター",
    page_icon="💎",
    layout="wide"
)

# --- 2. 高度なデザインカスタマイズ (CSS) ---
st.markdown("""
    <style>
    /* Google Fonts 導入 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto+Sans+JP', sans-serif;
    }
    
    /* カードデザインの強化 */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }

    /* フッターのデザイン */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f8f9fa;
        color: #6c757d;
        text-align: center;
        padding: 10px;
        font-size: 12px;
        border-top: 1px solid #dee2e6;
    }
    
    /* タブのスタイル調整 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        gap: 1px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00cc96 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# セッションステート初期化
if "current_savings" not in st.session_state:
    st.session_state["current_savings"] = 0.0

# --- メインコンテンツ ---
st.title("💎 Future Design")
st.markdown("##### 投資とキャリアの力で、理想の未来を。")

tab1, tab2, tab3 = st.tabs(["📊 家計診断", "📈 老後シミュレーション", "🎯 キャリア逆算"])

# --- Tab 1: 家計診断 ---
with tab1:
    st.header("家賃や生活費から「投資余力」を出す")
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        income = st.number_input("手取り月収 (万円)", value=25.0, step=1.0, help="給与明細の「振込額」を入力してください")
        fixed_cost = st.number_input("固定費合計 (万円)", value=12.0, step=1.0, help="家賃、光熱費、通信費などの合計です")
    with col2:
        remainder = income - fixed_cost
        st.write("##### 資産形成への配分")
        ratio = st.slider("投資に回す割合 (%)", 0, 100, 20, help="自由に使えるお金のうち、将来のために貯める割合です")
        saving_amount = remainder * (ratio / 100)
        st.session_state["current_savings"] = saving_amount
        st.metric("毎月の投資可能額", f"{saving_amount:.1f}万円", delta="Next Stepへ")

# --- Tab 2: 老後シミュレーション ---
with tab2:
    st.header("人生100年時代の資産推移")
    c_in, c_graph = st.columns([1, 2], gap="large")
    
    with c_in:
        st.write("##### シミュレーション条件")
        c_age = st.number_input("現在年齢", 18, 80, 30)
        r_age = st.number_input("引退年齢", 40, 80, 65, help="仕事を辞めて取り崩しを始める年齢です")
        initial_asset = st.number_input("現在の貯蓄 (万円)", 0, 5000, 100)
        m_save = st.session_state["current_savings"]
        m_withdraw = st.number_input("引退後の月間生活費 (万円)", 5, 100, 20, help="老後に「貯蓄から」いくら使うか。年金とは別です。")
        rate = st.slider("想定利回り (%)", 0.0, 10.0, 5.0, help="S&P500の過去平均は約7%と言われています")
        inflation = st.slider("インフレ率 (%)", 0.0, 5.0, 0.0, help="物価が上がると実質的な価値が下がります")
        is_nisa = st.toggle("NISAを使用 (非課税)", value=True)

    df_std = calculate_life_plan(c_age, r_age, 95, initial_asset, m_save, m_withdraw, rate, inflation, is_nisa)
    df_cash = calculate_life_plan(c_age, r_age, 95, initial_asset, m_save, m_withdraw, 0.01, inflation, False)

    with c_graph:
        final_amt = df_std.iloc[-1]["資産額"]
        if final_amt > 0:
            st.success("🎉 資産寿命は95歳まで持続する見込みです！")
        else:
            st.error("⚠️ 老後資金が不足する可能性があります。設定を見直しましょう。")

        m1, m2 = st.columns(2)
        m1.metric("95歳時点の資産額", f"¥{final_amt:,.0f}")
        m2.metric("投資による増益額", f"+¥{final_amt - df_cash.iloc[-1]['資産額']:,.0f}", delta="運用効果")

        st.area_chart(df_std.set_index("年齢")["資産額"], color="#00cc96")

# --- Tab 3: キャリア逆算 ---
with tab3:
    st.header("目標達成に向けた「稼ぎ方」の提案")
    col_t, col_r = st.columns([1, 1], gap="large")
    
    with col_t:
        st.write("##### 理想のゴール設定")
        target_asset = st.number_input("目標資産額 (万円)", value=3000, step=100)
        target_years = st.number_input("達成までの期間 (年)", value=20, step=1)
        current_assets = st.number_input("現在の資産額 (万円)", value=100)
        
    req_monthly = calculate_required_savings(target_asset, target_years, 5.0, current_assets)
    gap = req_monthly - st.session_state["current_savings"]

    with col_r:
        st.write("##### 達成率とアクション")
        # 達成率の計算とプログレスバー
        achievement = min(100, int((st.session_state["current_savings"] / req_monthly) * 100)) if req_monthly > 0 else 100
        st.write(f"現状の積立達成率: **{achievement}%**")
        st.progress(achievement / 100)
        
        st.metric("目標に必要な毎月の積立額", f"{req_monthly:.1f}万円/月")
        
        title, msg, type_ = get_side_hustle_suggestion(gap)
        if type_ == "success": st.success(f"### {title}\n{msg}")
        elif type_ == "info": st.info(f"### {title}\n{msg}")
        elif type_ == "warning": st.warning(f"### {title}\n{msg}")
        else: st.error(f"### {title}\n{msg}")

# --- フッター ---
st.markdown("""
    <div class="footer">
        © 2026 Future Design Simulator | Developed with Streamlit
    </div>
""", unsafe_allow_html=True)