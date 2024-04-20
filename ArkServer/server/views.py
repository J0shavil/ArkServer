import subprocess
import logging
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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
            text=True
        )

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
            ("Loading Steam API...OK", "login anonymous"),
            ("Waiting for user info...OK", "app_update 2430930 validate"),
            ("Success! App '2430930' fully installed.", "quit"),
        ]

        for target_line, cmd in commands:
            logging.info(f"Waiting for: {target_line}")
            if read_output_until_line_contains(target_line):
                logging.info(f"Sending command: {cmd}")
                process.stdin.write(f"{cmd}\n")
                process.stdin.flush()  # Explicitly flush stdin
                time.sleep(2)  # Sleep for 2 seconds to allow time for command processing
            else:
                logging.warning(f"Failed to receive '{target_line}' output before sending {cmd} command")
                break

        process.terminate()

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
