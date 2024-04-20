from django.shortcuts import render
from django.http import HttpResponse
import os
import subprocess
import logging
import time
import requests
import zipfile
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

logging.basicConfig(level=logging.INFO)

def download_steamcmd():
    steamcmd_dir = 'steamcmd'
    steamcmd_zip_path = os.path.join(steamcmd_dir, 'steamcmd.zip')
    
    if not os.path.exists(steamcmd_dir):
        os.makedirs(steamcmd_dir)
    
    if os.path.exists(steamcmd_zip_path):
        logging.info("steamcmd.zip already exists, skipping download.")
    else:
        url = 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip'
        response = requests.get(url)
        
        if response.status_code == 200:
            with open(steamcmd_zip_path, 'wb') as file:
                file.write(response.content)
            logging.info("steamcmd.zip downloaded successfully.")
            
            # Extract steamcmd.exe from the zip file
            with zipfile.ZipFile(steamcmd_zip_path, 'r') as zip_ref:
                zip_ref.extract('steamcmd.exe', steamcmd_dir)
            
            logging.info("steamcmd.exe extracted successfully.")
        else:
            logging.error("Failed to download steamcmd.zip.")
            return False
    
    return True

def run_steamcmd(request):
    steamcmd_dir = 'steamcmd'
    steamcmd_path = os.path.join(steamcmd_dir, 'steamcmd.exe')

    if not os.path.exists(steamcmd_path):
        logging.error("steamcmd.exe not found. Attempting to download...")
        
        if not download_steamcmd():
            return HttpResponse("Failed to download steamcmd.exe.")
    
    logging.info("steamcmd.exe found. Starting steamcmd...")
    
    process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    def read_output_until_line_contains(target_line, timeout):
        start_time = time.time()
        while True:
            if process.poll() is not None:  # Check if process is terminated
                logging.info("steamcmd process terminated")
                break
            
            output_line = process.stdout.readline().strip()
            if output_line:
                logging.info(f"steamcmd output: {output_line}")
                
                if target_line in output_line:
                    return True
                
                start_time = time.time()  # Reset timer on activity
            
            if time.time() - start_time > timeout:
                logging.warning("Timeout reached while waiting for steamcmd output")
                break
        
        return False

    commands = [
        ("login anonymous", "loading steam API...OK", 30),  # Login with 30-second timeout
        ("app_update 2430930 validate", "Waiting for user info...OK" , 1200),  # Update with 20-minute timeout
        ("quit", "Success! App '2430930' fully installed.", 1200),
        # Add more commands as needed
    ]

    # "Success! App '2430930' fully installed."

    for cmd, target_line, timeout in commands:
        logging.info(f"Sending command: {cmd}")
        process.stdin.write(f"{cmd}\n")
        process.stdin.flush()

        if not read_output_until_line_contains(target_line, timeout):
            logging.warning(f"Failed to receive expected output: {target_line}")
            return HttpResponse(f"Failed to execute command: {cmd}")

    return HttpResponse("steamcmd commands completed")


@api_view(['POST', 'OPTIONS'])
@csrf_exempt
def start_server(request):
    if request.method == 'POST':
        # Call run_steamcmd function to execute the commands
        result = run_steamcmd(request)
        logging.info(result)
        return HttpResponse(result)
    else:
        # Render your template with the button
        return render(request, 'your_template_name.html')
