import paramiko, sys, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.248.77', username='hibug', password='mug2025', timeout=10)

chan = client.get_transport().open_session()
chan.exec_command(
    'rm -rf /home/hibug/FORGE-Bench && '
    'git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 '
    'clone --depth=1 https://github.com/am-ns/FORGE-Bench.git /home/hibug/FORGE-Bench 2>&1 && '
    'echo CLONE_OK && ls /home/hibug/FORGE-Bench/'
)
chan.settimeout(300)

print("Cloning...")
while True:
    try:
        if chan.recv_ready():
            d = chan.recv(4096).decode('utf-8', errors='replace')
            sys.stdout.buffer.write(d.encode('gbk', errors='replace'))
            sys.stdout.flush()
        if chan.exit_status_ready():
            time.sleep(0.3)
            while chan.recv_ready():
                d = chan.recv(4096).decode('utf-8', errors='replace')
                sys.stdout.buffer.write(d.encode('gbk', errors='replace'))
                sys.stdout.flush()
            break
        time.sleep(0.05)
    except Exception:
        time.sleep(1)

code = chan.recv_exit_status()
print(f"\nexit={code}")
client.close()
