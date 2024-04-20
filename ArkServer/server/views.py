from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO)

class StartArkServer(APIView):

    def run_steamcmd(self):
        steamcmd_dir = 'steamcmd'  # Update with your actual path
        steamcmd_path = f"{steamcmd_dir}/steamcmd.exe"

        process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        def read_output_until_line_contains(target_line, timeout=30):
            start_time = time.time()
            while True:
                if process.poll() is not None:
                    logging.info("steamcmd process terminated")
                    break
                
                output_line = process.stdout.readline().strip()
                if output_line:
                    logging.info(f"steamcmd output: {output_line}")
                    if target_line in output_line:
                        logging.info(f"Received target line: {target_line}")
                        return True
                
                if time.time() - start_time > timeout:
                    logging.warning(f"Timeout reached while waiting for '{target_line}'")
                    logging.info(f"Current output buffer: {process.stdout.read().strip()}")
                    return False

            return False

        commands = [
            ("Loading Steam API...OK", "login anonymous", 30),
            ("Waiting for user info...OK", "app_update 2430930 validate", 600),
            ("Success! App '2430930' fully installed.", "quit", 30),
        ]

        for target_line, cmd, timeout in commands:
            logging.info(f"Waiting for: {target_line}")
            if read_output_until_line_contains(target_line, timeout):
                logging.info(f"Sending command: {cmd.strip()}")
                process.stdin.write(f"quit\n")
                process.stdin.flush()
                
                # Add a delay after sending "login anonymous"
                if cmd == "login anonymous":
                    time.sleep(5)  # Wait for 5 seconds

            else:
                logging.warning(f"Failed to receive '{target_line}' output before sending {cmd.strip()} command")
                break

        process.terminate()

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
