PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source_documents (
    source_document_id TEXT PRIMARY KEY,
    entity_code TEXT NOT NULL,
    document_title TEXT NOT NULL,
    document_type TEXT NOT NULL,
    period_end TEXT,
    published_date TEXT,
    source_url TEXT,
    retrieved_at TEXT,
    sha256 TEXT,
    data_status TEXT NOT NULL CHECK (data_status IN ('official', 'derived', 'synthetic')),
    notes TEXT NOT NULL DEFAULT '',
    CHECK (data_status != 'official' OR (source_url IS NOT NULL AND source_url != '')),
    CHECK (data_status != 'official' OR (retrieved_at IS NOT NULL AND retrieved_at != '')),
    CHECK (data_status != 'official' OR length(sha256) = 64)
);

CREATE TABLE IF NOT EXISTS financial_facts (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_code TEXT NOT NULL,
    period_end TEXT NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('FY', 'Q1', 'Q2', 'Q3', 'Q4', 'H1', '9M', 'LTM')),
    statement_scope TEXT NOT NULL CHECK (statement_scope IN ('consolidated', 'separate', 'carve_out')),
    currency TEXT NOT NULL,
    unit TEXT NOT NULL CHECK (unit IN ('VND', 'VND_thousand', 'VND_mn', 'VND_bn')),
    line_item TEXT NOT NULL,
    value NUMERIC NOT NULL,
    data_status TEXT NOT NULL CHECK (data_status IN ('official', 'derived', 'synthetic')),
    source_document_id TEXT NOT NULL REFERENCES source_documents(source_document_id),
    source_page TEXT,
    extraction_method TEXT NOT NULL CHECK (extraction_method IN ('manual', 'table_extract', 'ocr', 'api', 'calculated')),
    notes TEXT NOT NULL DEFAULT '',
    loaded_at TEXT NOT NULL,
    UNIQUE (entity_code, period_end, period_type, statement_scope, currency, unit, line_item)
);

CREATE INDEX IF NOT EXISTS idx_financial_facts_lookup
ON financial_facts (entity_code, period_end, statement_scope, line_item);

CREATE TABLE IF NOT EXISTS validation_results (
    validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    check_code TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error')),
    passed INTEGER NOT NULL CHECK (passed IN (0, 1)),
    message TEXT NOT NULL,
    entity_code TEXT,
    period_end TEXT,
    context_json TEXT NOT NULL DEFAULT '{}',
    checked_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_validation_results_run
ON validation_results (run_id, severity, passed);

CREATE TABLE IF NOT EXISTS analytics_runs (
    run_id TEXT PRIMARY KEY,
    engine_version TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('running', 'failed', 'completed')),
    facts_sha256 TEXT NOT NULL,
    sources_sha256 TEXT NOT NULL,
    assumptions_sha256 TEXT,
    notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS valuation_results (
    valuation_result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES analytics_runs(run_id),
    scenario_name TEXT NOT NULL,
    unit_code TEXT,
    result_type TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    currency TEXT NOT NULL,
    unit TEXT NOT NULL,
    assumptions_json TEXT NOT NULL,
    UNIQUE (run_id, scenario_name, unit_code, result_type)
);
