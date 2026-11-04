import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import os, sqlite3

for root, dirs, files in os.walk('/var/www/withmore'):
    for f in files:
        if f.endswith('.db'):
            p = os.path.join(root, f)
            try:
                conn = sqlite3.connect(p)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
                res = cur.fetchone()
                if res:
                    cur.execute("SELECT COUNT(*) FROM products")
                    cnt = cur.fetchone()[0]
                    print(f"DATABASE WITH PRODUCTS: {p} (count: {cnt})")
                conn.close()
            except Exception as e:
                pass
"""

stdin, stdout, stderr = ssh.exec_command(f'/var/www/withmore/.venv/bin/python3 -c "{remote}"')
print("DB SEARCH:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

