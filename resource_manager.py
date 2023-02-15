from flask import Flask, jsonify, request, render_template
import pycurl
import json
from io import BytesIO
import re

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
            


cURL = pycurl.Curl()
proxy_url = 'http://10.140.17.112:6000/'

app = Flask(__name__)

pods_dict = dict()



@app.route('/', methods=['GET', 'POST'])
def cloud():
    if request.method == 'GET':
        print('A client says hello')
        response = 'Cloud says hello!'
        return jsonify({'response': response})



@app.route('/cloud/nodes/<name>', defaults={'pod_name': 'default'})
@app.route('/cloud/nodes/<name>/<pod_name>')

def cloud_register(name, pod_name):
    if request.method == 'GET':
        print('Request to register node: ' + str(name) + ' on pod: ' + str(pod_name))
        #TODO: Management for pod_name (not for A1)
        #TODO: call proxy to register node
        data = BytesIO()

        cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/nodes/' + str(name))
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dictionary = json.loads(data.getvalue())
        print(dictionary)

        result = dictionary['result']
        node_status = dictionary['node_status']
        new_node_name = dictionary['node_name']
        new_node_pod = pod_name

        if pod_name in pods_dict:
            pods_dict[pod_name].add(name)
        else:
            pods_dict[pod_name] = set([name])

        return jsonify({'result': result, 'node_status': node_status, 'new_node_name':str(name), 'new_node_pod': new_node_pod})


@app.route('/cloud/rmnodes/<name>')
def cloud_rm_node(name):
    if request.method == 'GET':
        print('Request to remove node: ' + str(name))
        #TODO: Management for pod_name (not for A1)
        #TODO: call proxy to register node
        data = BytesIO()

        cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/rmnodes/' + str(name))
        cURL.setopt(cURL.WRITEFUNCTION, data.write)
        cURL.perform()
        dictionary = json.loads(data.getvalue())
        print(dictionary)

        result = dictionary['result']
        node_status = dictionary['node_status']
        

        return jsonify({'result': result, 'node_status': node_status})




@app.route('/cloud/jobs/launch', methods=['POST'])
def cloud_launch():
    if request.method == 'POST':
        print('Client is posting a file')
        job_file = request.files['file']
        print(job_file.read())
        #TODO:logic for invoking RM-Proxy
        result = 'success'
        return jsonify ({'result': result})


@app.route('/cloud/podls/')
def cloud_pod_ls():
    print(pods_dict)
    result = 'success'
    return jsonify ({'result': result})

@app.route('/cloud/init/')
def cloud_init():
    cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/init/')
    cURL.perform()
    result = 'success'
    return jsonify ({'result': result})

all_nodes = []

@app.route('/cloud/nodels/')
def cloud_node_ls(): 
    global all_nodes
    #return the nodes array from proxy
    data = BytesIO()

    cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/nodels/')
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dictionary = json.loads(data.getvalue())
    print(dictionary)

    result = "success"
    all_nodes = dictionary['all_nodes']
    all_nodes.sort(key=lambda x: int(re.search(r'\d+$', x['name']).group()))  # Sort by trailing digits

    return jsonify({'result': result, 'all_nodes': all_nodes})


@app.route('/cloud/dashboard/')
def cloud_dashboard():

    data = BytesIO()
    all_nodes = []
    cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/nodels/')
    cURL.setopt(cURL.WRITEFUNCTION, data.write)
    cURL.perform()
    dictionary = json.loads(data.getvalue())

    result = "success"
    all_nodes = dictionary['all_nodes']
    all_nodes.sort(key=lambda x: int(re.search(r'\d+$', x['name']).group()))  # Sort by trailing digits
    headings = ("Name", "ID", "Status")

    return render_template('main.html', all_nodes=all_nodes, headings=headings)



        


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
