from flask import Flask, jsonify, request, render_template
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
                print('Node already exists: ' + node.name + ' with status: ' + node.container_status)
                result = 'already_exists'
                node_status = node.container_status

        if result == 'unknown' and node_status == 'unknown':
            result = 'node_added'
            #creating a new node
            #create the container
            c = client.containers.run('alpine','ash',detach=True,tty=True, name = name)
            n = Node(name=name, id = c.id, container =c, container_status="Running")
            nodes.append(n)
            node_status = 'Idle'
            print('Successfully added a new node: ' + str(name))

        print("Node List after adding: "+ str([node.name for node in nodes]))

        return jsonify({'result': result, 'node_status': node_status, 'node_name':name})

@app.route('/cloudproxy/rmnodes/<name>')
def cloud_rm_node(name):
    if request.method == 'GET':
        print('Request to remove node: ' + str(name))

        #check if the node is one of the default 50 nodes
        default_node = False
        for i in range(1,51):
            if name == f"node{i}":
                default_node = True
                break

        if default_node:
            result = 'Node already exists and is a default node'
            node_status = 'default node cannot be removed'
            return jsonify({'result': result, 'node_status': node_status, 'node_name':name})


        result = 'unknown'
        node_status = 'unknown'

        print("Node List before deleting: "+ str([node.name for node in nodes]))

        for node in nodes:
            if name == node.name:
                print('Node already exists: ' + node.name + ' with status: ' + node.container_status)

                if node.container_status == 'Running':
                    result = 'already_exists and running'
                    node_status = 'running node cannot be removed'
                    return jsonify({'result': result, 'node_status': node_status, 'node_name':name})


                result = 'already_exists and idle'
                node_status = 'removed'
                #need to actually remove the container using docker rm

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
        n = Node(name=f"node{i+1}", container=c, id=c.id)
        nodes.append(n)

    result = 'successful initialized idle 50 nodes'
    node_list = [(node.name,node.id) for node in nodes]
    return jsonify({'result': result, "node_list": node_list})


@app.route('/cloudproxy/nodels/')
def cloud_node_ls():
    all_nodes = []
    for node in nodes:
        all_nodes.append({"name":node.name,"id": node.id, "status": node.container_status})

    return jsonify({"all_nodes":all_nodes})

@app.route('/cloudproxy/dashboard/')
def cloud_dashboard():
    all_nodes = []
    for node in nodes:
        all_nodes.append({"name":node.name,"id": node.id, "status": node.container_status})

    headings = ("Name", "ID", "Status")

    return render_template('main.html', all_nodes=all_nodes, headings = headings)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)


