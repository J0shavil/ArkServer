from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import ptyprocess
import logging
import time

logging.basicConfig(level=logging.INFO)

class StartArkServer(APIView):

    def run_steamcmd(self):
        steamcmd_dir = 'steamcmd'  # Update with your actual path
        steamcmd_path = f"{steamcmd_dir}/steamcmd.exe"

        process = ptyprocess.popen_spawn.PopenSpawn(
            [steamcmd_path], 
            cwd=steamcmd_dir, 
            timeout=30
        )

        def send_command(cmd, target_line):
            process.expect(target_line, timeout=30)
            logging.info(f"Received target line: {target_line}")
            process.write(f"{cmd}\n".encode('utf-8'))
            process.expect(target_line, timeout=30)

        send_command("login anonymous", "Loading Steam API...OK")
        send_command("app_update 2430930 validate", "Waiting for user info...OK")
        send_command("quit", "Success! App '2430930' fully installed.")

        process.close()

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
