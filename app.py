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
    page_title="Institutional Wealth & Risk Engine",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Institutional Wealth & Risk Engine: Portfolio Analytics & IPS Framework")
st.markdown("Welcome to your institutional-grade portfolio risk engine. Configure client IPS constraints, download sample templates or upload your portfolio files, and review multi-asset risk analytics alongside institutional LLM advisory.")

st.markdown("---")

# ==========================================
# HELPER: Sample File Generator & Downloader
# ==========================================
def create_sample_excel_files():
    # 1. Equities & Crypto Sample
    output_stock = io.BytesIO()
    with pd.ExcelWriter(output_stock, engine='openpyxl') as writer:
        meta_df = pd.DataFrame([["Institutional Stock & Crypto Portfolio"], ["Currency: INR (₹)"]])
        meta_df.to_excel(writer, sheet_name="Holdings", index=False, header=False)
        
        data_stocks = pd.DataFrame({
            "Asset Type": ["Equity", "Equity", "Crypto", "Equity"],
            "Stock Name": ["Reliance Industries", "Tata Consultancy Services", "Bitcoin (INR)", "HDFC Bank"],
            "Ticker": ["RELIANCE.NS", "TCS.NS", "BTC-INR", "HDFCBANK.NS"],
            "Quantity": [50, 30, 0.05, 100],
            "Closing Value": [145000.00, 120000.00, 285500.75, 109000.00]
        })
        data_stocks.to_excel(writer, sheet_name="Holdings", index=False, startrow=5)
    output_stock.seek(0)

    # 2. Mutual Funds Sample
    output_mf = io.BytesIO()
    with pd.ExcelWriter(output_mf, engine='openpyxl') as writer:
        meta_mf = pd.DataFrame([["Expanded Mutual Funds Portfolio"], ["Valuation Date: Current"]])
        meta_mf.to_excel(writer, sheet_name="MF_Holdings", index=False, header=False)
        
        data_mf = pd.DataFrame({
            "Scheme Name": ["Mirae Asset Large Cap Fund", "SBI Bluechip Fund", "Axis Growth Opportunities Fund", "Nippon India Small Cap Fund"],
            "AMC": ["Mirae Asset", "SBI Mutual Fund", "Axis Mutual Fund", "Nippon India"],
            "Units": [1500.50, 2200.00, 1800.25, 3100.00],
            "Current Value": [2250000.00, 1500000.00, 950000.00, 550000.00]
        })
        data_mf.to_excel(writer, sheet_name="MF_Holdings", index=False, startrow=10)
    output_mf.seek(0)
    
    return output_stock.getvalue(), output_mf.getvalue()

stock_bytes, mf_bytes = create_sample_excel_files()

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
# STEP 2: Portfolio Holdings Ingestion & Sample Downloads
# ==========================================
st.header("📁 Step 2: Portfolio Holdings Ingestion")
st.markdown("Download sample institutional templates below to test the engine, or upload your own portfolio files.")

dl_col1, dl_col2 = st.columns(2)
with dl_col1:
    st.download_button(
        label="📥 Download Sample Stocks & Crypto Template",
        data=stock_bytes,
        file_name="stock_crypto_portfolio.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
with dl_col2:
    st.download_button(
        label="📥 Download Sample Mutual Funds Template",
        data=mf_bytes,
        file_name="mf_portfolio.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.markdown("")
col_up1, col_up2 = st.columns(2)
with col_up1:
    stock_file = st.file_uploader("Upload Stocks & Crypto (Excel/CSV)", type=["xlsx", "csv"], key="stocks")

with col_up2:
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

        # Pre-calculate percentages for safe formatting
        stock_crypto_pct = (total_stock_crypto_val / total_portfolio_value) * 100
        mf_pct = (total_mf_val / total_portfolio_value) * 100

        # Display Summary Metrics & Institutional IPS Summary Box
        st.markdown("---")
        st.header(f"📊 Institutional Portfolio Valuation & Governance: {investor_name}")
        
        st.info(f"""
        **Approved Investment Policy Statement (IPS) Summary:**
        * **Statement of Purpose:** {statement_of_purpose}
        * **[L] Liquidity:** {liquidity_needs} | **[L] Legal:** {legal_reg}
        * **[T] Time Horizon:** {time_horizon} | **[T] Tax:** {tax_consider
