import streamlit as st
from snowflake.snowpark.context import get_active_session

# 1. Set to wide mode for a dashboard feel
st.set_page_config(
    page_title="TradeLens Risk Agent",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

    /* Main Background & Base Text - Deep Hero Canvas */
    .stApp {
        background-color: #060E1C; 
        color: #cbd5e1; /* slate-300 */
        font-family: 'Inter', sans-serif;
    }

    /* Headers - Plus Jakarta Sans */
    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }

    h1 {
        border-bottom: 1px solid #1E3252;
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
    }

    /* Metric Values (Glowing Cyan & JetBrains Mono) */
    [data-testid="stMetricValue"] {
        color: #06B6D4 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(6, 182, 212, 0.2);
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important; /* slate-400 */
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.8rem;
    }

    /* Primary Button - Double-L Logo Blue Accent */
    div.stButton > button:first-child {
        background-color: #2563EB !important;
        color: white !important;
        border: 1px solid #1D4ED8 !important;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #1D4ED8 !important;
        box-shadow: 0 0 15px rgba(37, 99, 235, 0.4);
    }

/* Custom AI Response Box - Informative & Elegant */
    .ai-box {
        background-color: #0B1528; 
        border: 1px solid #1E3252;
        border-top: 3px solid #06B6D4; /* Subtle cyan top accent instead of harsh left bar */
        padding: 1.5rem; 
        border-radius: 8px; 
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        font-size: 0.95rem; 
        line-height: 1.6; 
        margin-top: 1rem;
        color: #F8FAFC; /* Crisp white text for readability */
    }

    .ai-badge {
        display: inline-block;
        background: rgba(6, 182, 212, 0.1);
        color: #38BDF8;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
    }

    /* Terminal/Stack Tags inside AI box */
    .tech-tag {
        font-family: 'JetBrains Mono', monospace;
        background-color: #0B1528;
        color: #22D3EE;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        border: 1px solid #1E3252;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown(
    "<h1>TradeLens <span style='color: #06B6D4;'>"
    "Risk Intelligence</span></h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='color: #94a3b8; font-family: \"JetBrains Mono\", monospace; font-size: 0.9rem;'>"
    "&lt; Next-Gen Tech Solutions / Built for Real-World Scale. &gt;</p>",
    unsafe_allow_html=True
)
st.divider()

session = get_active_session()

# --- DATA FETCHING ---
sql_query = """
SELECT 
    trade_id, 
    instrument_type,
    counterparty, 
    notional_value, 
    risk_reason_context 
FROM tradelens_db.risk_analytics.v_trade_risk_analysis 
WHERE is_risk_flagged = TRUE
ORDER BY notional_value DESC
"""
df = session.sql(sql_query).to_pandas()

# --- KPI METRICS LAYER ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Flagged Trades", f"{len(df)}")
with col2:
    # Calculate critical exposures > $10M
    crit = len(df[df['NOTIONAL_VALUE'] > 10000000])
    st.metric("Critical Exposure Alerts", f"{crit}")
with col3:
    st.metric("AI Agent Status", "Online & Active")

st.divider()

# --- MAIN DASHBOARD LAYOUT (2 Columns) ---
left_col, right_col = st.columns([1.6, 1])

with left_col:
    st.markdown("### 🚨 Active Risk Anomalies")

    # Professional dataframe formatting
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "TRADE_ID": "Trade ID",
            "INSTRUMENT_TYPE": "Asset Class",
            "COUNTERPARTY": "Counterparty",
            "NOTIONAL_VALUE": st.column_config.NumberColumn(
                "Notional Value", format="$%d"
            ),
            "RISK_REASON_CONTEXT": "Semantic Rule Triggered"
        }
    )

with right_col:
    st.markdown("### 🤖 Ask Cortex Agent")

    # Enclose the AI tool in a bordered widget
    with st.container(border=True):
        st.markdown(
            "<p style='color: #cbd5e1; font-size: 0.9rem;'>"
            "Select a flagged trade to generate a "
            "stakeholder-ready explanation.</p>",
            unsafe_allow_html=True
        )

        selected_trade = st.selectbox(
            "Target Trade ID:",
            df['TRADE_ID'],
            label_visibility="collapsed"
        )

        if st.button("Generate Risk Analysis"):
            with st.spinner("Analyzing semantic layer..."):
                row = df[df['TRADE_ID'] == selected_trade].iloc[0]

                # Format numbers with commas for the LLM
                val = f"${row['NOTIONAL_VALUE']:,.2f}"

                p_text = (
                    "You are a Capital Markets Risk Analyst. "
                    "Explain this risk flag to a stakeholder. "
                    f"Trade: {row['TRADE_ID']}. "
                    f"Asset: {row['INSTRUMENT_TYPE']}. "
                    f"Party: {row['COUNTERPARTY']}. "
                    f"Value: {val}. "
                    f"Rule: {row['RISK_REASON_CONTEXT']} "
                    "Keep your answer under 3 sentences "
                    "and be highly professional."
                )

                cortex_query = f"""
                SELECT SNOWFLAKE.CORTEX.AI_COMPLETE(
                    'mistral-7b', 
                    $$ {p_text} $$
                )
                """

                try:
                    result = session.sql(cortex_query).collect()[0][0]
                    # Strip extra quotes from LLM output
                    clean_res = result.strip(' "\'')

                    st.markdown(
                        f"<div class='ai-box'>"
                        f"<div class='ai-badge'>✦ CORTEX AI INSIGHT</div>"
                        f"<div>{clean_res}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                except Exception as e:
                    st.error("Cortex execution failed.")
                    st.write(str(e))