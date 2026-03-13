import streamlit as st
import numpy as np
import scipy.stats as stats
import pandas as pd
import time

# --- 1. UIカスタム ---
st.set_page_config(page_title="ABテスト軍師 | 損得の判定", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; color: #1e293b; }
    .decision-card {
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        text-align: center;
    }
    .status-go { background-color: #dcfce7; border: 2px solid #22c55e; color: #166534; }
    .status-wait { background-color: #fef9c3; border: 2px solid #eab308; color: #854d0e; }
    .status-stop { background-color: #fee2e2; border: 2px solid #ef4444; color: #991b1b; }
    
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 1.5em !important;
        background: #1e3a8a !important;
        color: white !important;
        border-radius: 50px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 導入 ---
st.title("🛡️ ABテスト軍師")
st.write("複雑な統計学は不要です。データを入れれば「継続か、停止か」を軍師が断定します。")

# --- 3. 入力エリア ---
with st.expander("💰 利益の設定（ここを入れると「損した金額」がわかります）", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        profit_per_cv = st.number_input("商品1つ売れた時の利益 (円)", value=10000)
    with col2:
        monthly_budget = st.number_input("この広告の月間予算 (円)", value=500000)

st.markdown("### 📈 今のテスト結果を入れてください")
n_variants = st.radio("比較している案の数", [2, 3], horizontal=True)

input_data = []
cols = st.columns(n_variants)
for i, col in enumerate(cols):
    with col:
        st.markdown(f"**案 {chr(65+i)}**")
        cl = st.number_input(f"クリック数", value=1000 + i*100, key=f"cl_{i}")
        cv = st.number_input(f"獲得(CV)数", value=20 + i*5, key=f"cv_{i}")
        input_data.append({"name": f"案 {chr(65+i)}", "clicks": cl, "cvs": cv})

# --- 4. 解析 ---
if st.button("軍師に判断を仰ぐ"):
    with st.spinner('軍師がデータを精査中...'):
        time.sleep(1)
        
        clicks = np.array([d["clicks"] for d in input_data])
        cvs = np.array([d["cvs"] for d in input_data])
        cvrs = (cvs / np.where(clicks == 0, 1, clicks)) * 100
        
        # 勝率計算
        samples = 20000
        sim_cvrs = np.array([stats.beta(1+c, 1+cl-c).rvs(samples) for c, cl in zip(cvs, clicks)])
        win_rates = [np.mean(np.argmax(sim_cvrs, axis=0) == i) for i in range(n_variants)]
        best_idx = np.argmax(win_rates)
        
        # 損失額
        max_sim_cvrs = np.max(sim_cvrs, axis=0)
        loss_per_click = np.mean(max_sim_cvrs - sim_cvrs[best_idx])
        monthly_loss_yen = int(loss_per_click * monthly_budget * profit_per_cv / 100) # 修正：単位調整
        
        st.divider()
        # 判定メッセージ
        if win_rates[best_idx] > 0.95:
            st.markdown(f'<div class="decision-card status-go"><h2>【即停止】勝負あり</h2><p><b>案 {chr(65+best_idx)}</b> の勝利はほぼ間違いありません。他の案を止めて予算を集中させてください。</p></div>', unsafe_allow_html=True)
        elif win_rates[best_idx] > 0.75:
            st.markdown(f'<div class="decision-card status-wait"><h2>【継続】まだ差が不十分</h2><p><b>案 {chr(65+best_idx)}</b> が優勢ですが、偶然の可能性があります。あと少しデータを溜めましょう。</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="decision-card status-stop"><h2>【再考】どんぐりの背比べ</h2><p>どちらも決め手に欠けます。デザインのコンセプトを根本から変えた新案の投入を推奨します。</p></div>', unsafe_allow_html=True)

        # --- 5. グラフ（Streamlit標準チャートで文字化け回避） ---
        st.markdown("### 📊 獲得効率の比較 (CVR %)")
        chart_data = pd.DataFrame({
            '案': [d["name"] for d in input_data],
            '獲得率(%)': cvrs,
            '確信度': [f"{w:.0%}" for w in win_rates]
        })
        # 棒グラフを表示
        st.bar_chart(chart_data, x='案', y='獲得率(%)', color="#3b82f6")
        
        # 確信度の補足
        col_stats = st.columns(n_variants)
        for i, col in enumerate(col_stats):
            col.metric(f"案 {chr(65+i)} の確信度", f"{win_rates[i]:.0%}")

        # --- 6. お金の話 ---
        st.warning(f"💡 もし今すぐ勝利案に切り替えれば、月間でおよそ **¥{monthly_loss_yen:,}** の利益改善が見込めます。")

        st.markdown("---")
        st.markdown("### 🛡️ 軍師の深層レポートを受け取りますか？")
        with st.form("lead"):
            st.text_input("メールアドレス")
            st.form_submit_button("無料レポートを申し込む")
