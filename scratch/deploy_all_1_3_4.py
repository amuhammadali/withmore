import os
import sys
import time
import tarfile
import paramiko

HOST = "162.35.37.77"
PORT = 22
USER = "root"
PASSWORD = "withmore2026"

print(f"Connecting to {USER}@{HOST}:{PORT}...", flush=True)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=20)
print("SSH Connection Successful!", flush=True)

def run(cmd, timeout=30):
    print(f"\n>>> Running: {cmd}", flush=True)
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    while not stdout.channel.exit_status_ready():
        line = stdout.readline()
        if line:
            print(line, end="", flush=True)
        time.sleep(0.05)
    for line in stdout:
        print(line, end="", flush=True)
    err = stderr.read().decode("utf-8", errors="replace")
    status = stdout.channel.recv_exit_status()
    if err and status != 0:
        print(f"STDERR: {err}", flush=True)
    return status

sftp = client.open_sftp()

# 1. Upload backend files
print("\n>>> Uploading backend models and routers...", flush=True)
sftp.put(r"C:\Users\muham\OneDrive\Desktop\withmore\backend\app\models.py", "/var/www/withmore/backend/app/models.py")
sftp.put(r"C:\Users\muham\OneDrive\Desktop\withmore\backend\app\routers\shop.py", "/var/www/withmore/backend/app/routers/shop.py")
sftp.put(r"C:\Users\muham\OneDrive\Desktop\withmore\backend\app\routers\admin_ops.py", "/var/www/withmore/backend/app/routers/admin_ops.py")
print("Backend files uploaded successfully!", flush=True)

# 2. Pack and upload frontend/dist
print("\n>>> Packing and uploading frontend/dist...", flush=True)
tar_path = r"C:\Users\muham\OneDrive\Desktop\withmore\dist_bundle.tar.gz"
if os.path.exists(tar_path):
    os.remove(tar_path)

with tarfile.open(tar_path, "w:gz") as tar:
    tar.add(r"C:\Users\muham\OneDrive\Desktop\withmore\frontend\dist", arcname="dist")

sftp.put(tar_path, "/var/www/withmore/dist_bundle.tar.gz")
sftp.close()
if os.path.exists(tar_path):
    os.remove(tar_path)

# 3. SQLite migration on VPS
vps_migration_py = """
import sqlite3, json

for db in ['/var/www/withmore/whitmore.db', '/var/www/withmore/data/whitmore.db']:
    try:
        conn = sqlite3.connect(db)
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
        cur.execute('PRAGMA table_info(customers)')
        cols = [col[1] for col in cur.fetchall()]
        if 'bonus_balance' not in cols:
            cur.execute('ALTER TABLE customers ADD COLUMN bonus_balance INTEGER DEFAULT 0')
        if 'referral_code' not in cols:
            cur.execute("ALTER TABLE customers ADD COLUMN referral_code TEXT DEFAULT ''")
        if 'referred_by_id' not in cols:
            cur.execute('ALTER TABLE customers ADD COLUMN referred_by_id INTEGER')

        # Check and seed lookbooks if empty
        cur.execute('SELECT COUNT(*) FROM lookbook_bundles')
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute('''
            INSERT INTO lookbook_bundles (title_uz, title_ru, description_uz, description_ru, product_ids, discount_pct, sort, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Milano Executive Look',
                'Деловой образ Милано',
                'To\\'q ko\\'k nafis kostyum, 100% paxta oq ko\\'ylak va qimmatbaho ipak galstuk uyg\\'unligi. Muhim biznes uchrashuvlari va tantanalar uchun mukammal to\\'liq obraz.',
                'Классический темно-синий костюм, белая хлопковая рубашка и шелковый галстук.',
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
                'Zamonaviy grafit ikki tugmali kostyum, havorang nozik ko\\'ylak va tabiiy charm kamar. Noodatiy va bejirim did sohiblari uchun.',
                'Графитовый костюм двойка, голубая рубашка и кожаный ремень.',
                json.dumps([2, 4, 5]),
                12,
                2,
                1
            ))

        conn.commit()
        print(f"Migrated and checked {db} successfully!")
        conn.close()
    except Exception as e:
        print(f"Error migrating {db}: {e}")
"""

# 4. Unpack dist, run db migration, and restart service
run("""cd /var/www/withmore
python3 -c \"%s\"
rm -rf frontend/dist
tar -xzf dist_bundle.tar.gz -C frontend/
rm -f dist_bundle.tar.gz
ls -la frontend/dist
""" % vps_migration_py.replace('"', '\\"'))

run("systemctl restart whitmore && systemctl status whitmore --no-pager -n 7")

client.close()
print("\n🎉 All 3 features successfully deployed to VPS!", flush=True)

