import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO)

def run_steamcmd():
    steamcmd_dir = 'steamcmd'
    steamcmd_path = os.path.join(steamcmd_dir, 'steamcmd.exe')

    if not os.path.exists(steamcmd_path):
        logging.error("steamcmd.exe not found")
        return "steamcmd.exe not found"

    # Start steamcmd.exe
    process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Function to read output with timeout
    def read_output(timeout):
        start_time = time.time()
        while True:
            if process.poll() is not None:  # Check if process is terminated
                logging.info("steamcmd process terminated")
                break
            
            output_line = process.stdout.readline().strip()
            if output_line:
                logging.info(f"steamcmd output: {output_line}")
                return output_line
            
            # Check timeout
            if time.time() - start_time > timeout:
                logging.warning("Timeout reached while waiting for steamcmd output")
                break

        return None

    # Example commands and timeouts
    commands = [
        ("login anonymous", 10),  # Login with 10-second timeout
        ("app_update 2430930 validate", 600),  # Update with 10-minute timeout
        # Add more commands as needed
    ]

    for cmd, timeout in commands:
        logging.info(f"Sending command: {cmd}")
        process.stdin.write(f"{cmd}\n")
        process.stdin.flush()

        output = read_output(timeout)
        
        # Handle output or errors here
        if output:
            # Check for specific output or errors and handle accordingly
            if "loading steam API...OK" in output:
                logging.info("Logged in to steamcmd")
            elif "Success! App '2430930' fully installed." in output:
                logging.info("App fully installed")
            else:
                logging.warning("Unknown output received")

    return "steamcmd commands completed"

# Run the function
result = run_steamcmd()
logging.info(result)
