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

try:
    client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=15)
    print("✅ SSH Connection Successful!", flush=True)
except Exception as e:
    print(f"❌ Connection failed: {e}", flush=True)
    sys.exit(1)

def run(cmd, timeout=300):
    print(f"\n>>> Running: {cmd}", flush=True)
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    # Stream output
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
    print(f"Exit code: {status}", flush=True)
    return status

# 1. OS Info
run("cat /etc/os-release | grep PRETTY_NAME")

# 2. Update and install packages
run("apt-get update -y -q && apt-get install -y -q git curl python3 python3-pip python3-venv debian-keyring debian-archive-keyring apt-transport-https tar")

# 3. Install Caddy
run("""if ! command -v caddy &> /dev/null; then
    curl -1sLF 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg --yes
    curl -1sLF 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
    apt-get update -y -q && apt-get install -y -q caddy
fi""")

# 4. Clone or pull repo
run("""mkdir -p /var/www
if [ -d "/var/www/withmore/.git" ]; then
    cd /var/www/withmore && git pull origin main
else
    rm -rf /var/www/withmore
    git clone https://github.com/amuhammadali/withmore.git /var/www/withmore
fi""")

# 5. Pack and upload frontend/dist via SFTP
print("\n>>> Packing and uploading frontend/dist...", flush=True)
tar_path = "dist_bundle.tar.gz"
with tarfile.open(tar_path, "w:gz") as tar:
    tar.add("frontend/dist", arcname="dist")

sftp = client.open_sftp()
sftp.put(tar_path, "/var/www/withmore/dist_bundle.tar.gz")
sftp.close()
if os.path.exists(tar_path):
    os.remove(tar_path)

run("""cd /var/www/withmore
rm -rf frontend/dist
tar -xzf dist_bundle.tar.gz -C frontend/
rm -f dist_bundle.tar.gz
ls -la frontend/dist
""")

# 6. Setup .env
env_text = """MODE=production
APP_URL=https://withmore.uz
BOT_TOKEN=9132535201:AAGjmjl_LuGAEg6hmlzbvB6Acw0o0mSZdmY
ADMIN_PASSWORD=Owner-Pass-12345
OWNER_LOGIN=owner
SESSION_SECRET=withmore-production-secret-key-2026-sartorial-crm
DATABASE_URL=sqlite:///./whitmore.db
FRONTEND_DIST=frontend/dist
UPLOAD_DIR=uploads
"""
run(f'cat << "EOF" > /var/www/withmore/.env\n{env_text}\nEOF')

# 7. Python venv & requirements
run("""cd /var/www/withmore
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -q -r backend/requirements.txt
export PYTHONPATH=backend
.venv/bin/python3 -m app.manage init
""")

# 8. Systemd service
service_text = """[Unit]
Description=Whitmore E-Commerce & CRM Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/withmore
ExecStart=/var/www/withmore/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3
Environment="PYTHONPATH=backend"

[Install]
WantedBy=multi-user.target
"""
run(f'cat << "EOF" > /etc/systemd/system/whitmore.service\n{service_text}\nEOF')
run("systemctl daemon-reload && systemctl enable whitmore && systemctl restart whitmore")

# 9. Caddy configuration (Both direct IP and domain withmore.uz)
caddy_text = """:80 {
    encode gzip zstd
    reverse_proxy 127.0.0.1:8000
}

withmore.uz, www.withmore.uz {
    encode gzip zstd
    reverse_proxy 127.0.0.1:8000
}
"""
run(f'cat << "EOF" > /etc/caddy/Caddyfile\n{caddy_text}\nEOF')
run("systemctl reload caddy || systemctl restart caddy")

# 10. Status check
time.sleep(2)
run("systemctl status whitmore --no-pager | head -n 15")
run("curl -s http://127.0.0.1:8000/api/health")

print("\n🎉 Deployment completed successfully!", flush=True)
client.close()
