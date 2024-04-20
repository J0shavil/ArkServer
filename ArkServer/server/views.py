from django.http import JsonResponse
from rest_framework.views import APIView
import subprocess
import os
import logging
import time

logging.basicConfig(level=logging.INFO)

class StartArkServer(APIView):

    def run_steamcmd(self):
        steamcmd_dir = 'steamcmd'
        steamcmd_path = os.path.join(steamcmd_dir, 'steamcmd.exe')

        if not os.path.exists(steamcmd_path):
            logging.error("steamcmd.exe not found")
            return "steamcmd.exe not found"

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
                        logging.info(f"Received target line: {target_line}")
                        return True

                if time.time() - start_time > timeout:
                    logging.warning("Timeout reached while waiting for steamcmd output")
                    break

            return False

        commands = [
            ("Loading Steam API...OK", "login anonymous", 30),
            ("Waiting for user info...OK", "app_update 2430930 validate", 600),
            ("Success! App '2430930' fully installed.", "quit", 30),
        ]

        for target_line, cmd, timeout in commands:
            logging.info(f"Waiting for: {target_line}")

            if not read_output_until_line_contains(target_line, timeout):
                logging.warning(f"Failed to receive '{target_line}' output before sending {cmd} command")
                return f"Failed to execute {cmd} command: {target_line} not received"

            # Introduce a slight delay before sending the command
            time.sleep(1)

            logging.info(f"Sending command: {cmd}")
            process.stdin.write(f"{cmd}\n")
            process.stdin.flush()

            if cmd == "quit":
                break

        process.communicate()  # Wait for the process to finish

        return "steamcmd commands completed"

    def post(self, request, *args, **kwargs):
        result = self.run_steamcmd()
        logging.info(result)
        return JsonResponse({"output": result})
