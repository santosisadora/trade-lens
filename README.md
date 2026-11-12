# TradeLens: Snowflake AI Risk Agent

A native Streamlit-in-Snowflake application that monitors capital markets trading data (equities and bonds) and utilizes an LLM (Snowflake Cortex) to explain risk anomalies to stakeholders.

## The Business Problem
Risk analysts process massive daily trade volumes and struggle to quickly triage anomalous transactions. Traditional dashboards show raw metrics but lack the plain-text context needed for immediate decision-making. Furthermore, generic AI models hallucinate when exposed to raw tables without strict business logic.

## The Architecture
This project replicates an enterprise AI workflow using a two-plane architecture:
1. **Deterministic Plane (Semantic Layer):** A SQL View (`v_trade_risk_analysis`) acts as the semantic layer, defining dimensional metrics (30-day moving averages, variance ratios) and strict business rules for flagging trades. 
2. **Probabilistic Plane (AI Agent):** A native Snowflake Cortex LLM reads exclusively from the governed semantic layer to generate mathematically accurate, fully auditable risk narratives.

## Tech Stack
* **Database & Compute:** Snowflake
* **Semantic Modeling:** Snowflake SQL Views (Window functions, logic thresholds)
* **AI/LLM:** Snowflake Cortex (`mistral-7b`)
* **Frontend:** Streamlit (deployed natively in Snowsight)

## Files
* `commands.sql`: Contains the DDL for warehouse provisioning, synthetic data ingestion (Equities/Bonds), and the semantic view creation.
* `streamlit_app.py`: The Streamlit application UI and Cortex LLM integration.