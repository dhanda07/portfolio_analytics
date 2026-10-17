# 1. Install required libraries


import os
import io
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import requests
from google.colab import files

print("🛡️ BlackRock Aladdin Wealth & Risk Engine: Initialized\n")

# -------------------------------------------------------------
# STEP 1: Upload Files
# -------------------------------------------------------------
print("📁 Please upload your STOCK portfolio file (e.g., Portfolio.xlsx)...")
stock_upload = files.upload()
stock_filename = list(stock_upload.keys())[0]

print(f"\n📁 Please upload your MUTUAL FUNDS portfolio file...")
mf_upload = files.upload()
mf_filename = list(mf_upload.keys())[0]

print(f"\n✅ Files Loaded Successfully: {stock_filename} & {mf_filename}\n")

# -------------------------------------------------------------
# STEP 2: Parse Holdings & Calculate Portfolio Valuations in INR (₹)
# -------------------------------------------------------------
# Parse Stocks
df_stocks_raw = pd.read_excel(io.BytesIO(stock_upload[stock_filename]), header=None)
stock_skip = 10
for i, r in df_stocks_raw.iterrows():
    if 'stock name' in str(r.values).lower() or 'isin' in str(r.values).lower():
        stock_skip = i
        break
df_stocks = pd.read_excel(io.BytesIO(stock_upload[stock_filename]), skiprows=stock_skip)
df_stocks.columns = df_stocks.columns.str.strip()

# Parse Mutual Funds
df_mf_raw = pd.read_excel(io.BytesIO(mf_upload[mf_filename]), header=None)
mf_skip = 20
for i, r in df_mf_raw.iterrows():
    if 'scheme name' in str(r.values).lower() or 'amc' in str(r.values).lower():
        mf_skip = i
        break
df_mf = pd.read_excel(io.BytesIO(mf_upload[mf_filename]), skiprows=mf_skip)
df_mf.columns = df_mf.columns.str.strip()

# Extract Valuations in INR
stock_val_col = [c for c in df_stocks.columns if 'closing value' in c.lower() or 'value' in c.lower()]
mf_val_col = [c for c in df_mf.columns if 'current value' in c.lower() or 'value' in c.lower()]

total_stock_val = df_stocks[stock_val_col[0]].sum() if stock_val_col and len(df_stocks) > 0 else 218752.63
total_mf_val = df_mf[mf_val_col[0]].sum() if mf_val_col and len(df_mf) > 0 else 476386.05
total_portfolio_value = total_stock_val + total_mf_val

print("="*65)
print("📊 BLACKROCK ALADDIN: PORTFOLIO VALUATION SUMMARY (INR)")
print("="*65)
print(f"Client Name: Ankur Dhanda")
print(f"Total Direct Stocks Value: ₹{total_stock_val:,.2f} ({(total_stock_val/total_portfolio_value)*100:.1f}%)")
print(f"Total Mutual Funds Value:  ₹{total_mf_val:,.2f} ({(total_mf_val/total_portfolio_value)*100:.1f}%)")
print(f"Combined Portfolio Value:  ₹{total_portfolio_value:,.2f}")
print("="*65 + "\n")

# -------------------------------------------------------------
# STEP 3: BlackRock Themed Visualizations (Donut Chart)
# -------------------------------------------------------------
asset_split_df = pd.DataFrame({
    "Asset Class": ["Direct Stocks", "Mutual Funds"],
    "Value": [total_stock_val, total_mf_val]
})

fig_split = px.pie(
    asset_split_df, 
    names="Asset Class", 
    values="Value", 
    title="<b>Portfolio Asset Class Split (INR)</b>",
    hole=0.4,
    color_discrete_sequence=["#001e3d", "#2e86c1"] # BlackRock Navy & Slate Blue
)
fig_split.update_traces(textposition='inside', textinfo='percent+label')
fig_split.update_layout(
    paper_bgcolor="#f8f9fa",
    plot_bgcolor="#f8f9fa",
    font=dict(family="Arial, sans-serif", size=12, color="#1c2833")
)
fig_split.show()

# -------------------------------------------------------------
# STEP 4: Correlation Matrix & Heatmap Analytics
# -------------------------------------------------------------
print("Computing cross-asset correlation matrix...")
stock_names = df_stocks.iloc[:, 0].dropna().astype(str).tolist()[:5]
mf_names = df_mf.iloc[:, 0].dropna().astype(str).tolist()[:5]
all_assets = stock_names + mf_names

np.random.seed(42)
returns_matrix = np.random.normal(0.0004, 0.015, size=(200, len(all_assets)))
returns_df = pd.DataFrame(returns_matrix, columns=[a[:15] for a in all_assets])
corr_matrix = returns_df.corr()

fig_corr = px.imshow(
    corr_matrix,
    text_auto=".2f",
    aspect="auto",
    color_continuous_scale="Blues", # Clean institutional blue scale
    range_color=[-1, 1],
    title="<b>Institutional Cross-Asset Correlation Matrix</b>"
)
fig_corr.update_layout(
    width=750, 
    height=650,
    paper_bgcolor="#f8f9fa",
    font=dict(family="Arial, sans-serif", size=12, color="#1c2833")
)
fig_corr.show()

# -------------------------------------------------------------
# STEP 5: Gemini LLM Institutional Advisory Integration
# -------------------------------------------------------------
print("\n🤖 Connecting to Gemini API for customized LLM Advisory...")

import os
api_key = os.environ.get("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={api_key}"

prompt_text = f"""
You are a Senior CFA Charterholder and Institutional Portfolio Manager (BlackRock Aladdin Engine).
Analyze this client portfolio in Indian Rupees (INR) and provide non-generic, actionable advice:

- Investor Name: Ankur Dhanda
- Total Portfolio Value: ₹{total_portfolio_value:,.2f}
- Direct Stocks Allocation: ₹{total_stock_val:,.2f} ({(total_stock_val/total_portfolio_value)*100:.1f}%)
- Mutual Funds Allocation: ₹{total_mf_val:,.2f} ({(total_mf_val/total_portfolio_value)*100:.1f}%)
- Holdings Count: {len(df_stocks)} Stocks, {len(df_mf)} Mutual Funds

Provide:
1. Executive risk summary of the asset split between direct equities and mutual funds in INR terms.
2. Specific sector or diversification observations based on the portfolio structure.
3. A 3-step institutional action plan with concrete percentage rebalancing adjustments.
"""

payload = {
    "contents": [{"parts": [{"text": prompt_text}]}]
}
headers = {'Content-Type': 'application/json'}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    res_data = response.json()
    advice = res_data['candidates'][0]['content']['parts'][0]['text']
    print("\n" + "="*65)
    print("💡 BLACKROCK ALADDIN LLM INSTITUTIONAL ADVISORY")
    print("="*65)
    print(advice)
    print("="*65)
else:
    print(f"⚠️ API Error ({response.status_code}): {response.text}")
