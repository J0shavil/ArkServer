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

        def read_all_output(timeout=30):
            start_time = time.time()
            while True:
                if process.poll() is not None:
                    logging.info("steamcmd process terminated")
                    break
                
                output_line = process.stdout.readline().strip()
                if output_line:
                    logging.info(f"steamcmd output: {output_line}")
                
                if time.time() - start_time > timeout:
                    logging.warning("Timeout reached while waiting for output")
                    break

        commands = [
            "login anonymous",
            "app_update 2430930 validate",
            "quit"
        ]

        for cmd in commands:
            logging.info(f"Sending command: {cmd}")
            process.stdin.write(f"{cmd}\n")
            process.stdin.flush()
            read_all_output()

        process.terminate()

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
