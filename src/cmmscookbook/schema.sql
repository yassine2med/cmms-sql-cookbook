CREATE TABLE assets (
    asset_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    install_year INTEGER
);
CREATE TABLE technicians (
    tech_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    trade TEXT NOT NULL
);
CREATE TABLE work_orders (
    wo_id INTEGER PRIMARY KEY,
    asset_id TEXT NOT NULL REFERENCES assets(asset_id),
    type TEXT NOT NULL CHECK (type IN ('PM', 'CM')),
    priority INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 4),
    status TEXT NOT NULL CHECK (status IN ('Open', 'In Progress', 'Closed')),
    opened_at TEXT NOT NULL,
    started_at TEXT,
    closed_at TEXT,
    tech_id INTEGER REFERENCES technicians(tech_id),
    labor_hours REAL NOT NULL DEFAULT 0,
    description TEXT
);
CREATE INDEX idx_wo_asset ON work_orders(asset_id);
CREATE INDEX idx_wo_status ON work_orders(status);
