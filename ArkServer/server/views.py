from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO)

def read_output_until_line_contains(process, target_line, timeout):
    start_time = time.time()
    while True:
        if process.poll() is not None:
            break

        output_line = process.stdout.readline().strip()
        if output_line:
            logging.info(f"steamcmd output: {output_line}")
            
            if target_line in output_line:
                logging.info(f"Received target line: {target_line}")
                return True
            
        if time.time() - start_time > timeout:
            logging.warning(f"Timeout reached while waiting for '{target_line}'")
            break

    return False

def run_steamcmd():
    steamcmd_dir = 'steamcmd'
    steamcmd_path = os.path.join(steamcmd_dir, 'steamcmd.exe')

    if not os.path.exists(steamcmd_path):
        logging.error("steamcmd.exe not found")
        return Response({"output": "steamcmd.exe not found"}, status=status.HTTP_400_BAD_REQUEST)

    process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    commands = [
        ("Loading Steam API...OK", "login anonymous", 30),
        ("Waiting for user info...OK", "app_update 2430930 validate", 600),
        ("Success! App '2430930' fully installed.", "quit", 30),
    ]

    full_output = []  # To store the full output

    for target_line, cmd, timeout in commands:
        logging.info(f"Waiting for: {target_line}")

        if not read_output_until_line_contains(process, target_line, timeout):
            logging.warning(f"Failed to receive '{target_line}' before sending {cmd} command")
            return Response({"output": f"Failed to receive '{target_line}' before sending {cmd} command"}, status=status.HTTP_400_BAD_REQUEST)

        logging.info(f"Sending command: {cmd}")

        process.stdin.write(f"{cmd}\n")
        process.stdin.flush()

        # Read and log the entire output after sending the command
        cmd_output = []
        cmd_sent = False
        while True:
            output_line = process.stdout.readline().strip()
            if output_line:
                logging.info(f"steamcmd output: {output_line}")
                full_output.append(output_line)
                cmd_output.append(output_line)
                
                if target_line in output_line:
                    logging.info(f"Received target line: {target_line}")
                    cmd_sent = True

                if cmd_sent and any(cmd in output_line for cmd in ["Connecting anonymously to Steam Public...OK", "Success! App '2430930' fully installed."]):
                    logging.info(f"Full output after sending {cmd}: {' '.join(cmd_output)}")
                    break  # Exit loop once target line and command acknowledgment is received

    # Combine all output lines into a single string
    full_output_str = '\n'.join(full_output)

    # You can save the full output to a file if needed
    with open('steamcmd_output.txt', 'w') as f:
        f.write(full_output_str)

    return Response({"output": "steamcmd commands completed"})





class StartArkServer(APIView):
    def post(self, request, *args, **kwargs):
        result = run_steamcmd()
        logging.info(result)
        return result

