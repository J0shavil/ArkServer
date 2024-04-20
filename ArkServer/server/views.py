from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import subprocess
import threading
import time
import logging

logging.basicConfig(level=logging.INFO)

class StartArkServer(APIView):

    def run_steamcmd(self):
        steamcmd_dir = 'steamcmd'  # Update with your actual path
        steamcmd_path = f"{steamcmd_dir}/steamcmd.exe"

        process = subprocess.Popen(
            [steamcmd_path], 
            cwd=steamcmd_dir, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            bufsize=1  # Line buffered
        )

        def read_output():
            for line in iter(process.stdout.readline, ''):
                logging.info(f"steamcmd output: {line.strip()}")
                if any(target in line for target in ["Steam>", "Connecting anonymously to Steam Public...OK", "Waiting for client config...OK", "Waiting for user info...OK"]):
                    return True
            return False

        commands = [
            ("Loading Steam API...OK", "login anonymous\n", 30),
            ("Waiting for user info...OK", "app_update 2430930 validate\n", 600),
            ("Success! App '2430930' fully installed.", "quit\n", 30),
        ]

        for target_line, cmd, timeout in commands:
            logging.info(f"Waiting for: {target_line}")

            if not read_output():
                logging.warning("No response received after sending command")
                break

            logging.info(f"Sending command: {cmd.strip()}")
            process.stdin.write(cmd)
            process.stdin.flush()

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
