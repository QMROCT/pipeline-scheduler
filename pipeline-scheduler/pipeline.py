__author__ = 'Christoph Jansen, HTW Berlin'

import types
from thread import allocate_lock
from threading import Thread
from Queue import Queue
from time import time
from uuid import uuid4

class PipelineHandler:

    def __init__(self, applicationHandler):
         self.applicationHandler = applicationHandler

    lock = allocate_lock()
    queuedPipelines = Queue()
    activePipelines = {}

    def postPipeline(self, input):
        if(input == None):
            return {'request': 'error', 'content': 'input is missing'}
        elif type(input) is types.DictType:
            return self._registerPipeline(input)
        elif type(input) is types.ListType:
            return self._registerPipelines(input)
        else:
            return {'request': 'error', 'content': 'accepts dict or list of dicts'}

    def _registerPipelines(self, input):
        request = 'success'
        results = []
        for i in list(input):
            result = self._startPipeline(i)
            if(result['status'] != 'queued'):
                request = 'error'
            results.append(result)
        return {'request': request, 'content': results}

    def _registerPipeline(self, input):
        result = self._startPipeline(input)
        if(result['status'] != 'queued'):
            return {'request': 'error', 'content': result}

        return {'request': 'success', 'content': result}

    def _startPipeline(self, input):
        pipeline = self._generatePipeline(input)
        if(pipeline == None):
            return {'status' : 'incomplete', 'content': 'requires parameters project, subject, session, xnatid, host, user, pwd'}

        self.queuedPipelines.put(pipeline)
        t = Thread(target=self._processPipelines)
        t.start()
        return {'status':'queued', 'pipeline': pipeline.__dict__}

    def _generatePipeline(self, input):
        project = input.get('project')
        subject = input.get('subject')
        session = input.get('session')
        host = input.get('host')
        user = input.get('user')
        pwd = input.get('pwd')
        script = input.get('script')

        if(project != None and subject != None and session != None and host != None and user != None and pwd  != None and script != None):
            return Pipeline(project, subject, session, host, user, pwd, script)

    def _processPipelines(self):
        while(self._processPipeline()):
            pass

    def _processPipeline(self):
        pipeline = None

        self.lock.acquire()
        if(len(self.activePipelines) < self.applicationHandler.config.MAX_ACTIVE_PIPELINES and not self.queuedPipelines.empty()):
            pipeline = self.queuedPipelines.get()
            self.activePipelines[pipeline.id] = pipeline
        self.lock.release()

        if(pipeline != None):
            print 'start pipeline ', pipeline.id

            # TODO: None must be handled
            result = self.applicationHandler.cloudHandler.runTask(pipeline)

            self.lock.acquire()
            del self.activePipelines[pipeline.id]
            self.lock.release()

            print 'end pipeline ', pipeline.id
            return True

        return False

    def getPipeline(self, input):
        if(input == None):
            return self._listPipelines()
        elif type(input) is types.DictType:
            return self._listPipelineByInput(input)
        elif type(input) is types.ListType:
            return self._listPipelinesByInput(input)
        else:
            return {'request': 'error', 'content': 'accepts empty input or dict or list of dicts'}

    def _listPipelines(self):
        self.lock.acquire()
        active = []
        for k, v in self.activePipelines.items():
            active.append(v.__dict__)
        queued = []
        for i in list(self.queuedPipelines.queue):
            queued.append(i.__dict__)
        self.lock.release()
        return {'request': 'success', 'content': {'active': active, 'queued': queued}}

    def _listPipelinesByInput(self, input):
        results = []
        for i in input:
            id = i.get('id')
            if id != None:
                result = self._pipelineById(id)
                if(result != None):
                    results.append(result)
        if len(results) == 0:
            return {'request': 'error', 'content': 'no id found'}

        return {'request': 'success', 'content': results}

    def _listPipelineByInput(self, input):
        id = input.get('id')
        if id == None:
            return {'request': 'error', 'content': 'requires parameter id'}
        pipeline = self._pipelineById(id)
        if pipeline == None:
            return {'request': 'error', 'content': 'id not found'}

        return {'request': 'success', 'content': pipeline}


    def _pipelineById(self, id):
        self.lock.acquire()
        for k, v in self.activePipelines.items():
            if k == id:
                self.lock.release()
                return {'status': 'active', 'pipeline': v.__dict__}

        for i in list(self.queuedPipelines.queue):
            if i.id == id:
                self.lock.release()
                return {'status': 'queued', 'pipeline': i.__dict__}

        self.lock.release()
        return None

class Pipeline:

    def __init__(self, project, subject, session, host, user, pwd, script):
        self.project = project
        self.subject = subject
        self.session = session
        self.host = host
        self.user = user
        self.pwd = pwd
        self.script = script
        self.id = str(uuid4())
        self.timestamp = time()