import os
import urllib.request
import shutil

os.makedirs("src/sounds", exist_ok=True)

base_url = "https://raw.githubusercontent.com/Calinou/kenney-interface-sounds/master/addons/kenney_interface_sounds/"
sounds = {
    "work_to_break.wav": "confirmation_001.wav",
    "break_to_work.wav": "drop_001.wav",
    "work_to_long_break.wav": "maximize_001.wav",
    "long_break_to_work.wav": "bong_001.wav"
}

for local_name, remote_name in sounds.items():
    url = base_url + remote_name
    print(f"Downloading {url} to src/sounds/{local_name}...")
    urllib.request.urlretrieve(url, f"src/sounds/{local_name}")

if os.path.exists("main.py"):
    shutil.move("main.py", "src/main.py")

print("Setup complete.")
