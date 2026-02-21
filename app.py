import streamlit as st
import pandas as pd
import numpy as np

# --- 1. ページ設定 & デザインカスタマイズ ---
st.set_page_config(
    page_title="Future Design | 人生設計シミュレーター",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（見た目を整える魔法の呪文）
st.markdown("""
    <style>
    /* メインの背景色を少し調整 */
    .stApp {
        background-color: #f8f9fa;
    }
    /* 指標（Metric）のカードデザイン化 */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    /* 重要数字を大きく、色をつける */
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
        color: #00cc96;
    }
    /* タブのフォントを太く */
    button[data-baseweb="tab"] {
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- セッションステート初期化 ---
if "suggested_savings" not in st.session_state:
    st.session_state["suggested_savings"] = 0.0
if "current_savings" not in st.session_state:
    st.session_state["current_savings"] = 0.0

# --- 関数定義 (ロジックは前回と同じ) ---
def calculate_required_savings(target_amount, years, rate, current_assets):
    target = target_amount * 10000
    principal = current_assets * 10000
    r_monthly = (rate / 100) / 12
    n_months = years * 12

    if rate == 0:
        required = (target - principal) / n_months
    else:
        future_principal = principal * ((1 + r_monthly) ** n_months)
        numerator = (target - future_principal) * r_monthly
        denominator = ((1 + r_monthly) ** n_months) - 1
        required = numerator / denominator
    return required / 10000

def get_side_hustle_suggestion(gap_amount):
    if gap_amount <= 0:
        return "🎉 目標達成済み", "今のペースで完璧です！素晴らしい！", "success"
    elif gap_amount <= 1.0:
        return "🌱 Level 1: ポイ活・不用品販売", "スマホ一つで隙間時間にできることから始めましょう。", "info"
    elif gap_amount <= 3.0:
        return "✏️ Level 2: Webライター・軽作業", "クラウドソーシングで「書く」「入力する」仕事を獲得しましょう。", "warning"
    elif gap_amount <= 5.0:
        return "💻 Level 3: 動画編集・スキル販売", "単価の高いクリエイティブなスキルを身につけるチャンスです。", "warning"
    else:
        return "🚀 Level 4: 転職・事業・投資強化", "副業の域を超えています。本業の年収アップや資産運用の見直しが必要です。", "error"

# --- サイドバー：共通設定 ---
with st.sidebar:
    st.title("💎 Future Design")
    st.caption("Produced by AI Engineer")
    st.markdown("---")
    st.write("設定メニュー")
    # テーマカラー変更機能（おまけ）
    theme_color = st.color_picker("テーマカラー", "#00CC96")
    st.info("👆 シミュレーションのグラフ色などに反映されます")

# --- メイン画面 ---
st.title("人生設計 & キャリア戦略")
st.markdown("##### 💰 お金を知り、未来を描き、今やるべきことを見つける。")

# タブ作成（アイコン追加で見やすく）
tab1, tab2, tab3 = st.tabs(["📝 家計診断", "👴 老後シミュレーション", "🎯 キャリア逆算"])

# ==========================================
# Tab 1: 家計診断
# ==========================================
with tab1:
    st.header("1. 家計診断")
    st.markdown("今の収入と支出から、**「投資に回せる余力」** を診断します。")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("収入と固定費")
        income = st.number_input("手取り月収 (万円)", 15.0, 200.0, 25.0, 1.0, key="inc")
        fixed_cost = st.number_input("固定費合計 (家賃など) (万円)", 0.0, 150.0, 12.0, 1.0, key="fix")
        
        remainder = income - fixed_cost
        
    with col2:
        st.subheader("診断結果")
        if remainder <= 0:
            st.error(f"⚠️ 赤字です (▲{abs(remainder):.1f}万円)。固定費を見直しましょう。")
            st.session_state["current_savings"] = 0.0
        else:
            st.markdown(f"自由に使えるお金: <span class='big-font'>{remainder:.1f}万円</span>", unsafe_allow_html=True)
            
            # スライダーを見やすく
            ratio = st.slider("投資に回す割合 (%)", 0, 100, 20, 5)
            saving_amount = remainder * (ratio / 100)
            st.session_state["current_savings"] = saving_amount
            
            # カード表示
            st.metric(label="毎月の投資可能額", value=f"{saving_amount:.1f}万円", delta="この金額を次のタブで使います")

    # グラフ

    st.markdown("---")
    chart_df = pd.DataFrame({
        "固定費": [fixed_cost],
        "自由費": [remainder - saving_amount],
        "投資": [saving_amount]
    })
    # .T を消して、データフレームをそのまま渡します
    st.bar_chart(chart_df, color=[theme_color, "#FF9F36", "#FF4B4B"])
# ==========================================
# Tab 2: 老後シミュレーション
# ==========================================
with tab2:
    st.header("2. 老後シミュレーション")
    
    col_input, col_graph = st.columns([1, 2], gap="large")
    
    with col_input:
        st.info("家計診断の結果が自動入力されています👇")
        years = st.slider("運用期間 (年)", 10, 50, 30)
        rate = st.slider("想定利回り (%)", 1.0, 10.0, 5.0, 0.1)
        monthly_save = st.number_input("毎月の積立額", value=st.session_state["current_savings"])

    # 計算
    fv = (monthly_save * 10000 * (((1 + rate/100/12)**(years*12) - 1) / (rate/100/12)))
    principal = monthly_save * 10000 * 12 * years
    profit = fv - principal

    with col_graph:
        # 結果を3つのカードで並べる
        m1, m2, m3 = st.columns(3)
        m1.metric(f"{years}年後の資産総額", f"¥{int(fv/10000):,}万円")
        m2.metric("運用益 (不労所得)", f"+¥{int(profit/10000):,}万円", delta="利回りの力")
        m3.metric("積立元本", f"¥{int(principal/10000):,}万円")

        # エリアチャート
        chart_data = pd.DataFrame({
            "資産推移": [monthly_save * 10000 * (((1 + rate/100/12)**(i*12) - 1) / (rate/100/12)) for i in range(years)]
        })
        st.area_chart(chart_data, color=theme_color)

# ==========================================
# Tab 3: キャリア目標 (逆算)
# ==========================================
with tab3:
    st.header("3. キャリア目標 (逆算)")
    st.markdown("目標から逆算して、**「今やるべき副業」** をAIが提案します。")

    col_target, col_gap = st.columns([1, 1], gap="large")

    with col_target:
        st.subheader("🎯 ゴール設定")
        target_asset = st.number_input("目標資産 (万円)", 1000, 10000, 3000, 100)
        target_years = st.number_input("達成期間 (年)", 5, 40, 20)
        current_asset = st.number_input("現在の貯蓄 (万円)", 0, 5000, 100, 10)
        
        # 計算
        required_monthly = calculate_required_savings(target_asset, target_years, 5.0, current_asset)
        current_can_save = st.session_state["current_savings"]
        gap = required_monthly - current_can_save

    with col_gap:
        st.subheader("📊 ギャップ分析")
        
        c1, c2 = st.columns(2)
        c1.metric("必要な積立額", f"{required_monthly:.1f}万円/月")
        c2.metric("不足額 (Gap)", f"{gap:.1f}万円/月", delta_color="inverse")
        
        st.divider()

        # 副業提案の表示デザイン
        title, msg, type_ = get_side_hustle_suggestion(gap)
        
        if type_ == "success":
            st.balloons()
            st.success(f"### {title}\n{msg}")
        elif type_ == "info":
            st.info(f"### {title}\n{msg}")
            st.warning(f"### {title}\n{msg}")
        else:
            st.error(f"### {title}\n{msg}")
            
        if gap > 0:
            st.caption(f"💡 月{gap:.1f}万円稼げば、{target_years}年後に{target_asset:,}万円達成できます！")