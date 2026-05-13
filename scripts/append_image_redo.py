import paramiko, sys, time

# Append the improved image re-sourcing task to existing todo.md
TASK_IMAGE_REDO = """
[TASK-5: IMAGE QUALITY REDO] Working directory: /home/hibug/FORGE-Bench. The current images from LoremFlickr have unacceptable quality and content accuracy. Replace ALL 22 images with high-quality, content-accurate photographs. Requirements for every image: (A) Resolution: minimum 1920x1080 pixels; (B) Sharpness: compute PIL Laplacian variance via: import cv2,numpy as np; img=cv2.imread(p); gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY); var=cv2.Laplacian(gray,cv2.CV_64F).var(); reject if var<100 (blurry); (C) Content: must clearly and unambiguously show the specified industrial subject from a clear viewing angle; (D) Background: must match the prompt description in samples.json; (E) No watermarks, no text overlays, no heavy vignetting; (F) Real photograph (not CGI, not illustration, not diagram). SOURCE STRATEGY - use Wikimedia Commons with proxy (http_proxy=http://127.0.0.1:7897 already set in environment): Step 1 - Search API: curl 'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=QUERY&srnamespace=6&srlimit=8&format=json' for each subject. Step 2 - Get download URL: curl 'https://commons.wikimedia.org/w/api.php?action=query&titles=File:FILENAME&prop=imageinfo&iiprop=url&iiurlwidth=1920&format=json'. Step 3 - Download image. If Wikimedia Commons fails for a specific subject, try: curl 'https://source.unsplash.com/1920x1080/?KEYWORD' -L -o output.jpg (Unsplash random, higher quality than LoremFlickr). SPECIFIC SEARCH QUERIES per image (use these exact terms on Wikimedia Commons first): aerospace/boeing_747_400.jpg -> search 'Boeing 747-400 aircraft side view flight'; aerospace/airbus_a380.jpg -> search 'Airbus A380 aircraft landing side'; aerospace/boeing_chinook.jpg -> search 'CH-47 Chinook helicopter military transport'; aerospace/gulfstream_g650.jpg -> search 'Gulfstream G650 business jet aircraft'; aerospace/space_shuttle.jpg -> search 'Space Shuttle launch NASA'; energy/wind_turbine.jpg -> search 'offshore wind turbine sea'; energy/offshore_oil_platform.jpg -> search 'North Sea oil platform offshore'; energy/solar_farm.jpg -> search 'solar farm photovoltaic panels aerial'; manufacturing/cnc_machine.jpg -> search 'CNC milling machine industrial metalworking'; manufacturing/assembly_line.jpg -> search 'automotive assembly line robots factory'; manufacturing/3d_printer.jpg -> search 'industrial 3D printer FDM manufacturing'; microelectronics/pcb_circuit_board.jpg -> search 'printed circuit board PCB green macro closeup components'; microelectronics/semiconductor_wafer.jpg -> search 'silicon semiconductor wafer chip fabrication'; microelectronics/chip_packaging.jpg -> search 'integrated circuit chip package close-up'; robotics/industrial_robot_arm.jpg -> search 'FANUC industrial robot arm manufacturing'; robotics/collaborative_robot.jpg -> search 'collaborative robot cobot human interaction'; robotics/autonomous_mobile_robot.jpg -> search 'autonomous mobile robot warehouse logistics'; vehicles/cargo_ship.jpg -> search 'container cargo ship ocean port'; vehicles/mining_truck.jpg -> search 'Caterpillar 797 mining haul truck'; vehicles/excavator.jpg -> search 'Caterpillar excavator construction site'; vehicles/construction_crane.jpg -> search 'tower crane construction site'; vehicles/heavy_haul_truck.jpg -> search 'heavy haul truck highway transport'. For each image: download candidate, check resolution >=1920x1080 (if not, try different result or use -iiurlwidth=3840 for larger), check sharpness var>=100, check it shows the correct subject visually. If a Wikimedia image passes all checks, save it. If not, fall back to Unsplash URL with specific keywords. After replacing all images, run: python3 -c "import cv2,glob,numpy as np; imgs=glob.glob('dataset/images/**/*.jpg',recursive=True); [print(f.split('/')[-1], cv2.imread(f).shape, round(cv2.Laplacian(cv2.cvtColor(cv2.imread(f),cv2.COLOR_BGR2GRAY),cv2.CV_64F).var(),1)) for f in sorted(imgs)]" to print sharpness report. Commit: git -c http.proxy=http://127.0.0.1:7897 add dataset/images/ && git -c http.proxy=http://127.0.0.1:7897 commit -m 'dataset: replace all images with high-res sharp Wikimedia/Unsplash photographs (>=1920x1080, Laplacian>100)'.
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

# Append TASK-5 to existing todo.md
sftp = client.open_sftp()
with sftp.open('/home/hibug/lobster/todo.md', 'a') as f:
    f.write(TASK_IMAGE_REDO)
sftp.close()

# Verify todo now has tasks
stream(client, "grep -c '^\\[TASK' /home/hibug/lobster/todo.md && echo '---' && grep '^\\[TASK' /home/hibug/lobster/todo.md | cut -c1-60")
client.close()
