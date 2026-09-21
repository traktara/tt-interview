CREATE TABLE IF NOT EXISTS authorities (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    region_code TEXT NOT NULL,
    region_name TEXT NOT NULL
);

-- Remove the retired project table when upgrading an existing database.
DROP TABLE IF EXISTS projects;

CREATE TABLE IF NOT EXISTS pipeline_status (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    report JSONB NOT NULL
);
