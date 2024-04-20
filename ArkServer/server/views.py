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
            ("Loading Steam API...OK", "login anonymous\n", 30),
            ("Waiting for user info...OK", "app_update 2430930 validate\n", 600),
            ("Success! App '2430930' fully installed.", "quit\n", 30),
        ]

        for target_line, cmd, timeout in commands:
            logging.info(f"Waiting for: {target_line}")
            if read_output_until_line_contains(target_line, timeout):
                logging.info(f"Sending command: {cmd.strip()}")
                
                # Write the command to stdin
            write_result = process.stdin.write(cmd)
            process.stdin.flush()

            # Log the result of writing to stdin
            logging.info(f"Write result: {write_result}")

            # Read and log the output after sending the command
            logging.info("Reading output after sending command:")
            while True:
                output_line = process.stdout.readline().strip()
                if output_line:
                    logging.info(f"Received after sending command: {output_line}")
                    if any(target in output_line for target in ["Steam>", "Connecting anonymously to Steam Public...OK", "Waiting for client config...OK", "Waiting for user info...OK"]):
                        break
                else:
                    break

        process.terminate()

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
