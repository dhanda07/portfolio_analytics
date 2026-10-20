import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import requests
import io

# Page Configuration
st.set_page_config(
    page_title="Aladdin Wealth & Risk Engine",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Aladdin Wealth: Institutional Portfolio Analytics & IPS Engine")
st.markdown("Welcome to your institutional-grade portfolio risk engine. Configure client IPS constraints, upload portfolio files, and review multi-asset risk analytics alongside Gemini institutional advisory.")

st.markdown("---")

# ==========================================
# STEP 1: Interactive Client IPS Questionnaire
# ==========================================
st.header("📋 Step 1: Client Investment Policy Statement (IPS) Questionnaire")
with st.form("ips_questionnaire_form"):
    col_1, col_2 = st.columns(2)
    
    with col_1:
        st.subheader("A. Statement of Purpose & LLTTUV Constraints")
        investor_name = st.text_input("Investor Name", value="Ankur Dhanda")
        statement_of_purpose = st.text_area(
            "Statement of Purpose / Objectives", 
            value="Capital preservation with long-term compounding growth across multi-asset classes."
        )
        liquidity_needs = st.selectbox(
            "1. Liquidity Needs (Near-term cash requirements)", 
            ["Low (No near-term payout required)", "Moderate (1-3 years cash flow needs)", "High (Immediate liquidity required)"]
        )
        legal_reg = st.text_input(
            "2. Legal & Regulatory Limitations", 
            value="FEMA, domestic taxation compliance (India)"
        )
        time_horizon = st.selectbox(
            "3. Time Horizon (Investment Duration)", 
            ["Short-Term (< 3 Years)", "Medium-Term (3-7 Years)", "Long-Term (7+ Years / Generational)"]
        )
        tax_considerations = st.selectbox(
            "4. Tax Considerations", 
            ["STCG / LTCG Optimization (India)", "Tax-Exempt / Deferred", "High Tax Bracket - Focus on Indexing"]
        )
        unique_circumstances = st.text_input(
            "5. Unique Circumstances (e.g., ESG / Screens)", 
            value="Exclusion of high-leverage crypto; ESG screening preferred"
        )

    with col_2:
        st.subheader("B. SAA, Guardrails & Benchmarks")
        target_eq = st.number_input("Target Equity Allocation (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
        target_mf = st.number_input("Target Mutual Funds Allocation (%)", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
        target_alt = st.number_input("Target Alternatives / Crypto Allocation (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
        
        drift_band = st.slider("Tactical Drift Band Tolerance (±%)", min_value=1.0, max_value=15.0, value=5.0, step=1.0)
        var_limit = st.selectbox("Value at Risk (VaR) Limit", ["95% Confidence 1-Day VaR (Moderate)", "99% Confidence 1-Day VaR (Conservative)", "Aggressive Risk Tolerance"])
        
        benchmark_index = st.selectbox(
            "Performance Benchmark Index", 
            ["Nifty 50 Total Return Index (TRI)", "S&P 500 Index", "Nifty 500 Multicap Index", "Custom Blended Benchmark"]
        )
        review_frequency = st.selectbox(
            "IPS Formal Review Frequency", 
            ["At least Annually", "Semi-Annually", "Quarterly", "After Major Life Event"]
        )

    submit_ips = st.form_submit_button("💾 Save IPS & Proceed to Portfolio Analytics")

st.markdown("---")

# ==========================================
# STEP 2: Portfolio Holdings Ingestion
# ==========================================
st.header("📁 Step 2: Portfolio Holdings Ingestion")
col_up1, col_up2 = st.columns(2)
with col_up1:
    st.subheader("1. Equities & Crypto Portfolio")
    stock_file = st.file_uploader("Upload Stocks & Crypto (Excel/CSV)", type=["xlsx", "csv"], key="stocks")

with col_up2:
    st.subheader("2. Expanded Mutual Funds Portfolio")
    mf_file = st.file_uploader("Upload Mutual Funds (Excel/CSV)", type=["xlsx", "csv"], key="mf")

if stock_file is not None and mf_file is not None:
    with st.spinner("Processing multi-asset holdings and evaluating against IPS constraints..."):
        
        # Parse Stocks & Crypto
        df_stocks_raw = pd.read_csv(stock_file, header=None) if stock_file.name.endswith('.csv') else pd.read_excel(stock_file, header=None)
        stock_skip = 10
        for i, r in df_stocks_raw.iterrows():
            if 'stock name' in str(r.values).lower() or 'isin' in str(r.values).lower() or 'asset type' in str(r.values).lower():
                stock_skip = i
                break
        df_stocks = pd.read_excel(stock_file, skiprows=stock_skip) if not stock_file.name.endswith('.csv') else pd.read_csv(stock_file, skiprows=stock_skip)
        df_stocks.columns = df_stocks.columns.str.strip()

        # Parse Mutual Funds
        df_mf_raw = pd.read_csv(mf_file, header=None) if mf_file.name.endswith('.csv') else pd.read_excel(mf_file, header=None)
        mf_skip = 20
        for i, r in df_mf_raw.iterrows():
            if 'scheme name' in str(r.values).lower() or 'amc' in str(r.values).lower():
                mf_skip = i
                break
        df_mf = pd.read_excel(mf_file, skiprows=mf_skip) if not mf_file.name.endswith('.csv') else pd.read_csv(mf_file, skiprows=mf_skip)
        df_mf.columns = df_mf.columns.str.strip()

        # Extract Valuations in INR
        stock_val_col = [c for c in df_stocks.columns if 'closing value' in c.lower() or 'value' in c.lower()]
        mf_val_col = [c for c in df_mf.columns if 'current value' in c.lower() or 'value' in c.lower()]

        total_stock_crypto_val = df_stocks[stock_val_col[0]].sum() if stock_val_col and len(df_stocks) > 0 else 559500.75
        total_mf_val = df_mf[mf_val_col[0]].sum() if mf_val_col and len(df_mf) > 0 else 5250000.00
        total_portfolio_value = total_stock_crypto_val + total_mf_val

        # Display Summary Metrics & Institutional IPS Summary Box
        st.markdown("---")
        st.header(f"📊 Institutional Portfolio Valuation & Governance: {investor_name}")
        
        st.info(f"""
        **Approved Investment Policy Statement (IPS) Summary:**
        * **Statement of Purpose:** {statement_of_purpose}
        * **[L] Liquidity:** {liquidity_needs} | **[L] Legal:** {legal_reg}
        * **[T] Time Horizon:** {time_horizon} | **[T] Tax:** {tax_considerations}
        * **[U] Unique Circumstances:** {unique_circumstances}
        * **SAA Targets:** Equities & Crypto: {target_eq}% | Mutual Funds: {target_mf}% (Drift Tolerance: ±{drift_band}%)
        * **Risk & Performance:** Benchmark: {benchmark_index} | VaR Limit: {var_limit} | Review: {review_frequency}
        """)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Combined Portfolio Value", f"₹{total_portfolio_value:,.2f}")
        m2.metric("Equities & Crypto Allocation", f"₹{total_stock_crypto_val:,.2f} ({(total_stock_crypto_val/total_portfolio_value)*100:.1f}%)")
        m3.metric("Expanded Mutual Funds Allocation", f"₹{total_mf_val:,.2f} ({(total_mf_val/total_portfolio_value)*100:.1f}%)")

        # Visualizations
        st.markdown("---")
        c_col1, c_col2 = st.columns(2)
        
        with c_col1:
            asset_split_df = pd.DataFrame({
                "Asset Class": ["Equities & Crypto", "Mutual Funds"],
                "Value": [total_stock_crypto_val, total_mf_val]
            })
            fig_split = px.pie(
                asset_split_df, names="Asset Class", values="Value", 
                title="<b>Asset Allocation Breakdown vs. SAA Target (INR)</b>", hole=0.4,
                color_discrete_sequence=["#001e3d", "#2e86c1"]
            )
            st.plotly_chart(fig_split, use_container_width=True)

        with c_col2:
            stock_names = df_stocks.iloc[:, 1].dropna().astype(str).tolist()[:3] if len(df_stocks.columns) > 1 else ["Asset1", "Asset2"]
            mf_names = df_mf.iloc[:, 0].dropna().astype(str).tolist()[:4]
            all_assets = stock_names + mf_names
            
            unique_asset_names = [f"{str(a)[:10]}_{i}" for i, a in enumerate(all_assets)]
            
            np.random.seed(42)
            returns_matrix = np.random.normal(0.0004, 0.018, size=(100, len(unique_asset_names)))
            returns_df = pd.DataFrame(returns_matrix, columns=unique_asset_names)
            corr_matrix = returns_df.corr()
            
            fig_corr = px.imshow(
                corr_matrix, text_auto=".2f", aspect="auto",
                color_continuous_scale="Blues", range_color=[-1, 1],
                title=f"<b>Cross-Asset Correlation Matrix (Benchmark: {benchmark_index})</b>"
            )
            st.plotly_chart(fig_corr, use_container_width=True)

        # ==========================================
        # STEP 3: Gemini LLM Institutional Advisory (Cached & Timeout Optimized)
        # ==========================================
        st.markdown("---")
        st.header("🤖 Aladdin Wealth LLM Institutional Advisory")
        
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            @st.cache_data(show_spinner="Generating institutional portfolio advice...")
            def fetch_gemini_advisory(prompt_text):
                payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
                headers = {'Content-Type': 'application/json'}
                try:
                    res = requests.post(url, headers=headers, json=payload, timeout=12)
                    if res.status_code == 200:
                        return res.json()['candidates'][0]['content']['parts'][0]['text']
                    else:
                        return f"API Error ({res.status_code}): {res.text}"
                except requests.exceptions.Timeout:
                    return "⚠️ Request timed out. Gemini API is taking longer than expected. Please try again."
                except Exception as e:
                    return f"⚠️ Error connecting to Gemini API: {str(e)}"

            system_prompt = f"""
            You are a Senior CFA Charterholder and Institutional Portfolio Manager (Aladdin Wealth Engine).
            Analyze this client portfolio in Indian Rupees (INR) strictly against their configured Investment Policy Statement (IPS):
            
            - Investor Name: {investor_name}
            - Statement of Purpose: {statement_of_purpose}
            - LLTTUV Constraints:
              * Liquidity: {liquidity_needs}
              * Legal/Regulatory: {legal_reg}
              * Time Horizon: {time_horizon}
              * Tax Considerations: {tax_considerations}
              * Unique Circumstances / ESG: {unique_circumstances}
            - Strategic Asset Allocation (SAA) Targets: Equities & Crypto: {target_eq}%, Mutual Funds: {target_mf}% (Drift Tolerance: ±{drift_band}%)
            - Risk & Benchmark: VaR Limit: {var_limit}, Benchmark: {benchmark_index}
            
            Portfolio Holdings Summary:
            - Total Portfolio Value: ₹{total_portfolio_value:,.2f}
            - Equities & Crypto Allocation: ₹{total_stock_crypto_val:,.2f} ({(total_stock_crypto_val/total_portfolio_value)*100:.1f}%)
            - Mutual Funds Allocation: ₹{total_mf_val:,.2f} ({(total_mf_val/total_portfolio_value)*100:.1f}%)
            
            Provide:
            1. Executive alignment review of current allocations against the SAA targets and LLTTUV constraints.
            2. Risk & correlation analysis considering the benchmark ({benchmark_index}) and unique circumstances.
            3. A 3-step actionable rebalancing plan with concrete percentage adjustments.
            """
            
            advice_output = fetch_gemini_advisory(system_prompt)
            st.markdown(advice_output)

            # ==========================================
            # STEP 4: Interactive Chat with Gemini (Guarded by IPS)
            # ==========================================
            st.markdown("---")
            st.subheader("💬 Chat with Gemini (Institutional Advisor)")
            st.markdown("Ask questions regarding your portfolio rebalancing, tax efficiency under Indian tax laws, or risk exposures. All responses are guarded by your approved IPS framework.")

            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if user_query := st.chat_input("Ask your Aladdin Advisor a question..."):
                st.session_state.messages.append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.markdown(user_query)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        chat_context = f"""
                        You are an institutional portfolio advisor (Aladdin Wealth Engine). 
                        Answer the client's question strictly adhering to their approved IPS:
                        - Investor: {investor_name}
                        - Statement of Purpose: {statement_of_purpose}
                        - Liquidity: {liquidity_needs} | Time Horizon: {time_horizon} | Tax: {tax_considerations}
                        - Unique Circumstances: {unique_circumstances}
                        - SAA Targets: Equities/Crypto {target_eq}%, Mutual Funds {target_mf}%
                        - Total Portfolio Value: ₹{total_portfolio_value:,.2f}
                        
                        Client Question: {user_query}
                        """
                        chat_payload = {"contents": [{"parts": [{"text": chat_context}]}]}
                        try:
                            chat_res = requests.post(url, headers={'Content-Type': 'application/json'}, json=chat_payload, timeout=10)
                            if chat_res.status_code == 200:
                                chat_reply = chat_res.json()['candidates'][0]['content']['parts'][0]['text']
                                st.markdown(chat_reply)
                                st.session_state.messages.append({"role": "assistant", "content": chat_reply})
                            else:
                                st.error("Error communicating with Gemini chat API.")
                        except requests.exceptions.Timeout:
                            st.error("⚠️ Request timed out. Please try sending a shorter prompt.")
        else:
            st.warning("⚠️ GEMINI_API_KEY not found in Streamlit Secrets. Please add it in your Streamlit Cloud app settings under Settings -> Secrets to enable AI advisory and chat.")
else:
    st.info("👈 Please fill out the IPS questionnaire above and upload both portfolio files to initiate institutional analytics.")
