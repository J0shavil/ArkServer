import subprocess
import logging
import shutil
import requests
import zipfile
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

logging.basicConfig(level=logging.INFO)

class StartArkServer(APIView):

    STEAMCMD_PATH = r"C:\\Users\\josh_\\OneDrive\\Documentos\\ArkServer\\ArkServer\\ArkServer\\steamcmd"
    STEAMCMD_URL = r"https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
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

            # Check the last line of the output for success
            if "Update complete, launching..." or "AtualizaÃ§Ã£o concluÃ­da, a iniciar Steam..." in line:
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
        
@csrf_exempt    
def createserverstartup_bat(request):
    if request.method == "POST":

        data_unicode = request.body.decode('utf-8')

        data = json.loads(data_unicode)

        server_name = data.get("Server name")
        password = data.get("Password")
        map_name = data.get("Map")
        admin_password = data.get("Admin Password")
        max_players = data.get("Max Players")

        directory = r"C:\\Users\\josh_\\OneDrive\\Documentos\\ArkServer\\ArkServer\\ArkServer\\steamcmd\\steamapps\\common\\ARK Survival Ascended Dedicated Server\\ShooterGame\\binaries\Win64"
        
        check_filepath = f"C:\\Users\\josh_\\OneDrive\\Documentos\\ArkServer\\ArkServer\\ArkServer\\steamcmd\\steamapps\\common\\ARK Survival Ascended Dedicated Server\\ShooterGame\\binaries\\Win64\\{server_name}.bat"

        if file_exists(check_filepath):
            return JsonResponse({'message': 'A server with that name already exists.'})

        bat_content = f"""
        @echo off
        start ArkAscendedServer.exe {map_name}?SessionName={server_name}?ServerPassword={password}?AltSaveDirectoryName=TheIsland?MaxPlayers={max_players}?ServerAdminPassword={admin_password} -server -log -QueryPort=27015 -Port=7777
        """

        directory = "C:\\Users\\josh_\\OneDrive\\Documentos\\ArkServer\\ArkServer\\ArkServer\\steamcmd\\steamapps\\common\\ARK Survival Ascended Dedicated Server\\ShooterGame\\binaries\Win64"
        
        file_path = os.path.join(directory, f"{server_name}.bat")

        with open (file_path, "w", encoding="utf-8") as file:
            file.write(bat_content)
        
        print(server_name)
        print(password)

        return JsonResponse({'message': 'Bat file created successfully!'})
    return JsonResponse({'message': 'Invalid method!'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

def runserver_bat(request):
    pass

def file_exists(file_path):
    return os.path.exists(file_path)