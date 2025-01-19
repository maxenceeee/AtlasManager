from flask import Flask, request, send_file
import json
import requests

nodes = []

cpuLoadCoefficient = 0.7
memoryCoefficient = 0.3
template_directory = None
app = Flask(__name__)
#--------------------------------------------------------------------

def get_resources_nodes():
    nodes_data = []
    for node in nodes:
        ip = node["ip"]
        port = node["port"]

        data = requests.get(f"http://{ip}:{port}/status")
        data = json.loads(data.text)
        nodes_data.append({"name": node["name"], "data": data})
    return nodes_data

def get_better_nodes():
    nodes_data = get_resources_nodes()

    global cpuLoadCoefficient
    global memoryCoefficient
    nodes_score = []
    for node in nodes_data:
        score = 0
        score += (100 - node["data"]["cpu"]) * cpuLoadCoefficient
        score += (node["data"]["memory"]['available']) * memoryCoefficient
        nodes_score.append({"name": node["name"], "score": score})

    nodes_score.sort(key=filter_by_score, reverse=True)
    return nodes_score[0]

def filter_by_score(e):
    return e["score"]
#------------------------------------------------------

@app.route("/template_file")
def get_template_file():
    data = request.args.get("template_name")

    global template_directory
    try:
        return send_file(f"{template_directory}/{data}.zip")
    except FileNotFoundError:
        return 'Error: Template file not found.', 404



if __name__ == '__main__':
    config_file = './config.json'
    with open(config_file, 'r') as file:
        config = json.load(file)

    node_config = config['nodes']
    for node_index, node_data in node_config.items():

        node_name = node_data['name']
        node_ip = node_data['ip']
        node_port = node_data['port']

        nodes.append({"name": node_name, "ip": node_ip, "port": node_port})

    template_directory = config['templates']

    port = config['port']

    app.run(host='0.0.0.0', port=port, debug=True)