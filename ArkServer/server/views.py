import subprocess
import logging
import shutil
import requests
import zipfile
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logging.basicConfig(level=logging.INFO)

class StartArkServer(APIView):

    STEAMCMD_PATH = "C:\\Users\\josh_\\OneDrive\\Documentos\\ArkServer\\ArkServer\\ArkServer\\steamcmd"
    STEAMCMD_URL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
    STEAMCMD_ZIP_PATH = "steamcmd.zip"

    def is_steamcmd_installed(self):
        return shutil.which("steamcmd") is not None

    def install_steamcmd(self):
        try:
            logging.info("Downloading SteamCMD...")
            response = requests.get(self.STEAMCMD_URL)
            
            with open(self.STEAMCMD_ZIP_PATH, 'wb') as f:
                f.write(response.content)
            
            logging.info("Extracting SteamCMD...")
            with zipfile.ZipFile(self.STEAMCMD_ZIP_PATH, 'r') as zip_ref:
                zip_ref.extractall(self.STEAMCMD_PATH)

            os.remove(self.STEAMCMD_ZIP_PATH)
            
            logging.info("SteamCMD installed successfully.")
            print("SteamCMD installed successfully.")  # Print to terminal

        except Exception as e:
            logging.error(f"Error installing SteamCMD: {e}")
            print(f"Error installing SteamCMD: {e}")  # Print to terminal
            raise

    def run_steamcmd(self):
        steam_cmd = os.path.join(self.STEAMCMD_PATH, "steamcmd.exe")
        try:
            if not self.is_steamcmd_installed():
                logging.error("SteamCMD is not installed")
                print("SteamCMD is not installed. Installing...")  # Print to terminal
                self.install_steamcmd()

            logging.info("Updating Ark Server...")
            
            # Start the steamcmd process
            process = subprocess.Popen(
                [steam_cmd, "+login", "anonymous", "+app_update", "2430930", "+quit"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                text=True
            )
            
            # Read and log output line by line
            for line in iter(process.stdout.readline, ''):
                logging.info(line.strip())
                print(line.strip())  # Print to terminal
            
            process.stdout.close()
            process.wait()

            if process.returncode == 0:
                logging.info("Ark Server update completed successfully")
                print("Ark Server update completed successfully")  # Print to terminal
            else:
                logging.error("Ark Server update failed")
                print("Ark Server update failed")  # Print to terminal
                raise Exception("Ark Server update failed")

        except Exception as e:
            logging.error(f"Error while updating Ark Server: {e}")
            print(f"Error while updating Ark Server: {e}")  # Print to terminal
            raise


    def post(self, request, *args, **kwargs):
        try:
            self.run_steamcmd()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Error while running steamcmd: {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
