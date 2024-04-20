from django.shortcuts import render
from django.http import HttpResponse
import os
import subprocess
import logging
import time
import requests
import zipfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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
            
            with zipfile.ZipFile(steamcmd_zip_path, 'r') as zip_ref:
                zip_ref.extract('steamcmd.exe', steamcmd_dir)
            
            logging.info("steamcmd.exe extracted successfully.")
        else:
            logging.error("Failed to download steamcmd.zip.")
            return False
    
    return True

def run_steamcmd():
    steamcmd_dir = 'steamcmd'
    steamcmd_path = os.path.join(steamcmd_dir, 'steamcmd.exe')

    if not os.path.exists(steamcmd_path):
        logging.error("steamcmd.exe not found. Attempting to download...")
        
        if not download_steamcmd():
            return "Failed to download steamcmd.exe."
    
    logging.info("steamcmd.exe found. Starting steamcmd...")
    
    process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    def read_output_until_line_contains(target_line, timeout):
        start_time = time.time()
        while True:
            if process.poll() is not None:
                logging.info("steamcmd process terminated")
                break
            
            output_line = process.stdout.readline().strip()
            if output_line:
                logging.info(f"steamcmd output: {output_line}")
                
                if target_line in output_line:
                    return True
                
            if time.time() - start_time > timeout:
                logging.warning("Timeout reached while waiting for steamcmd output")
                break
        
        return False

    commands = [
        ("login anonymous", "Loading Steam API...OK", 30),
        ("app_update 2430930 validate", "Waiting for user info", 1200),
        ("quit", "Success! App '2430930' fully installed.", 30),
    ]

    for cmd, target_line, timeout in commands:
        logging.info(f"Sending command: {cmd}")
        
        if cmd == "login anonymous":
            if not read_output_until_line_contains(target_line, 30):
                logging.warning(f"Failed to receive '{target_line}' output before sending {cmd} command")
                return f"Failed to execute {cmd} command: {target_line} not received"
            
        process.stdin.write(f"{cmd}\n")
        process.stdin.flush()

        if cmd != "login anonymous":
            if not read_output_until_line_contains(target_line, timeout):
                logging.warning(f"Failed to receive expected output: {target_line}")
                return f"Failed to execute command: {cmd}"

        time.sleep(2)  # Add a small delay before sending the next command

    # Additional logging to print the final output of steamcmd
    final_output = process.stdout.read().strip()
    logging.info(f"Final output from steamcmd: {final_output}")

    # Check the exit status of steamcmd
    exit_status = process.wait()
    logging.info(f"steamcmd process exit status: {exit_status}")

    return "steamcmd commands completed"







class StartArkServer(APIView):
    
    def post(self, request, *args, **kwargs):
        result = run_steamcmd()
        
        if "Failed" in result:
            return Response({"output": result}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"output": result}, status=status.HTTP_200_OK)
