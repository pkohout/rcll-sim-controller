import logging
import os
import threading
import time

from flask import Flask, request, jsonify, render_template
import subprocess

app = Flask(__name__)
kube_config_file = "KUBECONFIG=" + os.getenv("K8S_CONFIG")
namespace_and_container_selection = "--namespace rcll --container refbox"
log = logging.getLogger("controller")
log.setLevel(logging.INFO)
# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# Add the handler to the logger
log.addHandler(console_handler)
# Log a message
log.info("Started logger!")
log.info(f"Using k8s config file: {kube_config_file}")
@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        'status': 'success',
        'message': 'This is the info endpoint.',
        'data': {
            'points': get_points_last_game(),
        }
    })


@app.route('/cancel-game', methods=['POST'])
def cancel_game():
    stop_all_pods()

    # Perform some action with the data
    action_result = {
        'status': 'success',
        'message': 'Start action has been initiated.',
        'data_received': "Ok"
    }

    return jsonify(action_result)

@app.route('/start-multiple', methods=['POST'])
def startMultiple():
    number = request.form.get('number', type=int)
    thread = threading.Thread(target=start_new_games, args=(number,))
    thread.start()
    # Perform some action with the data
    action_result = {
        'status': 'success',
        'message': 'Start action has been initiated.',
        'data_received': "Ok"
    }

    return jsonify(action_result)
@app.route('/start', methods=['POST'])
def start():
    start_new_game()
    action_result = {
        'status': 'success',
        'message': 'Start action has been initiated.',
        'data_received': "Ok"
    }

    return jsonify(action_result)

def stop_all_pods():
    bash_line = kube_config_file + " kubectl delete pods --all --namespace rcll"
    stop_pod_cmd = ["/bin/bash", "-c", bash_line]
    log.info(f"Running: [{stop_pod_cmd}]")
    process = subprocess.run(stop_pod_cmd, capture_output=True, text=True)
    if process.returncode != 0:
        raise Exception("Error stopping all pods!")


def get_refbox_pod_name():
    bash_line = kube_config_file + " kubectl get pods --namespace rcll -l app=refbox -o custom-columns=\":metadata.name\" | grep refbox"
    pod_name_cmd = ["/bin/bash", "-c", bash_line]
    log.info(f"Running: [{pod_name_cmd}]")
    process = subprocess.run(pod_name_cmd, capture_output=True, text=True)
    if process.returncode != 0:
        raise Exception("Error get_refbox_pod_name!")
    pod_name = str(process.stdout).strip()
    return pod_name

def get_points_last_game():
    commandPoints = ["/bin/bash", "-c",
                     kube_config_file + " kubectl logs " + get_refbox_pod_name() + " " + namespace_and_container_selection + "  | grep \"TOTAL POINTS\""]
    log.info(f"Running: [{commandPoints}]")
    resultPoints = subprocess.run(commandPoints, capture_output=True, text=True)
    if resultPoints.returncode != 0:
        raise Exception("Error get_points_last_game!")
    return resultPoints.stdout

def get_run_in_refbox_command(command):
    return ["/bin/bash", "-c",
                     kube_config_file + " kubectl exec " + get_refbox_pod_name() + " " + namespace_and_container_selection + " -- " + command]

def start_new_games(amount):
    for i in range(0, amount):
        log.info(f"Starting game {i+1}")
        stop_all_pods()
        log.info("Waiting 60s buffer time")
        time.sleep(60)
        start_new_game()
        log.info("Waiting 20min game time")
        time.sleep(20 * 60) #game time
        log.info("Waiting 60s post game buffer time")
        time.sleep(60) #buffer time
        log.info(f"Last game had: {get_points_last_game()} points!")

def start_new_game():
    p1 = subprocess.run(get_run_in_refbox_command("rcll-refbox-instruct -c GRIPS"), capture_output=True, text=True)
    log.info(p1.returncode)
    p2 = subprocess.run(get_run_in_refbox_command("rcll-refbox-instruct -s RUNNING"), capture_output=True, text=True)
    log.info(p2.returncode)
    p3 = subprocess.run(get_run_in_refbox_command("sleep 15"), capture_output=True, text=True)
    log.info(p3.returncode)
    p4 = subprocess.run(get_run_in_refbox_command("rcll-refbox-instruct -p PRODUCTION"), capture_output=True, text=True)
    log.info(p4.returncode)

if __name__ == '__main__':
    app.run(debug=True)
