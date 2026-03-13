import streamlit as st
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import time

# --- 1. UIカスタム設定（CSS） ---
st.set_page_config(page_title="Air Design Gunshi", layout="wide")

st.markdown("""
    <style>
    /* 全体の背景とフォント */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* ヘッダーの高級感 */
    .header-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e1b4b 100%);
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    /* 入力カードの装飾 */
    .input-card {
        background-color: #1f2937;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #374151;
    }
    
    /* 判定結果のカード */
    .result-card {
        background: #ffffff;
        color: #111827;
        padding: 30px;
        border-radius: 15px;
        border-left: 8px solid #3b82f6;
    }
    
    /* ボタンの高級感 */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        font-weight: bold;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ファーストビュー ---
st.markdown("""
    <div class="header-box">
        <h1 style="color: #f8fafc; font-size: 2.8em; margin-bottom: 10px;">Air Design 軍師</h1>
        <p style="color: #cbd5e1; font-size: 1.2em;">そのABテストに、プロの『終止符』と『利益の最大化』を。</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. 入力エリア ---
st.markdown("### 📊 Test Parameters")
with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        profit_per_cv = st.number_input("CV1件あたりの利益 (¥)", value=50000, step=1000)
    with col2:
        monthly_budget = st.number_input("月間運用予算 (¥)", value=1000000, step=10000)
    with col3:
        n_variants = st.select_slider("比較案数", options=[2, 3, 4, 5], value=2)

st.markdown("---")

# 入力グリッド
input_data = []
cols = st.columns(n_variants)
for i, col in enumerate(cols):
    with col:
        st.markdown(f"#### Variant {chr(65+i)}")
        cl = st.number_input(f"Clicks", value=1500, key=f"cl_{i}")
        cv = st.number_input(f"CVs", value=30, key=f"cv_{i}")
        cpc = st.number_input(f"CPC (¥)", value=120, key=f"cpc_{i}")
        input_data.append({"name": f"Variant {chr(65+i)}", "clicks": cl, "cvs": cv, "cpc": cpc})

# --- 4. 解析アクション ---
if st.button("RUN ANALYSIS - 軍師の診断を開始"):
    with st.spinner('🔮 クリエイティブの深層心理と統計データを照合中...'):
        time.sleep(2) # 演出用の待ち時間
        
        # --- (計算ロジック) ---
        names = [d["name"] for d in input_data]
        clicks = np.array([d["clicks"] for d in input_data])
        conversions = np.array([d["cvs"] for d in input_data])
        cpcs = np.array([d["cpc"] for d in input_data])
        cvrs = conversions / np.where(clicks == 0, 1, clicks)
        
        # 簡易ベイズシミュレーション
        samples = 20000
        sim_cvrs = np.array([stats.beta(1+c, 1+cl-c).rvs(samples) for c, cl in zip(conversions, clicks)])
        sim_profits = (sim_cvrs * profit_per_cv) - cpcs[:, np.newaxis]
        
        current_best_idx = np.argmax(cvrs)
        best_indices = np.argmax(sim_profits, axis=0)
        probs_best = [np.mean(best_indices == i) for i in range(n_variants)]
        
        # 損失リスク計算
        max_profits = np.max(sim_profits, axis=0)
        risk_per_click = np.mean(np.maximum(max_profits - sim_profits[current_best_idx], 0))
        monthly_risk_yen = risk_per_click * (monthly_budget / cpcs[current_best_idx])

        # --- 5. 結果表示（高級カード） ---
        st.markdown(f"""
            <div class="result-card">
                <h2 style="margin-top:0;">🛡️ 分析結果レポート</h2>
                <p style="font-size: 1.1em; color: #4b5563;">現在の勝利案： <b>{names[current_best_idx]}</b></p>
                <hr>
                <div style="display: flex; justify-content: space-around; text-align: center;">
                    <div>
                        <p style="color: #6b7280; margin-bottom:0;">統計的勝率</p>
                        <h1 style="color: #2563eb;">{probs_best[current_best_idx]:.1%}</h1>
                    </div>
                    <div style="border-left: 1px solid #e5e7eb; padding-left: 40px;">
                        <p style="color: #ef4444; margin-bottom:0;">月間損失リスク</p>
                        <h1 style="color: #ef4444;">¥{int(monthly_risk_yen):,}</h1>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # グラフ
        col_graph, col_spacer = st.columns([2, 1])
        with col_graph:
            fig, ax = plt.subplots(figsize=(10, 5), facecolor='#ffffff')
            for i in range(n_variants):
                ax.hist(sim_cvrs[i], bins=50, alpha=0.6, label=f"{names[i]}", color=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'][i])
            ax.set_title("Conversion Rate Probability Distribution", fontsize=12)
            ax.legend()
            st.pyplot(fig)

        # 6. リード獲得エリア
        st.markdown("---")
        st.markdown("### 🔒 Deep Analysis Report")
        with st.container():
            l_col, r_col = st.columns([1, 1])
            with l_col:
                st.write("**軍師の深層レポートが生成されました**")
                st.write("・この結果から読み取れるターゲットの心理的バイアス")
                st.write("・デザイン要素（色・構図・コピー）の具体的な修正案")
                st.write("・次回のテストで狙うべき『勝ち筋』の言語化")
            with r_col:
                with st.form("lead_form"):
                    email = st.text_input("Report Delivery Email", placeholder="email@example.com")
                    company = st.text_input("Company Name")
                    st.form_submit_button("GET FULL REPORT")

st.markdown("<p style='text-align: center; color: #6b7280; margin-top: 50px;'>© Air Design - Scientific Design for High-Growth Brands</p>", unsafe_allow_html=True)
