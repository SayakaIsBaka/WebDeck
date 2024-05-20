from obswebsocket import obsws

from flask import jsonify

from app.utils.global_variables import get_global_variables

import app.buttons.obs.scenes as scene
import app.buttons.obs.recording as recording
import app.buttons.obs.streaming as stream
import app.buttons.obs.virtualcam as virtualcam


#    https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
#    https://github.com/Elektordi/obs-websocket-py



def handle_command(message, text):
    try:
        obs_host, obs_port, obs_password = get_global_variables(("obs_host", "obs_port", "obs_password"))
        
        obs = obsws(obs_host, obs_port, obs_password)
        obs.connect()
    except Exception as e:
        if "10061" in str(e):
            e = text["obs_error_10061"]
        elif "password may be inco" in str(e):
            e = text["obs_error_incorrect_password"]

        return jsonify({
            "success": False,
            "message": f"{text['obs_failed_connection_error'].replace('.','')}: {e}",
        })


    if message.startswith("/obs_toggle_rec"):
        recording.toggle(obs, text)

    elif message.startswith("/obs_start_rec"):
        recording.start(obs, text)

    elif message.startswith("/obs_stop_rec"):
        recording.stop(obs, text)


    elif message.startswith("/obs_toggle_rec_pause"):
        recording.pause_toggle(obs, text)

    elif message.startswith("/obs_pause_rec"):
        recording.pause(obs, text)
        
    elif message.startswith("/obs_resume_rec"):
        recording.resume(obs, text)


    elif message.startswith("/obs_toggle_stream"):
        stream.toggle(obs, text)

    elif message.startswith("/obs_start_stream"):
        stream.start(obs, text)

    elif message.startswith("/obs_stop_stream"):
        stream.stop(obs, text)


    elif message.startswith("/obs_toggle_virtualcam"):
        virtualcam.toggle(obs, text)

    elif message.startswith("/obs_start_virtualcam"):
        virtualcam.start(obs, text)

    elif message.startswith("/obs_stop_virtualcam"):
        virtualcam.stop(obs, text)


    elif message.startswith("/obs_scene"):
        scene_name = message.replace("/obs_scene", "")
        scene.set(obs, scene_name)


    obs.disconnect()