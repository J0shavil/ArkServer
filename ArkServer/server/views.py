from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

class StartArkServer(APIView):

    def run_steamcmd(self):
        steamcmd_dir = 'steamcmd'  # Update with your actual path
        steamcmd_path = f"{steamcmd_dir}/steamcmd.exe"

        process = subprocess.Popen([steamcmd_path], cwd=steamcmd_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        def read_output(process):
            output = []
            while True:
                line = process.stdout.readline().strip()
                if line:
                    logging.info(f"steamcmd output: {line}")
                    output.append(line)
                else:
                    break
            return output

        commands = [
            "login anonymous",
            "app_update 2430930 validate",
            "quit"
        ]

        for cmd in commands:
            logging.info(f"Sending command: {cmd}")
            stdout, stderr = process.communicate(input=f"{cmd}\n", timeout=30)
            logging.info(f"SteamCMD stdout: {stdout.strip()}")
            logging.info(f"SteamCMD stderr: {stderr.strip()}")

            # Read any remaining output
            remaining_output = read_output(process)
            for line in remaining_output:
                logging.info(f"Remaining steamcmd output: {line}")

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
