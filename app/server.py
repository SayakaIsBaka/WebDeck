# Standard library imports
import time
import threading
import subprocess
import shutil
import re
import random
import json
import os
import sys
import importlib
import ipaddress
import inspect
import ast

# Third-party library imports
import requests
import spotipy
import spotipy.util as util
from deepdiff import DeepDiff
import mss
from PIL import Image
try: from deep_translator import GoogleTranslator
except SyntaxError: pass
import pyautogui as keyboard
import keyboard as keyboard2
import webcolors
import pyaudio
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from flask_minify import Minify
from engineio.async_drivers import gevent # DO NOT REMOVE
import pyperclip
import win32api
import win32con
import win32gui
from win32com.client import Dispatch
if sys.platform == 'win32':
    from win10toast import ToastNotifier
import easygui
import psutil
import GPUtil
import pynvml

try:
    import vlc
except:
    pass
from obswebsocket import obsws, events
from obswebsocket import requests as obsrequests

# Numerical and scientific libraries
import numpy as np
import ctypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume
import comtypes
import math

# WebDeck imports
from app.on_start import on_start, check_json_update
from app.functions.global_variables import set_global_variable, get_global_variable
from app.functions.themes.parse_themes import parse_themes
from app.functions.plugins.load_plugins import load_plugins
from app.functions.firewall import fix_firewall_permission, check_firewall_permission
from app.functions.load_lang_file import load_lang_file
from app.functions.audio_devices import get_audio_devices
from app.functions.merge_dicts import merge_dicts
from app.buttons.usage import get_usage

from app.buttons import command
import app.buttons.soundboard as soundboard


config, text, commands, local_ip = on_start()
set_global_variable("text", text)
set_global_variable("config", config)


def save_config(config):
    with open("config.json", "w", encoding="utf-8") as json_file:
        json.dump(config, json_file, indent=4)
    set_global_variable("config", config)
    return config


def create_folders(config):
    global folders_to_create
    for folder in folders_to_create:

        config["front"]["buttons"][folder["name"]] = [
            {
                "image": "back10.svg",
                "image_size": "110%",
                "message": f"/folder {folder['parent_folder']}",
                "name": f"back to {folder['parent_folder']}",
            }
        ]

        void_count = int(config["front"]["width"]) * int(config["front"]["height"])
        for _ in range(void_count - 1):
            config["front"]["buttons"][folder["name"]].append({"VOID": "VOID"})

        print("NEW FOLDER :", folder["name"])
    folders_to_create = []
    return config


def print_dict_differences(dict1, dict2):
    diff = DeepDiff(dict1, dict2, ignore_order=True)

    print("Differences found :")
    for key, value in diff.items():
        print(f"Key : {key}")
        print(f"Difference : {value}")
        print("----------------------")





# resize grid ||| start

def create_matrix(config):
    matrix = []
    for folder_count, (folder_name, folder_content) in enumerate(
        config["front"]["buttons"].items()
    ):
        row_count = 0
        matrix.append([])
        for count, button in enumerate(folder_content, start=1):
            if row_count >= len(matrix[folder_count]):
                matrix[folder_count].append([])
            matrix[folder_count][row_count].append(button)
            if count % int(config["front"]["width"]) == 0:
                row_count += 1
    matrix_height = len(matrix)
    matrix_width = len(matrix[0])
    return matrix


def unmatrix(matrix):
    for folder_count, folder in enumerate(matrix):
        folderName = list(config["front"]["buttons"])[folder_count]
        config["front"]["buttons"][folderName] = []
        for row in folder:
            for button in row:
                config["front"]["buttons"][folderName].append(button)

    return config


def update_gridsize(config, new_height, new_width):
    new_height, new_width = int(new_height), int(new_width)
    matrix = create_matrix(config)
    old_height, old_width = int(config["front"]["height"]), int(
        config["front"]["width"]
    )

    # if height has changed
    if old_height != new_height:

        # if the height has increased
        if new_height > old_height:
            difference = new_height - old_height
            for count, _ in enumerate(range(difference), start=1):
                for folder_name, folder_content in config["front"]["buttons"].items():
                    for _ in range(old_width):
                        # if count % 2 == 0:
                        #     folder_content.insert(0, {"VOID": "VOID"})
                        # else:
                        folder_content.append({"VOID": "VOID"})
            matrix = create_matrix(config)

        # if the height has decreased
        if old_height > new_height:
            difference = old_height - new_height
            print("height decreased")
            for count, _ in enumerate(range(difference), start=1):
                for folder_count, folder in enumerate(matrix):
                    for row_count, row in enumerate(reversed(folder)):
                        if all(element == {"VOID": "VOID"} for element in row):
                            folder.pop(-row_count - 1)
                            break
                    else:
                        for col_count in range(len(folder[0])):
                            for row_count, row in enumerate(reversed(folder), start=1):
                                if folder[-row_count][col_count] == {"VOID": "VOID"}:
                                    num = row_count
                                    while num > 1:
                                        folder[-num][col_count] = folder[-num + 1][
                                            col_count
                                        ]
                                        num -= 1
                                    folder[-num][col_count] = {"DEL": "DEL"}
                                    break
                            else:
                                x = False
                                for colb_count in range(len(folder[0])):
                                    for rowb_count in range(len(folder)):
                                        if folder[rowb_count][colb_count] == {
                                            "VOID": "VOID"
                                        }:
                                            folder[rowb_count][colb_count] = folder[-1][
                                                col_count
                                            ]
                                            x = True
                                            break
                                    if x == True:
                                        break
                                if x == False:
                                    print("NOT ENOUGH SPACE")
                        folder.pop(-1)

    # if width has changed
    if old_width != new_width:

        # if the width has increased
        if new_width > old_width:

            difference = new_width - old_width
            new_matrix = matrix
            for count, _ in enumerate(range(difference), start=1):
                for folder_count, folder in enumerate(matrix):
                    for row_count, row in enumerate(folder):
                        # if count % 2 == 0:
                        #     new_matrix[folder_count][row_count].insert(0, {"VOID": "VOID"})
                        # else:
                        new_matrix[folder_count][row_count].append({"VOID": "VOID"})
            matrix = new_matrix

        if new_width < old_width:
            difference = old_width - new_width
            print("width decreased")
            for count, _ in enumerate(range(difference), start=1):
                for folder in matrix:
                    for col_count in range(len(folder[0])):
                        if all(
                            folder[row_count][-col_count - 1] == {"VOID": "VOID"}
                            for row_count in range(len(folder))
                        ):
                            for row_count in range(len(folder)):
                                folder[row_count].pop(-col_count - 1)
                            break
                    else:
                        element_to_del = 0
                        for row in folder:
                            element_to_del += 1
                            for element_count, element in enumerate(row):
                                if element == {"VOID": "VOID"}:
                                    row.pop(element_count)
                                    element_to_del -= 1
                                    if element_to_del == 0:
                                        break
                        if element_to_del > 0:
                            for row in folder:
                                for element_count, element in enumerate(row):
                                    if element == {"VOID": "VOID"}:
                                        row.pop(element_count)
                                        element_to_del -= 1
                                        if element_to_del == 0:
                                            break
                                if element_to_del == 0:
                                    break
                        if element_to_del > 0:
                            print("NOT ENOUGH SPACE")

    config = unmatrix(matrix)
    print(old_height, new_height)
    print(old_width, new_width)
    return config


# resize grid ||| end



# for folder_name, folder_content in config["front"]["buttons"].items():
#     for button in folder_content:
#         if 'action' not in button.keys():
#             button['action'] = {
#                 "touch_start": "click",
#                 "touch_keep": "None",
#                 "touch_end": "none",
#             }


#         if 'image' in button.keys() and not button['image'].strip() == '' and ':' in button['image'] and not button['image'].startswith('http'):
#             button['image'] = button['image'].replace('/', '\\')
#             splitted = button['image'].split('\\')
#             try:
#                 copyfile(button['image'],f'static/files/images/{splitted[-1]}')
#             except Exception:
#                 pass


app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.jinja_env.globals.update(get_audio_devices=get_audio_devices)
if getattr(sys, "frozen", False):
    Minify(app=app, html=True, js=True, cssless=True)
app.config["SECRET_KEY"] = "secret!"

socketio = SocketIO(app)


# Set up the OBS WebSocket client
def reload_obs():
    obs_host = config["settings"]["obs"]["host"]
    obs_port = int(config["settings"]["obs"]["port"])
    obs_password = config["settings"]["obs"]["password"]

    obs = obsws(obs_host, obs_port, obs_password)

    return obs_host, obs_port, obs_password, obs

obs_host, obs_port, obs_password, obs = reload_obs()


@app.route("/usage", methods=["POST"])
def usage():
    return jsonify(get_usage())


# Middleware to check request IP address
@app.before_request
def check_local_network():
    remote_ip = request.remote_addr    

    netmask = '255.255.255.0'

    ip_local = ipaddress.IPv4Network(local_ip + '/' + netmask, strict=False)
    ip_remote = ipaddress.IPv4Network(remote_ip + '/' + netmask, strict=False)
    
    # print(f"local IP is: {local_ip}")
    # print(f"remote: {remote_ip}")
    # print(f"IP1: {ip_local} == IP2: {ip_remote} {ip_local == ip_remote}")
    
    # print(f'new connection established: {remote_ip}')
    
    if ip_remote != ip_local:
        return (
            "Unauthorized access: you are not on the same network as the server.",
            403,
        )


@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(message)

    return dict(mdebug=print_in_console)


# Function to get all the svgs from the theme file, so we can load them during the loading screen
def get_svgs():
    svgs = []

    with open(f"static/themes/{config['front']['theme']}", "r") as f:
        content = f.read()

        # url(...)
        matches = re.findall(r"url\(([^)]+)\)", content)

        for match in matches:
            if match.endswith(".svg"):
                svgs.append(match)

    return svgs


@app.route("/")
def home():
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    new_config = check_json_update(config)
    with open("config.json", "w", encoding="utf-8") as json_file:
        json.dump(new_config, json_file, indent=4)
    config = new_config

    with open("commands.json", encoding="utf-8") as f:
        commands = json.load(f)
        commands, all_func = load_plugins(commands)
        set_global_variable("all_func", all_func)
        
    text = load_lang_file(config['settings']['language'])
    set_global_variable("text", text)
        
    with open("static/files/version.json", encoding="utf-8") as f:
        versions = json.load(f)
    is_exe = bool(getattr(sys, "frozen", False))

    random_bg = "//"
    while random_bg.startswith("//") == True:
        random_bg = random.choice(config["front"]["background"])
        if random_bg.startswith("**uploaded/"):
            random_bg_path = random_bg.replace("**uploaded/", "static/files/uploaded/")
            if os.path.exists(random_bg_path):
                file_name, extension = os.path.splitext(
                    os.path.basename(random_bg_path)
                )
                random_bg_90_path = f"static/files/uploaded/{file_name}-90{extension}"
                if not os.path.exists(random_bg_90_path):
                    try:
                        img = Image.open(random_bg_path)
                        img_rotated = img.rotate(-90, expand=True)
                        file_name, extension = os.path.splitext(
                            os.path.basename(random_bg_path)
                        )
                        img_rotated.save(random_bg_90_path)
                    except Exception as e:
                        print(e)
    print(f"random background: {random_bg}")

    themes = [
        file_name
        for file_name in os.listdir("static/themes/")
        if file_name.endswith(".css")
    ]
    langs = [
        file_name.replace(".lang", "")
        for file_name in os.listdir("static/files/langs/")
        if file_name.endswith(".lang")
    ]

    return render_template(
        "index.jinja",
        config=config, default_theme=config['front']['theme'], themes=themes, parsed_themes=parse_themes(text),
        commands=commands, versions=versions, random_bg=random_bg, usage_example=get_usage(True),
        langs=langs, text=text,
        svgs=get_svgs(), is_exe=is_exe, portrait_rotate=config['front']['portrait-rotate'],
        int=int, str=str, dict=dict, json=json, type=type, eval=eval, open=open,
        isfile=os.path.isfile
    )


folders_to_create = []

@app.route("/save_config", methods=["POST"])
def saveconfig():
    global config, folders_to_create, obs_host, obs_port, obs_password, obs

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    # Retrieve form data
    new_config = request.get_json()

    new_height = new_config["front"]["height"]
    new_width = new_config["front"]["width"]
    config = update_gridsize(config, new_height, new_width)
    config["front"]["height"] = new_height
    config["front"]["width"] = new_width

    soundboard_restart = (
        not config["settings"]["soundboard"] == new_config["settings"]["soundboard"]
    )
    obs_reload = not config["settings"]["obs"] == new_config["settings"]["obs"]

    soundboard_start = False
    soundboard_stop = False
    if (
        not config["settings"]["soundboard"]["enabled"]
        == new_config["settings"]["soundboard"]["enabled"]
    ):
        if new_config["settings"]["soundboard"]["enabled"] == "true":
            soundboard_start = True
        else:
            soundboard_stop = True

    config = check_json_update(config)
    new_config = check_json_update(new_config)

    if (
        config["settings"]["windows-startup"].lower().strip() == "false"
        and new_config["settings"]["windows-startup"].lower().strip() == "true"
    ):
        if getattr(sys, "frozen", False):
            dir = (
                os.getenv("APPDATA") + r"\Microsoft\Windows\Start Menu\Programs\Startup"
            )
            path = os.path.join(dir, "WebDeck.lnk")
            target = os.getcwd() + r"\\WebDeck.exe"
            working_dir = os.getcwd()
            icon = os.getcwd() + r"\\WebDeck.exe"

            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = working_dir
            shortcut.IconLocation = icon
            shortcut.save()
    elif (
        config["settings"]["windows-startup"].lower().strip() == "true"
        and new_config["settings"]["windows-startup"].lower().strip() == "false"
    ):
        if getattr(sys, "frozen", False):
            file_path = (
                os.getenv("APPDATA")
                + r"\Microsoft\Windows\Start Menu\Programs\Startup\WebDeck.lnk"
            )
            if os.path.exists(file_path):
                os.remove(file_path)

    config = merge_dicts(config, new_config)
    config = create_folders(config)
    config = save_config(config)

    try:
        config["front"]["background"] = config["front"]["background"].replace("['", '["').replace("']", '"]').replace("', '", "','").replace("','", '","')
        config["front"]["background"] = ast.literal_eval(config["front"]["background"])
    except TypeError:
        pass

    with open("config.json", "w", encoding="utf-8") as json_file:
        json.dump(config, json_file, indent=4)

    if soundboard_stop:
        soundboard.mic.stop()
    elif soundboard_restart or soundboard_start:
        soundboard.mic.restart()

    if obs_reload:
        obs_host, obs_port, obs_password, obs = reload_obs()

    return jsonify({"success": True})


# Save the config ENTIRELY, it does not merge anything
@app.route("/COMPLETE_save_config", methods=["POST"])
def complete_save_config():
    global folders_to_create
    
    old_height = config["front"]["height"]
    old_width = config["front"]["width"]
    config = request.get_json()
    new_height = config["front"]["height"]
    new_width = config["front"]["width"]

    config = create_folders(config)
    config = save_config(config)

    config["front"]["height"] = old_height
    config["front"]["width"] = old_width
    config = update_gridsize(config, new_height, new_width)
    config["front"]["height"] = new_height
    config["front"]["width"] = new_width
    with open("config.json", "w", encoding="utf-8") as json_file:
        json.dump(config, json_file, indent=4)

    return jsonify({"success": True})


@app.route("/save_single_button", methods=["POST"])
def save_single_button():
    data = request.get_json()
    button_folder = int(data.get("location_Folder"))
    button_index = int(data.get("location_Id"))
    button_content = data.get("content")

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    button_folderName = list(config["front"]["buttons"])[button_folder]
    print(
        "FETCH /save_single_button -> before :"
        + str(config["front"]["buttons"][button_folderName][button_index])
    )
    config["front"]["buttons"][button_folderName][button_index] = button_content
    print(
        "FETCH /save_single_button -> after  :"
        + str(config["front"]["buttons"][button_folderName][button_index])
    )

    with open("config.json", "w", encoding="utf-8") as json_file:
        json.dump(config, json_file, indent=4)
        set_global_variable("config", config)

    return jsonify({"success": True})


# Save the config but only the buttons
@app.route("/save_buttons_only", methods=["POST"])
def save_buttons_only():
    global folders_to_create

    # Get current config first
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    # Retrieve form data
    new_config = request.get_json()

    new_config = new_config["front"]["buttons"]

    temp_order_list = [key for key, value in config["front"]["buttons"].items()]

    sorted_buttons = {}
    for folder in temp_order_list:
        sorted_buttons[folder] = new_config.get(folder)

    config["front"]["buttons"] = sorted_buttons
    config = create_folders(config)
    config = save_config(config)
    return jsonify({"success": True})


@app.route("/get_config", methods=["GET"])
def get_config():
    global folders_to_create, config

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    config = create_folders(config)
    set_global_variable("config", config)

    with open("config.json", "w", encoding="utf-8") as json_file:
        json.dump(config, json_file, indent=4)
        set_global_variable("config", config)

    return jsonify(config)


@app.route("/upload_folderpath", methods=["POST"])
def upload_folderpath():
    path = easygui.diropenbox()
    if path is None:
        path = ""
        
    return path

@app.route("/upload_filepath", methods=["POST"])
def upload_filepath():
    filetypes = request.args.get("filetypes")
    default = '*'
    if filetypes is not None:
        filetypes = filetypes.split('_')
        filetypes = [f"*{item}" for item in filetypes]
        default = filetypes[0]

    path = easygui.fileopenbox(filetypes=filetypes, default=default)
    if path is None:
        path = ""
        
    return path


@app.route("/upload_file", methods=["POST"])
def upload_file():
    print("request:", request)
    print("request.files:", request.files)
    if "file" not in request.files:
        return jsonify({"success": False, "message": text["no_files_found_error"]})

    uploaded_file = request.files["file"]

    save_path = os.path.join("static/files/uploaded", uploaded_file.filename)
    uploaded_file.save(save_path)

    if request.form.get("info") and request.form.get("info") == "background_image":
        try:
            img = Image.open(save_path)
            img_rotated = img.rotate(-90, expand=True)
            file_name, extension = os.path.splitext(os.path.basename(save_path))
            img_rotated.save(f"static/files/uploaded/{file_name}-90{extension}")
        except Exception as e:
            print(e)

    return jsonify({"success": True, "message": text["downloaded_successfully"]})


@app.route("/create_folder", methods=["POST"])
def create_folder():
    global folders_to_create
    data = request.get_json()
    folder_name = data.get("name")
    parent_folder_name = data.get("parent_folder")

    if (
        all(item["name"] != folder_name for item in folders_to_create)
        and folder_name not in config["front"]["buttons"].keys()
    ):
        folders_to_create.append(
            {"name": f"{folder_name}", "parent_folder": f"{parent_folder_name}"}
        )
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


@socketio.on("connect")
def socketio_connect():
    print("Socketio client connected")
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

@socketio.event
def send(data):
    socketio.emit("json_data", data)

@socketio.on("message_from_socket")
def send_data_socketio(message):
    return command(message=message)


@app.route("/send-data", methods=["POST"])
def send_data_route():
    return command(message=request.get_json()["message"])


if (
    config["settings"]["automatic-firewall-bypass"] == "true"
    and check_firewall_permission() == False
):
    fix_firewall_permission()

print('local_ip: ', local_ip)

app.run(
    host=local_ip,
    port=config["url"]["port"],
    debug=config["settings"]["flask-debug"] == "true",
    use_reloader=config["settings"]["flask-debug"] == "false",
)
