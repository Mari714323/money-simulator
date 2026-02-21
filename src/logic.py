def calculate_life_plan(current_age, retire_age, death_age, 
                       initial_assets, monthly_save, monthly_withdraw, 
                       rate_return, rate_inflation, is_nisa):
    """
    人生100年時代の資産推移を計算する
    """
    effective_rate = rate_return * 0.8 if not is_nisa and rate_return > 0 else rate_return
    data = []
    current_asset = initial_assets * 10000
    total_principal = initial_assets * 10000
    
    data.append({"年齢": current_age, "資産額": int(current_asset), "実質価値": int(current_asset), "元本": int(total_principal), "フェーズ": "現在"})

    for age in range(current_age + 1, death_age + 1):
        if age <= retire_age:
            gain = current_asset * (effective_rate / 100)
            current_asset += gain + (monthly_save * 10000 * 12)
            total_principal += (monthly_save * 10000 * 12)
            phase = "積立期"
        else:
            years_since_retire = age - retire_age
            inflated_withdraw = (monthly_withdraw * 10000) * ((1 + rate_inflation/100) ** years_since_retire)
            gain = current_asset * (effective_rate / 100)
            current_asset = max(0, current_asset + gain - (inflated_withdraw * 12))
            phase = "取崩し期"

        present_value = current_asset / ((1 + rate_inflation/100) ** (age - current_age))
        data.append({"年齢": age, "資産額": int(current_asset), "実質価値": int(present_value), "元本": int(total_principal), "フェーズ": phase})
    import pandas as pd
    return pd.DataFrame(data)

def calculate_required_savings(target_amount, years, rate, current_assets):
    """目標額を達成するために必要な毎月の積立額を逆算する"""
    target = target_amount * 10000
    principal = current_assets * 10000
    r_monthly = (rate / 100) / 12
    n_months = years * 12
    if rate == 0:
        required = (target - principal) / n_months
    else:
        future_principal = principal * ((1 + r_monthly) ** n_months)
        required = (target - future_principal) * r_monthly / (((1 + r_monthly) ** n_months) - 1)
    return required / 10000

def get_side_hustle_suggestion(gap_amount):
    """不足金額に応じた副業提案"""
    if gap_amount <= 0: return "🎉 目標達成済み", "今のペースで完璧です！", "success"
    if gap_amount <= 1.0: return "🌱 Level 1: ポイ活・不用品販売", "隙間時間でできることから始めましょう。", "info"
    if gap_amount <= 3.0: return "✏️ Level 2: Webライター・軽作業", "クラウドソーシングで案件を獲得しましょう。", "warning"
    if gap_amount <= 5.0: return "💻 Level 3: 動画編集・スキル販売", "高単価なスキルを身につけるチャンスです。", "warning"
    return "🚀 Level 4: 転職・事業・投資強化", "本業の年収アップや事業構築を検討しましょう。", "error"