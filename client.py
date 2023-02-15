import pycurl
import sys
import os
import requests

cURL = pycurl.Curl()

init_check = False

def cloud_hello(url):
    if init_check:
        cURL.setopt(cURL.URL, url)
        cURL.perform()

def cloud_init(url):
    global init_check
    init_check = True
    cURL.setopt(cURL.URL, url + '/cloud/init/')
    cURL.perform()


def cloud_register(url, command):
    if init_check:
        command_list = command.split()
        if len(command_list) == 3:
            cURL.setopt(cURL.URL, url + '/cloud/nodes/' + command_list[2])
            cURL.perform()
        elif len(command_list) == 4:
            cURL.setopt(cURL.URL, url + '/cloud/nodes/' + command_list[2] + '/' + command_list[3])
            cURL.perform()
  


def cloud_rm_node(url, command):
    if init_check:
        command_list = command.split()
        if len(command_list) == 3:
            cURL.setopt(cURL.URL, url + '/cloud/rmnodes/' + command_list[2])
            cURL.perform()



def cloud_launch(url, command):
    if init_check:
        command_list = command.split()
        if len(command_list) == 3:
            file_path = command_list[2]
            if os.path.isfile(file_path):
                files = {'file': open(file_path, 'rb')}
                ret = requests.post(url + '/cloud/jobs/launch', files=files)
                print(ret.text)


def cloud_pod_ls(url, command):
    if init_check:
        command_list = command.split()
        if len(command_list) == 3:
            cURL.setopt(cURL.URL, url + '/cloud/podls/')
            cURL.perform()

def cloud_node_ls(url):
    if init_check:
        cURL.setopt(cURL.URL, url + '/cloud/nodels/')
        cURL.perform()


def main():
    rm_url = sys.argv[1]
    while(1):
        command = input('$ ')
        if command == 'cloud hello':
            cloud_hello(rm_url)
        elif command.startswith('cloud register'):
            cloud_register(rm_url, command)
        elif command.startswith('cloud launch'):
            cloud_launch(rm_url, command)
        elif command.startswith('cloud rm'):
            cloud_rm_node(rm_url, command)
        elif command.startswith('cloud pod ls'):
            cloud_pod_ls(rm_url, command)
        elif command.startswith('cloud init'):
            cloud_init(rm_url)

        elif command.startswith('cloud node ls'):
            cloud_node_ls(rm_url)

if __name__ == '__main__':
    main()


