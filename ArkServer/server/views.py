from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pexpect
import logging

logging.basicConfig(level=logging.INFO)

class StartArkServer(APIView):

    def run_steamcmd(self):
        steamcmd_dir = 'steamcmd'  # Update with your actual path
        steamcmd_path = f"{steamcmd_dir}/steamcmd.exe"

        child = pexpect.spawn(steamcmd_path)

        def send_command(cmd):
            child.sendline(cmd)
            child.expect('Steam>')

        send_command("login anonymous")

        # Continue with other commands
        send_command("app_update 2430930 validate")
        send_command("quit")

        child.close()

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
