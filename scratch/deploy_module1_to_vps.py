import os
import sys
import time
import tarfile
import subprocess
import paramiko

print("=== Starting Module 1 Deployment to VPS ===", flush=True)

# 1. Push to git
print(">>> Pushing git commit to GitHub...", flush=True)
res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
print("Git stdout:", res.stdout, flush=True)
print("Git stderr:", res.stderr, flush=True)

# 2. Connect to VPS
HOST = "162.35.37.77"
PORT = 22
USER = "root"
PASSWORD = "withmore2026"

print(f">>> Connecting SSH to {USER}@{HOST}:{PORT}...", flush=True)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=20)
print("SSH Connected successfully!", flush=True)

def run(cmd, timeout=30):
    print(f"\n>>> Remote: {cmd}", flush=True)
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
        print(f"Remote STDERR: {err}", flush=True)
    return status

# 3. Create SQLite table on VPS if not exists
create_table_sql = """
import sqlite3

db_path = '/var/www/withmore/whitmore.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS fitting_appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    product_id INTEGER,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    height_cm INTEGER,
    weight_kg INTEGER,
    fit_preference TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
)
''')
conn.commit()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fitting_appointments'")
print("Table check:", cur.fetchone())
conn.close()
"""

# 4. Upload backend files
sftp = client.open_sftp()
print("\n>>> Uploading backend files to VPS...", flush=True)
sftp.put(r"C:\Users\muham\OneDrive\Desktop\withmore\backend\app\models.py", "/var/www/withmore/backend/app/models.py")
sftp.put(r"C:\Users\muham\OneDrive\Desktop\withmore\backend\app\routers\shop.py", "/var/www/withmore/backend/app/routers/shop.py")
sftp.put(r"C:\Users\muham\OneDrive\Desktop\withmore\backend\app\routers\admin_crm.py", "/var/www/withmore/backend/app/routers/admin_crm.py")
print("Backend files uploaded!", flush=True)

# 5. Pack and upload frontend/dist
print("\n>>> Packing and uploading frontend/dist bundle...", flush=True)
tar_path = r"C:\Users\muham\OneDrive\Desktop\withmore\dist_bundle.tar.gz"
if os.path.exists(tar_path):
    os.remove(tar_path)

with tarfile.open(tar_path, "w:gz") as tar:
    tar.add(r"C:\Users\muham\OneDrive\Desktop\withmore\frontend\dist", arcname="dist")

sftp.put(tar_path, "/var/www/withmore/dist_bundle.tar.gz")
sftp.close()
if os.path.exists(tar_path):
    os.remove(tar_path)
print("Frontend bundle uploaded!", flush=True)

# 6. Unpack dist, run db migration, and restart service
run("""cd /var/www/withmore
python3 -c \"\"\"%s\"\"\"
rm -rf frontend/dist
tar -xzf dist_bundle.tar.gz -C frontend/
rm -f dist_bundle.tar.gz
ls -la frontend/dist
""" % create_table_sql)

run("systemctl restart whitmore && systemctl status whitmore --no-pager -n 7")

client.close()
print("\n🎉 Module 1 successfully deployed to VPS!", flush=True)

