import paramiko, sys, time

# Replace TASK-5 with an improved version that uses Claude's vision to judge images
NEW_TASK5 = """[TASK-5: IMAGE QUALITY REDO WITH VISUAL INSPECTION] Working directory: /home/hibug/FORGE-Bench. Replace all 22 current images with high-quality, visually verified photographs. You have vision capabilities - USE THEM to inspect every candidate image before accepting it. WORKFLOW for each of the 22 images in dataset/annotations/samples.json: (1) Read the sample's 'text' prompt and 'domain' to understand exactly what the image must show. (2) Search Wikimedia Commons (proxy already set): curl 'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=QUERY&srnamespace=6&srlimit=8&format=json' - use specific queries listed below. (3) For each search result, get the image URL: curl 'https://commons.wikimedia.org/w/api.php?action=query&titles=File:FILENAME&prop=imageinfo&iiprop=url&iiurlwidth=1920&format=json'. (4) Download to a temp path: /tmp/candidate.jpg. (5) VISUALLY INSPECT the downloaded image by reading it - check: (a) Does it clearly show the correct industrial subject described in the prompt? (b) Is the subject the main focus and clearly visible (not tiny or partially obscured)? (c) Is the image sharp and in focus (not blurry, not motion-blurred)? (d) Does the background roughly match the prompt description? (e) Are there no watermarks, text overlays, logos, or heavy post-processing artifacts? (f) Is the viewing angle appropriate for the orbit/pan/tilt motion described? For orbit prompts the subject should be visible from the side or 3/4 view. For pan prompts the subject should fill the frame horizontally. (6) If the image PASSES visual inspection AND resolution >=1280x1080: copy to the correct dataset/images/{domain}/filename.jpg path. If it FAILS: try the next search result, or try Unsplash fallback: curl 'https://source.unsplash.com/1920x1080/?KEYWORD' -L -o /tmp/candidate.jpg then visually inspect again. (7) After replacing an image, note in a log file /home/hibug/lobster/image_audit.log: 'ACCEPTED: filename | source: URL | reason: why it passes'. SPECIFIC SEARCH QUERIES: aerospace/boeing_747_400.jpg -> 'Boeing 747-400 aircraft side flight blue sky'; aerospace/airbus_a380.jpg -> 'Airbus A380 aircraft takeoff landing'; aerospace/boeing_chinook.jpg -> 'CH-47 Chinook helicopter transport flight'; aerospace/gulfstream_g650.jpg -> 'Gulfstream business jet aircraft side'; aerospace/space_shuttle.jpg -> 'Space Shuttle Discovery launch NASA'; energy/wind_turbine.jpg -> 'offshore wind turbine sea ocean'; energy/offshore_oil_platform.jpg -> 'offshore oil platform North Sea jacket'; energy/solar_farm.jpg -> 'solar farm photovoltaic panel field'; manufacturing/cnc_machine.jpg -> 'CNC machine tool milling lathe industrial'; manufacturing/assembly_line.jpg -> 'automobile assembly line robot factory'; manufacturing/3d_printer.jpg -> 'industrial FDM 3D printer manufacturing'; microelectronics/pcb_circuit_board.jpg -> 'printed circuit board PCB green macro components resistors'; microelectronics/semiconductor_wafer.jpg -> 'silicon wafer semiconductor fab cleanroom'; microelectronics/chip_packaging.jpg -> 'integrated circuit chip BGA package closeup'; robotics/industrial_robot_arm.jpg -> 'industrial robot arm FANUC KUKA factory'; robotics/collaborative_robot.jpg -> 'collaborative robot cobot Universal Robots'; robotics/autonomous_mobile_robot.jpg -> 'autonomous mobile robot AGV warehouse'; vehicles/cargo_ship.jpg -> 'container ship cargo vessel ocean port'; vehicles/mining_truck.jpg -> 'Caterpillar haul truck open pit mine'; vehicles/excavator.jpg -> 'excavator construction earthmoving hydraulic'; vehicles/construction_crane.jpg -> 'tower crane construction site building'; vehicles/heavy_haul_truck.jpg -> 'heavy haul truck semi highway'. After all 22 images replaced and visually verified, run sharpness check: python3 -c "import cv2,glob,numpy as np; [print(f.split('/')[-1], cv2.imread(f).shape[:2], 'sharp' if cv2.Laplacian(cv2.cvtColor(cv2.imread(f),cv2.COLOR_BGR2GRAY),cv2.CV_64F).var()>100 else 'BLURRY') for f in sorted(glob.glob('dataset/images/**/*.jpg',recursive=True))]". Reject and re-download any image marked BLURRY. Commit: git -c http.proxy=http://127.0.0.1:7897 add dataset/images/ && git -c http.proxy=http://127.0.0.1:7897 commit -m 'dataset: all 22 images replaced with visually inspected high-quality photographs'.
"""

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

# Read current todo, replace TASK-5 line
sftp = client.open_sftp()
with sftp.open('/home/hibug/lobster/todo.md', 'r') as f:
    content = f.read().decode('utf-8')

lines = content.split('\n')
new_lines = []
for line in lines:
    if line.startswith('[TASK-5:'):
        new_lines.append(NEW_TASK5.strip())
    else:
        new_lines.append(line)

with sftp.open('/home/hibug/lobster/todo.md', 'w') as f:
    f.write('\n'.join(new_lines))
sftp.close()

print("TASK-5 updated with visual inspection instructions.")
stream(client, "grep '^\\[TASK' /home/hibug/lobster/todo.md | cut -c1-70")
client.close()
