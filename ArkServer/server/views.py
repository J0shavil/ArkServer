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
from django.views.decorators.http import require_POST
import json
from django.middleware.csrf import get_token
from rest_framework import status
import bcrypt
from .models import Server
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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




def password_hash(password):
    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password, salt
    
@csrf_exempt  
def createserverstartup_bat(request):

    response = JsonResponse({'message': 'Default message'})
    response["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response["Access-Control-Allow-Credentials"] = "true"
    if request.method == "OPTIONS":
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        return response

    print(request.headers)
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

        hashed_password, salt = password_hash(password)

        hashed_admin_password, salt_admin = password_hash(admin_password)

        Server.objects.create(
            server_session_name=server_name, 
            server_password_hash = hashed_password.decode('utf-8'),
            server_password_salt = salt.decode('utf-8'),
            admin_password_hash = hashed_admin_password.decode('utf-8'),
            admin_password_salt = salt_admin.decode('utf-8'),
            max_server_players = max_players,
            map_name = map_name,
            )

        bat_content = f"""
        @echo off
        start ArkAscendedServer.exe {map_name}?SessionName={server_name}?ServerPassword={hashed_password}?AltSaveDirectoryName=TheIsland?MaxPlayers={max_players}?ServerAdminPassword={hashed_admin_password} -server -log -QueryPort=27015 -Port=7777
        """

        directory = r"C:\\Users\\josh_\\OneDrive\\Documentos\\ArkServer\\ArkServer\\ArkServer\\steamcmd\\steamapps\\common\\ARK Survival Ascended Dedicated Server\\ShooterGame\\binaries\Win64"
        
        file_path = os.path.join(directory, f"{server_name}.bat")

        with open (file_path, "w", encoding="utf-8") as file:
            file.write(bat_content)
        
        print(server_name)
        print(password)

        return JsonResponse({'message': 'Bat file created successfully!'})
    return JsonResponse({'message': 'Invalid method!'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

def runserver_bat(request):
    try:
        subprocess.run(r"C:\\Users\\josh_\\OneDrive\\Documentos\\ArkServer\\ArkServer\\ArkServer\\steamcmd\\steamapps\\common\\ARK Survival Ascended Dedicated Server\\ShooterGame\\binaries\Win64", shell=True, check=True)
        print("Bat file started successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error executing bat file: {e}")

def file_exists(file_path):
    return os.path.exists(file_path)


from django.http import JsonResponse

@csrf_exempt
def get_csrf_token(request):
    csrf_token = get_token(request)
    response = JsonResponse({'csrfToken': csrf_token})
    response["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response["Access-Control-Allow-Credentials"] = "true"
    return response


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login  # Rename the login function

@csrf_exempt
def custom_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Use renamed login function
            
            # Check user status code
            if user.is_active:
                return JsonResponse({'message': 'Login successful', 'status_code': 200})
            else:
                return JsonResponse({'error': 'User is inactive', 'status_code': 403}, status=403)
        else:
            return JsonResponse({'error': 'Invalid username or password', 'status_code': 400}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed', 'status_code': 405}, status=405)


@csrf_exempt
def register(request):
    response = JsonResponse({'message': 'Default message'})
    response["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response["Access-Control-Allow-Credentials"] = "true"

    if request.method == "OPTIONS":
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        return response
    
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        username = data.get('username')
        password = data.get('password')

        print(username)
        print(password)
        
        if not username or not password:
            print("NOT USERNAME AND NOT PASS")
            return JsonResponse({'error': 'Username and password are required.'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username is already taken.'}, status=409)  # 409 Conflict
        
        print("USER CREATED")
        # Create a new user
        user = User.objects.create_user(username=username, password=password)
        
        # Authenticate and log in the user
        
        
        return JsonResponse({'message': 'User registered and logged in successfully.'})
    else:
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

def logout(request):
    logout(request)
    return redirect('https://localhost:3000/')

def get_server(request):
    pass