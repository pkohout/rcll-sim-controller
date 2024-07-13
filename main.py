import threading
import time

from flask import Flask, request, jsonify, render_template
import subprocess

app = Flask(__name__)
kube_config_file = "KUBECONFIG=/home/peter/.config/OpenLens/kubeconfigs/755af755-1473-49b0-8ba0-f9645e34f261"
namespace_and_container_selection = "--namespace rcll --container refbox"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        'status': 'success',
        'message': 'This is the info endpoint.',
        'data': {
            'points': get_points_last_game(kube_config_file, namespace_and_container_selection),
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
    pod_name_cmd = ["/bin/bash", "-c", bash_line]
    process = subprocess.run(pod_name_cmd, capture_output=True, text=True)


def get_refbox_pod_name():
    bash_line = kube_config_file + " kubectl get pods --namespace rcll -l app=refbox -o custom-columns=\":metadata.name\" | grep refbox"
    pod_name_cmd = ["/bin/bash", "-c", bash_line]
    process = subprocess.run(pod_name_cmd, capture_output=True, text=True)
    pod_name = str(process.stdout).strip()
    return pod_name

def get_points_last_game(kube_config_file, namespace_and_container_selection):
    commandPoints = ["/bin/bash", "-c",
                     kube_config_file + " kubectl logs " + get_refbox_pod_name() + " " + namespace_and_container_selection + "  | grep \"TOTAL POINTS\""]
    resultPoints = subprocess.run(commandPoints, capture_output=True, text=True)
    return resultPoints.stdout

def get_run_in_refbox_command(command):
    return ["/bin/bash", "-c",
                     kube_config_file + " kubectl exec " + get_refbox_pod_name() + " " + namespace_and_container_selection + " -- " + command]

def start_new_games(amount):
    for i in range(0, amount):
        print(f"Starting game {i+1}")
        stop_all_pods()
        time.sleep(60)
        start_new_game()
        time.sleep(20 * 60) #game time
        time.sleep(120) #buffer time
        print(f"Last game had: {get_points_last_game(kube_config_file, namespace_and_container_selection)} points!")

def start_new_game():
    p1 = subprocess.run(get_run_in_refbox_command("rcll-refbox-instruct -c GRIPS"), capture_output=True, text=True)
    print(p1.returncode)
    p2 = subprocess.run(get_run_in_refbox_command("rcll-refbox-instruct -s RUNNING"), capture_output=True, text=True)
    print(p2.returncode)
    p3 = subprocess.run(get_run_in_refbox_command("sleep 15"), capture_output=True, text=True)
    print(p3.returncode)
    p4 = subprocess.run(get_run_in_refbox_command("rcll-refbox-instruct -p PRODUCTION"), capture_output=True, text=True)
    print(p4.returncode)

if __name__ == '__main__':
    app.run(debug=True)
