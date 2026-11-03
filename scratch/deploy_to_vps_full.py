import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

def run(cmd):
    print(f"\n>>> Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    while not stdout.channel.exit_status_ready():
        time.sleep(0.5)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(out)
    if err:
        print("ERR:", err)
    return stdout.channel.recv_exit_status()

# 1. Pull latest git on VPS
run("cd /var/www/withmore && git reset --hard && git pull origin main")

# 2. Build frontend on VPS
run("cd /var/www/withmore/frontend && npm run build")

# 3. Ensure lookbook_bundles table exists in backend/shop.db
vps_db_script = """
import sqlite3, json

for db_path in ['/var/www/withmore/backend/shop.db', '/var/www/withmore/backend/app.db']:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Lookbook bundles table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS lookbook_bundles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_uz TEXT NOT NULL,
            title_ru TEXT,
            description_uz TEXT,
            description_ru TEXT,
            image TEXT,
            product_ids TEXT NOT NULL,
            discount_pct INTEGER DEFAULT 10,
            sort INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Insert sample bundles if empty
        cur.execute('SELECT COUNT(*) FROM lookbook_bundles')
        if cur.fetchone()[0] == 0:
            cur.execute('''
            INSERT INTO lookbook_bundles (title_uz, title_ru, description_uz, description_ru, product_ids, discount_pct, sort, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Milano Business Elite',
                'Деловой образ Милан',
                'Klassik toq-ko\\'k kostyum, oppoq paxtali ko\\'ylak va ipak galstuk jamlanmasi.',
                'Классический темно-синий костюм, белая рубашка и шелковый галстук.',
                json.dumps([1, 3, 6]),
                10,
                1,
                1
            ))
            cur.execute('''
            INSERT INTO lookbook_bundles (title_uz, title_ru, description_uz, description_ru, product_ids, discount_pct, sort, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Napoli Modern Grafit',
                'Современный образ Неаполь',
                'Zamonaviy grafit ikki tugmali kostyum, havorang nozik ko\\'ylak va tabiiy charm kamar.',
                'Графитовый костюм двойка, голубая рубашка и кожаный ремень.',
                json.dumps([2, 4, 5]),
                12,
                2,
                1
            ))

        conn.commit()
        print(f"Verified DB {db_path} successfully!")
        conn.close()
    except Exception as e:
        print(f"Error verifying {db_path}: {e}")
"""

run(f"python3 -c \"{vps_db_script}\"")

# 4. Restart backend service
run("systemctl restart whitmore && systemctl status whitmore --no-pager -n 5")

ssh.close()
print("\nDeployment complete!")
