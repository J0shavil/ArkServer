from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO)

class StartArkServer(APIView):

    def run_steamcmd(self):
        steamcmd_dir = 'steamcmd'  # Update with your actual path
        steamcmd_path = f"{steamcmd_dir}/steamcmd.exe"

        process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        def read_output(process, target_line, timeout=30):
            start_time = time.time()
            while True:
                line = process.stdout.readline().strip()
                if line:
                    logging.info(f"steamcmd output: {line}")
                    if target_line in line:
                        logging.info(f"Received target line: {target_line}")
                        return True
                
                if time.time() - start_time > timeout:
                    logging.warning(f"Timeout reached while waiting for '{target_line}'")
                    logging.info(f"Current output buffer: {process.stdout.read().strip()}")
                    return False

        commands = [
            ("Loading Steam API...OK", "login anonymous\n"),
            ("Waiting for user info...OK", "app_update 2430930 validate\n"),
            ("Success! App '2430930' fully installed.", "quit\n"),
        ]

        for target_line, cmd in commands:
            logging.info(f"Waiting for: {target_line}")
            if read_output(process, target_line):
                logging.info(f"Sending command: {cmd.strip()}")
                process.stdin.write(cmd)
                process.stdin.flush()

        process.terminate()

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
