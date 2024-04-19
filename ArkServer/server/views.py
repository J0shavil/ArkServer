from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import os
import subprocess
import time


# Create your views here.


def index(request):
    pass



def download_steamcmd():
    steamcmd_dir = 'steamcmd'
    steamcmd_path = os.path.join(steamcmd_dir, 'steamcmd.exe')


    # chech if steamcmd was already downloaded
    if os.path.exists(steamcmd_path):
        print("SteamCMD already exists.")
        return
    
    url = 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip'
    response = requests.get(url)


    os.makedirs(steamcmd_dir, exist_ok=True)


    zip_path = os.path.join(steamcmd_dir, 'steamcmd.zip')
    with open(zip_path, 'wb') as file:
        file.write(response.content)

    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(steamcmd_dir)

    
    os.remove(zip_path)


def run_steamcmd():
    steamcmd_dir = 'steamcmd'
    steamcmd_path = os.path.join(steamcmd_dir, 'steamcmd.exe')
    
    # Check if SteamCMD exists
    if not os.path.exists(steamcmd_path):
        print("SteamCMD does not exist. Downloading...")
        download_steamcmd()
    
    # Start SteamCMD
    process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Set up select for a timeout
    poll_obj = select.poll()
    poll_obj.register(process.stdout, select.POLLIN)
    
    timeout_seconds = 60  # Timeout after 60 seconds of no activity
    end_time = time.time() + timeout_seconds
    
    installation_complete = False
    
    while True:
        if poll_obj.poll(0):  # Check if there's data to read
            line = process.stdout.readline().strip()
            print(line)
            
            # Check for specific patterns or lines
            if "loading steam API...OK" in line:
                process.stdin.write('login anonymous\n')
                process.stdin.flush()
                
            elif "Enter password:" in line:
                process.stdin.write('password_here\n')
                process.stdin.flush()
                
            elif "Success! App '2430930' fully installed." in line:
                print("Installation complete!")
                installation_complete = True
                
        elif time.time() > end_time:
            print("Timeout: No activity for {} seconds.".format(timeout_seconds))
            break
        
        if installation_complete or process.poll() is not None:
            break
    
    # Read remaining output
    remaining_output = process.communicate()[0]
    print(remaining_output)
    
    if installation_complete:
        # Execute additional commands or actions after installation
        print("Performing additional actions after installation...")
        # Add your additional commands or actions here

