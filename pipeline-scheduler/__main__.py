__author__ = 'Christoph Jansen, HTW Berlin'

from configuration import ApplicationHandler
from flask import Flask, request
from json import dumps
app = Flask(__name__)

applicationHandler = ApplicationHandler()

@app.route('/', methods=['GET'])
def getRoot():
    return dumps({'request': 'success', 'content': 'server active'}, indent=4)

@app.route('/pipeline', methods=['POST'])
def postPipeline():
    return dumps(applicationHandler.pipelineHandler.postPipeline(request.get_json()), indent=4)

@app.route('/pipeline', methods=['GET'])
def getPipeline():
    return dumps(applicationHandler.pipelineHandler.getPipeline(request.get_json()), indent=4)

@app.route('/pipeline', methods=['DELETE'])
def deletePipeline():
    return dumps({'request': 'error', 'content': 'unsupported operation'}, indent=4)

@app.route('/instance', methods=['GET'])
def getInstance():
    return dumps(applicationHandler.cloudHandler.getInstance(request.get_json()), indent=4)

@app.route('/instance', methods=['DELETE'])
def deleteInstance():
    return dumps(applicationHandler.cloudHandler.deleteInstance(), indent=4)

@app.route('/config', methods=['PUT'])
def putConfig():
    return dumps(applicationHandler.putConfig(), indent=4)

@app.route('/config', methods=['GET'])
def getConfig():
    return dumps(applicationHandler.getConfig(), indent=4)

@app.route('/error', methods=['POST'])
def postError():
    return dumps({'request': 'error', 'content': 'unsupported operation'}, indent=4)

if __name__ == '__main__':
    app.run(host=applicationHandler.config.HOST, port=applicationHandler.config.PORT)