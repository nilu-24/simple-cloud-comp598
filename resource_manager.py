from flask import Flask, jsonify, request, render_template
import pycurl
import json
from io import BytesIO
from operator import itemgetter
import re

#creating the cluster which is a list of pods
cluster = []

class Cluster:
    def __init__(self, cluster_name):
        self.cluster_name = cluster_name
        self.pods = []
class Pod:
    def __init__(self, pod_name="default", pod_id = "some_id"):
        self.pod_name = pod_name
        self.nodes = []
        self.number_of_nodes = 0
        self.pod_id = pod_id

        if pod_name=="default":
            self.number_of_nodes = 50

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
proxy_url = 'http://10.122.18.226:6000/'


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




@app.route('/cloud/jobs/launch/', methods=['POST','GET'])
def cloud_launch():
    if request.method == 'POST':
        print('Client is posting a file')
        job_file = request.files['file']
        print(job_file.read())
        #TODO:logic for invoking RM-Proxy
    elif request.method == 'GET':
            cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/jobs/launch/')
            cURL.perform()

    result = 'job posted to cloud successfully'
    return jsonify ({'result': result})


@app.route('/cloud/podls/')
def cloud_pod_ls():
    
    return jsonify([{"pod_name":pod.pod_name,"pod_id": pod.pod_id, "number_of_nodes": pod.number_of_nodes} for pod in cluster])



@app.route('/cloud/pod_register/<name>')
def pod_register(name):
    result = ""
    if request.method == 'GET':
        print("adding pod to main cluster")
        for pod in cluster:
            if pod.pod_name == name:
                result = "pod already exists"

        if result!="pod already exists":
            new_pod = Pod(pod_name=name)
            cluster.append(new_pod)
            result = 'successfully added pod to cluster'

        return jsonify ({'result': result})


@app.route('/cloud/pod_rm/<name>')
def cloud_pod_rm(name):

    if name == "default":
        return jsonify ({'result': "cannot remove default pod"}) 

    if request.method == 'GET':
        print("removing pod from main cluster")
        result = 'cannot remove non-existing pod'
        for pod in cluster:
            if pod.pod_name == name:
                cluster.remove(pod)
                result = "successfully removed pod from cluster"

        return jsonify ({'result': result})


@app.route('/cloud/init/')
def cloud_init():
    cURL.setopt(cURL.URL, proxy_url + '/cloudproxy/init/')
    cURL.perform()
    result = 'success'
    cluster.append(Pod())
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
    all_nodes = sorted(all_nodes, key=itemgetter('name'))
    headings = ("Name", "ID", "Status")

    return render_template('main.html', all_nodes=all_nodes, headings=headings)



@app.route('/could/abort/<jobid>')
def cloud_abort(jobid):
    pass
        


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
