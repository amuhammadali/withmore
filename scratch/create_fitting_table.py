import os
import sqlite3

def ensure_tables(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fitting_appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER REFERENCES customers(id),
        customer_name VARCHAR(120) DEFAULT '',
        customer_phone VARCHAR(32) DEFAULT '',
        tg_username VARCHAR(64) DEFAULT '',
        product_id INTEGER REFERENCES products(id),
        product_name VARCHAR(200) DEFAULT '',
        suit_size VARCHAR(32) DEFAULT '',
        date VARCHAR(16),
        time_slot VARCHAR(32),
        location VARCHAR(200) DEFAULT 'Withmore Bespoke Atelier (Toshkent)',
        notes TEXT DEFAULT '',
        status VARCHAR(24) DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS ix_fitting_appointments_customer_id ON fitting_appointments (customer_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_fitting_appointments_date ON fitting_appointments (date);")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_fitting_appointments_status ON fitting_appointments (status);")
    conn.commit()
    conn.close()
    print(f"Table fitting_appointments ensured on {db_path}!")

if __name__ == "__main__":
    for path in ["whitmore.db", "backend/whitmore.db", r"c:\Users\muham\OneDrive\Desktop\withmore\whitmore.db"]:
        if os.path.exists(path):
            ensure_tables(path)

