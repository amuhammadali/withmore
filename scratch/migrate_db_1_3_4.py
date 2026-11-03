import sqlite3

for db_path in ['whitmore.db', 'backend/whitmore.db']:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS lookbook_bundles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_uz TEXT NOT NULL,
            title_ru TEXT DEFAULT '',
            description_uz TEXT DEFAULT '',
            description_ru TEXT DEFAULT '',
            image TEXT DEFAULT '',
            product_ids TEXT DEFAULT '[]',
            discount_pct INTEGER DEFAULT 10,
            sort INTEGER DEFAULT 0,
            active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS broadcast_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            segment TEXT DEFAULT 'all',
            text TEXT NOT NULL,
            image_url TEXT DEFAULT '',
            button_text TEXT DEFAULT '',
            button_url TEXT DEFAULT '',
            sent_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'sent',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        # Check Customer table columns
        cur.execute("PRAGMA table_info(customers)")
        cols = [col[1] for col in cur.fetchall()]
        if 'bonus_balance' not in cols:
            cur.execute("ALTER TABLE customers ADD COLUMN bonus_balance INTEGER DEFAULT 0")
        if 'referral_code' not in cols:
            cur.execute("ALTER TABLE customers ADD COLUMN referral_code TEXT DEFAULT ''")
        if 'referred_by_id' not in cols:
            cur.execute("ALTER TABLE customers ADD COLUMN referred_by_id INTEGER")
        conn.commit()
        print(f"Database {db_path} migrated successfully!")
        conn.close()
    except Exception as e:
        print(f"Error on {db_path}: {e}")

