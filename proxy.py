from flask import Flask, jsonify, request
from resource_manager import Node
import docker

client = docker.from_env()


app = Flask(__name__)


nodes = []
jobs = [] #queue


@app.route('/cloudproxy/nodes/<name>')
def cloud_register(name):
    if request.method == 'GET':
        print('Request to register new node: ' + str(name))
        result = 'unknown'
        node_status = 'unknown'
        print("Node List before adding: "+ str([node.name for node in nodes]))

        for node in nodes:
            if name == node.name:
                print('Node already exists: ' + node.name + ' with status: ' + node.status)
                result = 'already_exists'
                node_status = node.status
        if result == 'unknown' and node_status == 'unknown':
            result = 'node_added'
            #creating a new node
            n = Node(name=name)
            nodes.append(n)
            node_status = 'Idle'
            print('Successfully added a new node: ' + str(name))

        print("Node List after adding: "+ str([node.name for node in nodes]))

        return jsonify({'result': result, 'node_status': node_status, 'node_name':name})

@app.route('/cloudproxy/rmnodes/<name>')
def cloud_rm_node(name):
    if request.method == 'GET':
        print('Request to remove node: ' + str(name))
        result = 'unknown'
        node_status = 'unknown'

        print("Node List before deleting: "+ str([node.name for node in nodes]))

        for node in nodes:
            if name == node.name:
                print('Node already exists: ' + node.name + ' with status: ' + node.status)
                result = 'already_exists'
                node_status = 'removed'
                nodes.remove(node)
        if result == 'unknown' and node_status == 'unknown':
            result = 'node DNE'
            node_status = 'node DNE'
            print('The node does not exist: ' + str(name))

        print("Node List after deleting: "+ str([node.name for node in nodes]))

        return jsonify({'result': result, 'node_status': node_status, 'node_name':name})

@app.route('/cloudproxy/init/')
def cloud_init():

    #initializing 50 nodes
    for i in range(50):
        c = client.containers.run('alpine','ash',detach=True,tty=True, name = f"node{i+1}")
        n = Node(name=f"node{i+1}", status="Idle", container=c)
        nodes.append(n)

    result = 'successful initialized idle 50 nodes'
    node_list = [node.name for node in nodes]
    return jsonify({'result': result, "node_list": node_list})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)


