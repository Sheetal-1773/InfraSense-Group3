-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create component_metrics table (will be converted to hypertable)
-- Note: This script runs on first startup. The actual table creation
-- is handled by SQLAlchemy models.py. This sets up TimescaleDB
-- specific configurations.

-- After tables are created, run these commands to convert to hypertable:
-- SELECT create_hypertable('component_metrics', 'timestamp', if_not_exists => TRUE);

-- Enable compression for data older than 7 days
-- ALTER TABLE component_metrics SET (
--   timescaledb.compress,
--   timescaledb.compress_segmentby = 'component_id, metric_name'
-- );

-- Add compression policy (compress after 7 days)
-- SELECT add_compression_policy('component_metrics', INTERVAL '7 days');

-- Add retention policy (drop data after 90 days)
-- SELECT add_retention_policy('component_metrics', INTERVAL '90 days');