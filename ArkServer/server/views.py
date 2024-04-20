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

        process = subprocess.Popen(
            [steamcmd_path],
            cwd=steamcmd_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        def send_command(cmd, target_line):
            process.stdin.write(f"{cmd}\n")
            process.stdin.flush()

            while True:
                output = process.stdout.readline().strip()
                if output:
                    logging.info(f"steamcmd output: {output}")
                    if target_line in output:
                        logging.info(f"Received target line: {target_line}")
                        time.sleep(2)
                        break

        send_command("login anonymous", "Loading Steam API...OK")
        send_command("app_update 2430930 validate", "Success! App '2430930' fully installed.")
        send_command("quit", "")  # No specific target line after quitting

        process.terminate()

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
