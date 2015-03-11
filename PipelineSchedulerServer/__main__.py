__author__ = 'Christoph Jansen, HTW Berlin'

from controller import ApplicationController
from flask import Flask, request
from json import dumps
app = Flask(__name__)

applicationController = ApplicationController()

@app.route('/', methods=['GET'])
def getRoot():
    if not applicationController.tokenAuthenticator.authorize(request.args.get('token')):
        return dumps({'request': 'error', 'content': 'Do I know you?'}, indent=4)
    return dumps({'request': 'success', 'content': 'A cloudy day!'}, indent=4)

@app.route('/tasks', methods=['POST'])
def postTask():
    if not applicationController.tokenAuthenticator.authorize(request.args.get('token')):
        return dumps({'request': 'error', 'content': 'Do I know you?'}, indent=4)
    return dumps(applicationController.processHandler.postTasks(request.get_json()), indent=4)

@app.route('/tasks', methods=['GET'])
def getTasks():
    if not applicationController.tokenAuthenticator.authorize(request.args.get('token')):
        return dumps({'request': 'error', 'content': 'Do I know you?'}, indent=4)
    return dumps(applicationController.taskHandler.getTasks(request.get_json()), indent=4)

@app.route('/servers', methods=['GET'])
def getServers():
    if not applicationController.tokenAuthenticator.authorize(request.args.get('token')):
        return dumps({'request': 'error', 'content': 'Do I know you?'}, indent=4)
    return dumps(applicationController.cloudHandler.getServers(request.get_json()), indent=4)

@app.route('/servers/untracked', methods=['DELETE'])
def deleteServersUntracked():
    if not applicationController.tokenAuthenticator.authorize(request.args.get('token')):
        return dumps({'request': 'error', 'content': 'Do I know you?'}, indent=4)
    return dumps(applicationController.cloudHandler.deleteServersUntracked(), indent=4)

@app.route('/config', methods=['PUT'])
def putConfig():
    if not applicationController.tokenAuthenticator.authorize(request.args.get('token')):
        return dumps({'request': 'error', 'content': 'Do I know you?'}, indent=4)
    return dumps(applicationController.putConfig(), indent=4)

@app.route('/config', methods=['GET'])
def getConfig():
    if not applicationController.tokenAuthenticator.authorize(request.args.get('token')):
        return dumps({'request': 'error', 'content': 'Do I know you?'}, indent=4)
    return dumps(applicationController.getConfig(), indent=4)

if __name__ == '__main__':
    app.run(host=applicationController.applicationConfig.HOST, port=applicationController.applicationConfig.PORT)