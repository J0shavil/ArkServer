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
        ("login anonymous", "Loading Steam API...OK", 30),
        ("app_update 2430930 validate", "Success! App '2430930' fully installed.", 600),
        ("quit", "logout", 30),
    ]

    for cmd, target_line, timeout in commands:
        logging.info(f"Sending command: {cmd}")
        
        if cmd == "login anonymous":
            if not read_output_until_line_contains(process, target_line, timeout):
                logging.warning(f"Failed to receive '{target_line}' output before sending {cmd} command")
                logging.info(f"Current output buffer: {process.stdout.read().strip()}")
                return Response({"output": f"Failed to execute {cmd} command: {target_line} not received"}, status=status.HTTP_400_BAD_REQUEST)
        
        process.stdin.write(f"{cmd}\n")
        process.stdin.flush()

        if not read_output_until_line_contains(process, target_line, timeout):
            logging.warning(f"Failed to receive '{target_line}' output before sending {cmd} command")
            logging.info(f"Current output buffer: {process.stdout.read().strip()}")
            return Response({"output": f"Failed to execute {cmd} command: {target_line} not received"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"output": "steamcmd commands completed"})

class StartArkServer(APIView):
    def post(self, request, *args, **kwargs):
        result = run_steamcmd()
        logging.info(result)
        return result
