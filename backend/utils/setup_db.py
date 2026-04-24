# setup_db.py
from backend.utils.db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS policies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    provider VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS policies (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,

    min_age INT,
    max_age INT,

    min_income INT,
    min_coverage INT,

    category TEXT,
    risk_level TEXT
);
""")

conn.commit()
cur.close()
conn.close()

print("Table created successfully!")