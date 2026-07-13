FACT_REQUIRED_COLUMNS = {
    "entity_code",
    "period_end",
    "period_type",
    "statement_scope",
    "currency",
    "unit",
    "line_item",
    "value",
    "data_status",
    "source_document_id",
    "source_page",
    "extraction_method",
    "notes",
}

SOURCE_REQUIRED_COLUMNS = {
    "source_document_id",
    "entity_code",
    "document_title",
    "document_type",
    "period_end",
    "published_date",
    "source_url",
    "retrieved_at",
    "sha256",
    "data_status",
    "notes",
}

PERIOD_TYPES = {"FY", "Q1", "Q2", "Q3", "Q4", "H1", "9M", "LTM"}
STATEMENT_SCOPES = {"consolidated", "separate", "carve_out"}
UNITS = {"VND", "VND_thousand", "VND_mn", "VND_bn"}
DATA_STATUSES = {"official", "derived", "synthetic"}
EXTRACTION_METHODS = {"manual", "table_extract", "ocr", "api", "calculated"}

CANONICAL_LINE_ITEMS = {
    "revenue",
    "cogs",
    "gross_profit",
    "ebitda",
    "ebit",
    "interest_expense",
    "pretax_income",
    "tax_expense",
    "net_income",
    "total_assets",
    "total_liabilities",
    "total_equity",
    "current_assets",
    "current_liabilities",
    "cash",
    "inventory",
    "receivables",
    "payables",
    "total_debt",
    "operating_cash_flow",
    "investing_cash_flow",
    "financing_cash_flow",
    "fx_cash_effect",
    "opening_cash",
    "ending_cash",
    "capex",
    "shares_outstanding",
}

NON_NEGATIVE_LINE_ITEMS = {
    "revenue",
    "gross_profit",
    "ebitda",
    "total_assets",
    "total_liabilities",
    "total_equity",
    "current_assets",
    "current_liabilities",
    "cash",
    "inventory",
    "receivables",
    "payables",
    "total_debt",
    "opening_cash",
    "ending_cash",
    "shares_outstanding",
}

NON_POSITIVE_LINE_ITEMS = {"cogs", "interest_expense", "tax_expense", "capex"}
