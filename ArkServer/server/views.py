from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import subprocess
import logging
import os
import time

logging.basicConfig(level=logging.INFO)

class StartArkServer(APIView):

    def run_steamcmd(self):
        steamcmd_dir = 'steamcmd'
        steamcmd_path = os.path.join(steamcmd_dir, 'steamcmd.exe')

        if not os.path.exists(steamcmd_path):
            logging.error("steamcmd.exe not found")
            return "steamcmd.exe not found"

        commands = [
            ("login anonymous", "Connecting anonymously to Steam Public...OK", 30),
            ("app_update 2430930 validate", "Waiting for user info...OK", 600),
            ("quit", "Success! App '2430930' fully installed.", 30),
        ]

        process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        def send_command(cmd, target_line, timeout):
            logging.info(f"Sending command: {cmd}")
            process.stdin.write(f"{cmd}\n")
            process.stdin.flush()
            
            start_time = time.time()
            while True:
                output_line = process.stdout.readline().strip()
                if output_line:
                    logging.info(f"steamcmd output: {output_line}")
                    if target_line in output_line:
                        logging.info(f"Received target line: {target_line}")
                        break
                
                if time.time() - start_time > timeout:
                    logging.warning(f"Timeout reached while waiting for {target_line}")
                    break

        for cmd, target_line, timeout in commands:
            send_command(cmd, target_line, timeout)

        stdout, stderr = process.communicate()
        logging.info(f"stdout: {stdout}")
        logging.info(f"stderr: {stderr}")

        return "steamcmd commands completed"

    def post(self, request, format=None):
        result = self.run_steamcmd()
        logging.info(result)
        return Response({"result": result}, status=status.HTTP_200_OK)
