-- 1. Create a dedicated compute warehouse
CREATE OR REPLACE WAREHOUSE tradelens_wh
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- 2. Create the database and schema
CREATE OR REPLACE DATABASE tradelens_db;
CREATE OR REPLACE SCHEMA risk_analytics;

-- 3. Set the context for the session
USE WAREHOUSE tradelens_wh;
USE DATABASE tradelens_db;
USE SCHEMA risk_analytics;


-- 1. Create the table for raw trades
CREATE OR REPLACE TABLE raw_trades (
    trade_id VARCHAR(50) DEFAULT UUID_STRING(),
    trade_timestamp TIMESTAMP_NTZ
        DEFAULT CURRENT_TIMESTAMP(),
    instrument_type VARCHAR(20),
    ticker_symbol VARCHAR(20),
    counterparty VARCHAR(50),
    notional_value NUMBER(38, 2),
    trader_id VARCHAR(20)
);

-- 2. Insert standard synthetic data
INSERT INTO raw_trades (
    trade_timestamp,
    instrument_type,
    ticker_symbol,
    counterparty,
    notional_value,
    trader_id
)
VALUES
(DATEADD(hour, -48, CURRENT_TIMESTAMP()),
    'Equity', 'AAPL', 'Goldman Sachs',
    250000.00, 'TRD-01'),
(DATEADD(hour, -47, CURRENT_TIMESTAMP()),
    'Bond', 'US-T-10Y', 'JPMorgan',
    1500000.00, 'TRD-02'),
(DATEADD(hour, -45, CURRENT_TIMESTAMP()),
    'Equity', 'MSFT', 'Morgan Stanley',
    320000.00, 'TRD-01'),
(DATEADD(hour, -24, CURRENT_TIMESTAMP()),
    'Equity', 'TSLA', 'Citigroup',
    180000.00, 'TRD-03'),
(DATEADD(hour, -23, CURRENT_TIMESTAMP()),
    'Bond', 'CORP-IBM', 'Barclays',
    850000.00, 'TRD-02');

-- 3. Insert ANOMALIES for the AI to catch
INSERT INTO raw_trades (
    trade_timestamp,
    instrument_type,
    ticker_symbol,
    counterparty,
    notional_value,
    trader_id
)
VALUES
-- Anomaly 1: Massive notional value
(DATEADD(hour, -2, CURRENT_TIMESTAMP()),
    'Equity', 'AAPL', 'Unknown-Fund-X',
    85000000.00, 'TRD-01'),
-- Anomaly 2: High value, strange counterparty
(DATEADD(hour, -1, CURRENT_TIMESTAMP()),
    'Bond', 'JUNK-BND-01', 'Offshore-Entity-Y',
    12000000.00, 'TRD-99');




    -- Create the semantic layer (View) combining dimensions and business logic metrics
CREATE OR REPLACE VIEW v_trade_risk_analysis AS
SELECT
    trade_id,
    trade_timestamp,
    instrument_type,
    ticker_symbol,
    counterparty,
    notional_value,
    trader_id,

    -- Metric 1: Calculate the average for this specific instrument type
    AVG(notional_value) OVER(PARTITION BY instrument_type) AS avg_instrument_notional,

    -- Metric 2: Ratio of this trade compared to the instrument average
    (notional_value / NULLIF(AVG(notional_value) OVER(PARTITION BY instrument_type), 0)) AS variance_ratio,

    -- Business Logic: Flag anomalous trades based on thresholds
    CASE
        WHEN notional_value > 5000000 THEN TRUE
        WHEN counterparty ILIKE '%Unknown%' OR counterparty ILIKE '%Offshore%' THEN TRUE
        ELSE FALSE
    END AS is_risk_flagged,

    -- Dimension: Human-readable context for the AI Agent downstream
    CASE
        WHEN notional_value > 5000000 AND (counterparty ILIKE '%Unknown%' OR counterparty ILIKE '%Offshore%')
            THEN 'Critical Breach: Value exceeds $5M limit AND high-risk counterparty detected.'
        WHEN notional_value > 5000000
            THEN 'Breach: Trade value exceeds $5M hard limit.'
        WHEN counterparty ILIKE '%Unknown%' OR counterparty ILIKE '%Offshore%'
            THEN 'Breach: Unapproved or high-risk counterparty.'
        ELSE 'Clear: Trade within normal parameters.'
    END AS risk_reason_context
FROM raw_trades;

-- Test the semantic layer to see the flags in action
SELECT * FROM v_trade_risk_analysis ORDER BY trade_timestamp DESC;