import subprocess
import logging
import time

def start_server(request):
    # Define the directory and path for steamcmd
    print("START")
    steamcmd_dir = 'steamcmd'
    steamcmd_path = os.path.join(steamcmd_dir, 'steamcmd.exe')

    if not os.path.exists(steamcmd_path):
        logging.error("steamcmd.exe not found")
        return "steamcmd.exe not found"

    # Start steamcmd.exe
    process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    installation_complete = False
    
    for line in iter(process.stdout.readline, ''):
        # Check for specific patterns or lines
        if "Loading Steam API...OK" in line:
            process.stdin.write('login anonymous\n')
            process.stdin.flush()
            
        elif "Enter password:" in line:
            process.stdin.write('password_here\n')
            process.stdin.flush()
            
        elif "Success! App '2430930' fully installed." in line:
            print("installed")
            installation_complete = True
    
    # Read remaining output
    remaining_output = process.communicate()[0]
    
    output = remaining_output.decode('utf-8')
    
    if installation_complete:
        output += "\nInstallation complete!"
    
    return JsonResponse({'output': output})

def test(request):
    print("TEST")
    return JsonResponse({'output': 'TEST'})