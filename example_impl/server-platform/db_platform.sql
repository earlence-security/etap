DROP TABLE IF EXISTS platform_data;
DROP TABLE IF EXISTS platform_info;

CREATE TABLE platform_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    literal_id TEXT NOT NULL,
    data_table BLOB NOT NULL,
    data_index INTEGER NOT NULL,
    FOREIGN KEY (literal_id) REFERENCES platform_info (literal_id)
);

CREATE TABLE platform_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    literal_id TEXT NOT NULL,
    api_trigger TEXT NOT NULL,
    api_action TEXT NOT NULL,
    token_trigger TEXT NOT NULL,
    token_action TEXT NOT NULL,
    data_top INTEGER NOT NULL,
    data_end INTEGER NOT NULL
);