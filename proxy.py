from flask import Flask, jsonify, request, render_template

import docker

client = docker.from_env()


app = Flask(__name__)



nodes = []
jobs = [] #queue

class Cluster:
    def __init__(self, cluster_name):
        self.cluster_name = cluster_name
        self.pods = []
class Pod:
    def __init__(self, pod_name):
        self.pod_name = pod_name
        self.nodes = []

#creating classes for Node
class Node:
    '''
Each node will have a specific CPU, memory, and storage limit factor.
You need to make these factors as configurable parameters in the simple cloud implementation so we can configure the type of nodes – thin, medium, large nodes.
    '''

    def __init__(self, name, job_status=None, container=None,id=None, container_status="Idle", curr_job=None, cpu=None, limit=None, memory=None):
        self.id = id
        self.name = name
        self.container_status = container_status
        self.job_status = job_status
        self.logs = []
        self.curr_job = curr_job
        self.container = container


        # idle
        #start job
        # running
        #as soon as job done reset to idle


        # def check_if_ended():
        #     if self.container.exec_inspect not None:
        #         self.status = "Job done"



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

import concurrent.futures

@app.route('/cloudproxy/init/')
def cloud_init():

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_container = {}
        for i in range(50):
            container_name = f"node{i+1}"
            future_to_container[executor.submit(check_or_create_container, container_name)] = container_name
            print(f'Submitted task to check or create container {container_name}')

        for future in concurrent.futures.as_completed(future_to_container):
            container_name = future_to_container[future]
            c = future.result()
            if c:
                n = Node(name=container_name, container=c, id=c.id)
                nodes.append(n)
                print(f'Successfully created or restarted container {container_name}')
            else:
                print(f'Container check or creation failed for {container_name}')
                
    # Sort the list of nodes by name
    sorted_nodes = sorted(nodes, key=lambda node: node.name)
    
    result = 'successfully initialized idle 50 nodes'
    node_list = [(node.name, node.id) for node in sorted_nodes]
    print(f'Node list: {node_list}')
    return jsonify({'result': result, "node_list": node_list})

def check_or_create_container(container_name):
    # Check if container already exists
    existing_containers = client.containers.list(filters={"name": container_name})
    if existing_containers:
        existing_container = existing_containers[0]
        if existing_container.status == "running":
            # Restart the existing container
            existing_container.restart()
            print(f'Restarted container {container_name}')
            return existing_container
        else:
            # Start the existing container
            existing_container.start()
            print(f'Started container {container_name}')
            return existing_container
    else:
        # Create a new container
        c = client.containers.run('alpine', 'ash', detach=True, tty=True, name=container_name)
        print(f'Created container {container_name}')
        return c



@app.route('/cloudproxy/nodels/')
def cloud_node_ls():
    # Create a set of node names to remove duplicates
    node_names = set()
    all_nodes = []
    for node in nodes:
        # Check if the node name is already in the set of node names
        if node.name not in node_names:
            # Add the node name to the set of node names
            node_names.add(node.name)
            # Add the node dictionary to the list of all nodes
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

