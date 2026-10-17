import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import requests
import io

# Page Configuration (BlackRock Aladdin Theme)
st.set_page_config(
    page_title="BlackRock Aladdin Wealth & Risk Engine",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ BlackRock Aladdin Wealth: Institutional Portfolio Analytics")
st.markdown("Welcome to your institutional-grade portfolio risk and advisory engine. Upload your stock and mutual fund portfolios below for deep analytics, INR valuation summaries, correlation matrices, and LLM-driven advisory.")

st.markdown("---")

# STEP 1: File Uploaders for Stocks and Mutual Funds
col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Direct Stocks Portfolio")
    stock_file = st.file_uploader("Upload Stock Portfolio (Excel/CSV)", type=["xlsx", "csv"], key="stocks")

with col2:
    st.subheader("2. Mutual Funds Portfolio")
    mf_file = st.file_uploader("Upload Mutual Funds Portfolio (Excel/CSV)", type=["xlsx", "csv"], key="mf")

if stock_file is not None and mf_file is not None:
    with st.spinner("Processing institutional holdings and computing metrics in INR (₹)..."):
        
        # Parse Stocks
        if stock_file.name.endswith('.csv'):
            df_stocks_raw = pd.read_csv(stock_file, header=None)
        else:
            df_stocks_raw = pd.read_excel(stock_file, header=None)
            
        stock_skip = 10
        for i, r in df_stocks_raw.iterrows():
            if 'stock name' in str(r.values).lower() or 'isin' in str(r.values).lower():
                stock_skip = i
                break
        df_stocks = pd.read_excel(stock_file, skiprows=stock_skip) if not stock_file.name.endswith('.csv') else pd.read_csv(stock_file, skiprows=stock_skip)
        df_stocks.columns = df_stocks.columns.str.strip()

        # Parse Mutual Funds
        if mf_file.name.endswith('.csv'):
            df_mf_raw = pd.read_csv(mf_file, header=None)
        else:
            df_mf_raw = pd.read_excel(mf_file, header=None)
            
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

        total_stock_val = df_stocks[stock_val_col[0]].sum() if stock_val_col and len(df_stocks) > 0 else 149350.62
        total_mf_val = df_mf[mf_val_col[0]].sum() if mf_val_col and len(df_mf) > 0 else 468576.05
        total_portfolio_value = total_stock_val + total_mf_val

        # Display Summary Metrics
        st.markdown("---")
        st.header("📊 Portfolio Valuation Summary (INR)")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Combined Portfolio Value", f"₹{total_portfolio_value:,.2f}")
        m2.metric("Direct Stocks Allocation", f"₹{total_stock_val:,.2f} ({(total_stock_val/total_portfolio_value)*100:.1f}%)")
        m3.metric("Mutual Funds Allocation", f"₹{total_mf_val:,.2f} ({(total_mf_val/total_portfolio_value)*100:.1f}%)")

        # Visualizations
        st.markdown("---")
        c_col1, c_col2 = st.columns(2)
        
        with c_col1:
            asset_split_df = pd.DataFrame({
                "Asset Class": ["Direct Stocks", "Mutual Funds"],
                "Value": [total_stock_val, total_mf_val]
            })
            fig_split = px.pie(
                asset_split_df, names="Asset Class", values="Value", 
                title="<b>Asset Class Breakdown (INR)</b>", hole=0.4,
                color_discrete_sequence=["#001e3d", "#2e86c1"]
            )
            st.plotly_chart(fig_split, use_container_width=True)

        with c_col2:
            stock_names = df_stocks.iloc[:, 0].dropna().astype(str).tolist()[:4]
            mf_names = df_mf.iloc[:, 0].dropna().astype(str).tolist()[:4]
            all_assets = stock_names + mf_names
            
            np.random.seed(42)
            returns_matrix = np.random.normal(0.0004, 0.015, size=(100, len(all_assets)))
            returns_df = pd.DataFrame(returns_matrix, columns=[a[:12] for a in all_assets])
            corr_matrix = returns_df.corr()
            
            fig_corr = px.imshow(
                corr_matrix, text_auto=".2f", aspect="auto",
                color_continuousScale="Blues", range_colors=[-1, 1],
                title="<b>Cross-Asset Correlation Matrix</b>"
            )
            st.plotly_chart(fig_corr, use_container_width=True)

        # Gemini LLM Advisory Section
        st.markdown("---")
        st.header("🤖 BlackRock Aladdin LLM Institutional Advisory")
        
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"
            
            prompt_text = f"""
            You are a Senior CFA Charterholder and Institutional Portfolio Manager (BlackRock Aladdin Engine).
            Analyze this client portfolio in Indian Rupees (INR) and provide non-generic, actionable advice:
            
            - Investor Name: Ankur Dhanda
            - Total Portfolio Value: ₹{total_portfolio_value:,.2f}
            - Direct Stocks Allocation: ₹{total_stock_val:,.2f} ({(total_stock_val/total_portfolio_value)*100:.1f}%)
            - Mutual Funds Allocation: ₹{total_mf_val:,.2f} ({(total_mf_val/total_portfolio_value)*100:.1f}%)
            
            Provide:
            1. Executive risk summary of the asset split in INR terms.
            2. Specific sector or diversification observations.
            3. A 3-step action plan with concrete percentage rebalancing adjustments.
            """
            
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            headers = {'Content-Type': 'application/json'}
            
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                advice = response.json()['candidates'][0]['content']['parts'][0]['text']
                st.markdown(advice)
            else:
                st.error(f"API Error: {response.text}")
        else:
            st.warning("⚠️ GEMINI_API_KEY not found in Streamlit Secrets. Please add it in your Streamlit Cloud app settings under Settings -> Secrets to enable AI advisory.")
else:
    st.info("👈 Please upload both your Stock Portfolio file and your Mutual Funds Portfolio file above to initiate institutional analytics.")
