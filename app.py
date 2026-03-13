import requests # 外部へデータを飛ばすためのライブラリ

# --- (前略：計算ロジック) ---

if st.session_state.get('analyzed'):
    # ... (判定結果の表示) ...

    with st.form("lead_form"):
        email = st.text_input("レポート送信先メールアドレス")
        company = st.text_input("会社名")
        trouble = st.multiselect("現在のお悩み", ["自社制作の限界", "代理店への不満", "勝率向上"])
        
        submitted = st.form_submit_button("軍師の深層レポートをメールで受け取る")
        
        if submitted:
            if email and company:
                # ZapierのWebhook URL (Zapierで作ったURLをここに貼る)
                ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/XXXXXX/XXXXXX/"
                
                # 送信するデータ一式
                payload = {
                    "email": email,
                    "company": company,
                    "trouble": ", ".join(trouble),
                    "best_variant": names[current_best_idx],
                    "reliability": f"{reliability_score:.1f}%",
                    "loss_risk": int(monthly_risk_yen)
                }
                
                # Zapierにデータを飛ばす
                try:
                    requests.post(ZAPIER_WEBHOOK_URL, json=payload)
                    st.success("✅ リード情報を送信しました。Salesforceへの登録とメール送付を完了します。")
                    st.balloons()
                except:
                    st.error("送信に失敗しました。ネット環境を確認してください。")
            else:
                st.error("必須項目（メール・会社名）を入力してください。")
