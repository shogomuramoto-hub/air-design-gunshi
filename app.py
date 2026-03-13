import streamlit as st
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import japanize_matplotlib
import requests

# 1. ファーストビュー設定
st.set_page_config(page_title="Air Design 軍師", layout="centered")

st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #004aad;">そのABテストの『やめどき』、軍師が判定します。</h1>
        <p style="font-size: 1.2em;">統計学×利益シミュレーションで、判断ミスによる月間損失リスクを可視化。</p>
    </div>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False

# 2. ツール体験エリア
with st.container():
    st.subheader("🧪 テストデータを入力")
    col_set1, col_set2 = st.columns(2)
    
    with col_set1:
        profit_per_cv = st.number_input("CV1件あたりの期待利益 (円)", value=50000)
        monthly_budget = st.number_input("勝利案に投入予定の月間予算 (円)", value=1000000)
    
    with col_set2:
        test_type = st.selectbox("テスト形式", ["同時ABテスト", "前後比較（期間比較）"])
        n_variants = st.selectbox("比較する案の数", [2, 3, 4, 5], index=0)

    input_data = []
    cols = st.columns(n_variants)
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"**案 {chr(65+i)}**")
            cl = st.number_input(f"クリック", value=1000, key=f"cl_{i}")
            cv = st.number_input(f"CV数", value=20, key=f"cv_{i}")
            cpc = st.number_input(f"単価(CPC)", value=100, key=f"cpc_{i}")
            input_data.append({"name": f"案 {chr(65+i)}", "clicks": cl, "cvs": cv, "cpc": cpc})

if st.button("軍師に勝敗を判定させる"):
    st.session_state['analyzed'] = True

# 3. 判定結果の表示
if st.session_state['analyzed']:
    names = [d["name"] for d in input_data]
    clicks = np.array([d["clicks"] for d in input_data])
    conversions = np.array([d["cvs"] for d in input_data])
    cpcs = np.array([d["cpc"] for d in input_data])
    
    # 統計計算
    safe_clicks = np.where(clicks == 0, 1, clicks)
    cvrs = conversions / safe_clicks
    
    # ベイズサンプリング
    samples = 20000
    sim_cvrs = np.array([stats.beta(1+c, 1+cl-c).rvs(samples) for c, cl in zip(conversions, clicks)])
    sim_profits = (sim_cvrs * profit_per_cv) - cpcs[:, np.newaxis]
    
    current_best_idx = np.argmax(cvrs)
    best_indices = np.argmax(sim_profits, axis=0)
    probs_best = [np.mean(best_indices == i) for i in range(n_variants)]
    
    # 信頼度（簡易z-score）
    idx1, idx2 = (np.argsort(cvrs)[-1], np.argsort(cvrs)[-2]) if n_variants > 1 else (0,0)
    p_pool = (conversions[idx1] + conversions[idx2]) / (clicks[idx1] + clicks[idx2] + 1e-10)
    se = np.sqrt(p_pool * (1 - p_pool) * (1/safe_clicks[idx1] + 1/safe_clicks[idx2]) + 1e-10)
    reliability_score = min(100, stats.norm.cdf(abs(cvrs[idx1] - cvrs[idx2]) / se) * 100) if se > 0 else 0
    
    # 損失リスク
    max_profits = np.max(sim_profits, axis=0)
    risk_per_click = np.mean(np.maximum(max_profits - sim_profits[current_best_idx], 0))
    monthly_risk_yen = risk_per_click * (monthly_budget / cpcs[current_best_idx])

    st.divider()
    st.subheader("📊 判定結果：勝率シミュレーション")
    
    fig, ax = plt.subplots(figsize=(8, 4))
    for i in range(n_variants):
        ax.hist(sim_cvrs[i], bins=50, alpha=0.5, label=f"{names[i]} (勝率:{probs_best[i]:.1%})")
    ax.legend()
    st.pyplot(fig)

    # 4. リード獲得の壁
    st.markdown(f"""
        <div style="background-color: #f0f0f0; padding: 30px; border-radius: 10px; text-align: center; border: 2px dashed #ccc;">
            <h3 style="color: #333;">🔒 利益リスク・深層レポート</h3>
            <p>判断ミスによる想定損失は月間 <b>¥{int(monthly_risk_yen):,}</b> です。</p>
            <p>この数値を改善するための具体的なアドバイスをメールで送付します。</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("lead_form"):
        email = st.text_input("レポート送信先メールアドレス")
        company = st.text_input("会社名")
        trouble = st.multiselect("現在のお悩み", ["自社制作の限界", "代理店への不満", "勝率向上"])
        submitted = st.form_submit_button("軍師の深層レポートを受け取る")
        
        if submitted:
            if email and company:
                # Zapier連携（URLがあれば有効化）
                # requests.post("YOUR_ZAPIER_URL", json={"email": email, "company": company})
                st.success(f"✅ ありがとうございます！{email} 宛に詳細レポートを送付します。")
                st.balloons()
