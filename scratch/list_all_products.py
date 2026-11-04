import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import sqlite3

conn = sqlite3.connect('/var/www/withmore/whitmore.db')
cur = conn.cursor()
cur.execute("SELECT id, name_uz FROM products")
rows = cur.fetchall()
print('All products in DB:', rows)
conn.close()
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("PRODUCTS:\n", stdout.read().decode())
ssh.close()

