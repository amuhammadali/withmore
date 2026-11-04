import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('162.35.37.77', port=22, username='root', password='withmore2026')

stdin, stdout, stderr = ssh.exec_command("python3 -c 'import gradio_client; print(gradio_client.__version__)'")
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print("gradio_client:", out or err)

if "No module" in err:
    print("Installing gradio_client...")
    stdin, stdout, stderr = ssh.exec_command("pip install --no-cache-dir gradio_client")
    print("pip out:", stdout.read().decode().strip())

ssh.close()

