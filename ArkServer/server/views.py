import requests
import os
import zipfile
import subprocess
from django.http import JsonResponse

def start_ark_server_view(request):
    # Define the directory and path for steamcmd
    steamcmd_dir = 'steamcmd'
    steamcmd_path = os.path.join(steamcmd_dir, 'steamcmd.exe')
    
    # Check if SteamCMD exists, if not download it
    if not os.path.exists(steamcmd_path):
        # Download SteamCMD
        url = 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip'
        response = requests.get(url)
        
        # Create the steamcmd directory if it doesn't exist
        os.makedirs(steamcmd_dir, exist_ok=True)
        
        # Save the downloaded zip file
        zip_path = os.path.join(steamcmd_dir, 'steamcmd.zip')
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(steamcmd_dir)
        
        # Remove the zip file
        os.remove(zip_path)
    
    # Run SteamCMD
    process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    installation_complete = False
    
    for line in iter(process.stdout.readline, ''):
        # Check for specific patterns or lines
        if "loading steam API...OK" in line:
            process.stdin.write('login anonymous\n')
            process.stdin.flush()
            
        elif "Enter password:" in line:
            process.stdin.write('password_here\n')
            process.stdin.flush()
            
        elif "Success! App '2430930' fully installed." in line:
            installation_complete = True
    
    # Read remaining output
    remaining_output = process.communicate()[0]
    
    output = remaining_output.decode('utf-8')
    
    if installation_complete:
        output += "\nInstallation complete!"
    
    return JsonResponse({'output': output})
