__author__ = 'Christoph Jansen, HTW Berlin'

from controller import ApplicationController
from flask import Flask, request
from json import dumps
app = Flask(__name__)

applicationController = ApplicationController()

@app.route('/', methods=['GET'])
def getRoot():
    return dumps({'request': 'success', 'content': 'A cloudy day!'}, indent=4)

@app.route('/tasks', methods=['POST'])
def postTask():
    return dumps(applicationController.processHandler.postTasks(request.get_json()), indent=4)

@app.route('/tasks', methods=['GET'])
def getTasks():
    return dumps(applicationController.taskHandler.getTasks(request.get_json()), indent=4)

@app.route('/servers', methods=['GET'])
def getServers():
    return dumps(applicationController.cloudHandler.getServers(request.get_json()), indent=4)

@app.route('/servers/untracked', methods=['DELETE'])
def deleteServersUntracked():
    return dumps(applicationController.cloudHandler.deleteServersUntracked(), indent=4)

@app.route('/config', methods=['PUT'])
def putConfig():
    return dumps(applicationController.putConfig(), indent=4)

@app.route('/config', methods=['GET'])
def getConfig():
    return dumps(applicationController.getConfig(), indent=4)

if __name__ == '__main__':
    app.run(host=applicationController.applicationConfig.HOST, port=applicationController.applicationConfig.PORT)