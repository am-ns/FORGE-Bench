import paramiko, sys, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.248.77', username='hibug', password='mug2025', timeout=10)

cmd = '''
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897
rm -rf ~/FORGE-Bench
cd ~
GIT_TERMINAL_PROMPT=0 git clone --depth=1 --progress https://github.com/am-ns/FORGE-Bench.git 2>&1
echo "---CLONE_EXIT:$?---"
ls ~/FORGE-Bench/ 2>/dev/null
'''

chan = client.get_transport().open_session()
chan.exec_command(cmd)
chan.settimeout(300)

print("克隆中（浅克隆，只拉最新一次提交）...")
last_output = time.time()
while True:
    try:
        if chan.recv_ready():
            data = chan.recv(4096).decode('utf-8', errors='replace')
            sys.stdout.buffer.write(data.encode('gbk', errors='replace'))
            sys.stdout.flush()
            last_output = time.time()
        if chan.recv_stderr_ready():
            data = chan.recv_stderr(4096).decode('utf-8', errors='replace')
            sys.stdout.buffer.write(data.encode('gbk', errors='replace'))
            sys.stdout.flush()
            last_output = time.time()
        if chan.exit_status_ready():
            time.sleep(0.5)
            while chan.recv_ready():
                data = chan.recv(4096).decode('utf-8', errors='replace')
                sys.stdout.buffer.write(data.encode('gbk', errors='replace'))
                sys.stdout.flush()
            break
        if time.time() - last_output > 60:
            print("\n[超过60秒无输出，可能在传输大文件，继续等待...]")
            last_output = time.time()
        time.sleep(0.1)
    except Exception as e:
        print(f"\n[读取超时，继续等待: {e}]")
        time.sleep(2)

exit_code = chan.recv_exit_status()
print(f"\n退出码: {exit_code}")
client.close()
