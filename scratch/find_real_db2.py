import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote_code = """
import os, sqlite3

for root, dirs, files in os.walk('/var/www/withmore'):
    for f in files:
        if f.endswith('.db'):
            p = os.path.join(root, f)
            try:
                conn = sqlite3.connect(p)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM products")
                print("FOUND DB:", p, "count:", cur.fetchone()[0])
                conn.close()
            except Exception:
                pass
"""

sftp = ssh.open_sftp()
with sftp.file('/tmp/find_db.py', 'w') as f:
    f.write(remote_code)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('/var/www/withmore/.venv/bin/python3 /tmp/find_db.py')
print("OUT:\n", stdout.read().decode())
print("ERR:\n", stderr.read().decode())
ssh.close()

