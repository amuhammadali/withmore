import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import sqlite3

conn = sqlite3.connect('/var/www/withmore/whitmore.db')
cur = conn.cursor()
cur.execute("SELECT id, name_uz FROM products WHERE name_uz LIKE '%lion%' OR name_uz LIKE '%koylek%'")
rows = cur.fetchall()
print('Products found:', rows)
for pid, name in rows:
    cur.execute("SELECT path FROM product_images WHERE product_id = ?", (pid,))
    imgs = cur.fetchall()
    print(f'Product {pid} ({name}): images = {imgs}')
conn.close()
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("DB CHECK:\n", stdout.read().decode())
ssh.close()

