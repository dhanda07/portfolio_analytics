# ==========================================
# STEP 3: DeepSeek LLM Institutional Advisory
# ==========================================
st.markdown("---")
st.header("🤖 Institutional LLM Portfolio Advisory (DeepSeek)")

if "DEEPSEEK_API_KEY" in st.secrets:
    deepseek_key = st.secrets["DEEPSEEK_API_KEY"]
    # DeepSeek API Endpoint
    url = "https://api.deepseek.com/chat/completions"
    
    @st.cache_data(show_spinner="Generating institutional portfolio advice via DeepSeek...")
    def fetch_deepseek_advisory(prompt_text):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {deepseek_key}'
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a Senior CFA Charterholder and Institutional Portfolio Manager."},
                {"role": "user", "content": prompt_text}
            ],
            "stream": False
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
            else:
                return None
        except Exception:
            return None

    # system_prompt definition remains the same...
    advice_output = fetch_deepseek_advisory(system_prompt)
    
    if advice_output:
        st.markdown(advice_output)
    else:
        # Fallback summary if needed...
