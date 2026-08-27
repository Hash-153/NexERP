-- ==============================================================================
-- NexERP Enterprise - PostgreSQL Initialization Script
-- Creates extensions, roles, and database configuration.
-- Run once on first database initialization.
-- ==============================================================================

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";     -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";       -- Trigram fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gist";    -- Exclusion constraint support
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- Query performance monitoring

-- Performance settings (can be tuned based on instance memory)
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Create read-only analytics role (for BI tools / Metabase / Redash)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'nexerp_readonly') THEN
        CREATE ROLE nexerp_readonly WITH LOGIN PASSWORD 'readonly_changeme' NOINHERIT;
    END IF;
END $$;

-- Grant schema privileges to readonly role after migrations create tables
-- (run again after first alembic upgrade head)
-- GRANT USAGE ON SCHEMA public TO nexerp_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO nexerp_readonly;
