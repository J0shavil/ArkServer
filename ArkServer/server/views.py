import subprocess
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logging.basicConfig(level=logging.INFO)

steamcmd_path = "C:\\Users\\josh_\\OneDrive\\Documentos\\ArkServer\\ArkServer\\ArkServer\\steamcmd"



class StartArkServer(APIView):

    def run_steamcmd(self):
        try:
            result = subprocess.run(
                [steamcmd_path, "+login", "anonymous", "+app_update", "2430930", "+quit"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                logging.info("SteamCMD process completed successfully")
                logging.info(result.stdout)
            else:
                logging.error("SteamCMD process failed")
                logging.error(result.stderr)
                raise Exception("SteamCMD process failed")

        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            raise

    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
