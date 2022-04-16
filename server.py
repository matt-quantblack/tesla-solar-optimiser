import datetime
import json
from pathlib import Path
import os
from flask_cors import CORS
from flask import Flask, request

# TODO: End points for force_charge configuration, getting tesla url and updating token ect.

app = Flask(__name__, static_folder='./web_app/build/', static_url_path='/')

if os.environ.get('ENV', 'DEV') == 'DEV':
    # Configure app
    CORS(app)


@app.route("/api/v1/solar_charge_state", methods=['GET'])
def get_solar_charge_state() -> str:
    """
    Gets the current state of the charging system
    Returns:
        The charge state object as a json string
    """
    current_state = Path('current_state.json').read_text()
    return current_state


@app.route("/api/v1/force_charge", methods=['GET'])
def get_force_charge() -> str:
    """
    Gets the command object for the force charge command
    Returns:
        The command object as a json string
    """
    force_charge = Path('force_charge.json').read_text()
    return force_charge


@app.route("/api/v1/force_charge", methods=['PATCH'])
def update_force_charge() -> str:
    """
    Toggles a true/false value for forcing the car to charge even if there is not enough solar
    Returns:
        The command object as a json string
    """
    if 'force_charge' not in request.json or not isinstance(request.json['force_charge'], bool):
        return 'force_charge must be True or False', 400

    command = {
        'request_time': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'force_charge': request.json['force_charge']
    }
    Path('force_charge.json').write_text(json.dumps(command))
    return json.dumps(command)


# This is a catch all path to send any non-api requests to the React front end
@app.route('/', defaults={'path': ''})
def catch_all(path: str):
    return app.send_static_file('index.html')


if __name__ == '__main__':
    """
    Flask server to view current state and activate/deactivate force charging
    """
    print("Booting Flask Server")
    app.run(host='0.0.0.0')
