import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

remote = """
import sqlite3

for p in ['/var/www/withmore/data/whitmore.db', '/var/www/withmore/backend/shop.db', '/var/www/withmore/whitmore.db']:
    try:
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute('SELECT product_id, path FROM product_images LIMIT 5')
        print(p, 'product_images:', cur.fetchall())
        conn.close()
    except Exception as e:
        print(p, 'err:', e)
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{remote}"')
print("DB CHECK:\n", stdout.read().decode())
ssh.close()

