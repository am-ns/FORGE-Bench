import paramiko, sys, time

REMOVE_TASK_PY = '''\
import sys
if len(sys.argv) < 2:
    sys.exit(0)
task = sys.argv[1]
todo_path = "/home/hibug/lobster/todo.md"
lines = open(todo_path).readlines()
new_lines = [l for l in lines if l.rstrip("\\n") != task]
open(todo_path, "w").writelines(new_lines)
'''

def stream(client, cmd, timeout=30):
    chan = client.get_transport().open_session()
    chan.exec_command(cmd)
    chan.settimeout(timeout)
    while True:
        if chan.recv_ready():
            d = chan.recv(4096).decode("utf-8", errors="replace")
            sys.stdout.buffer.write(d.encode("gbk", errors="replace"))
            sys.stdout.flush()
        if chan.exit_status_ready():
            time.sleep(0.2)
            while chan.recv_ready():
                d = chan.recv(4096).decode("utf-8", errors="replace")
                sys.stdout.buffer.write(d.encode("gbk", errors="replace"))
                sys.stdout.flush()
            break
        time.sleep(0.05)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.248.77', username='hibug', password='mug2025', timeout=10)

sftp = client.open_sftp()
with sftp.open('/home/hibug/lobster/remove_task.py', 'w') as f:
    f.write(REMOVE_TASK_PY)
sftp.close()
print("remove_task.py uploaded")
stream(client, "python3 /home/hibug/lobster/remove_task.py --test 2>/dev/null; echo ok")
client.close()
