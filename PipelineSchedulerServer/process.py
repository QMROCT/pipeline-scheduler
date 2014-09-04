__author__ = 'Christoph Jansen, HTW Berlin'

import types
from threading import Thread
from tasks.xnat import XNATPipeline

class ProcessHandler:

    tasks = {'xnat': XNATPipeline}

    def __init__(self, applicationConfig, taskHandler, cloudHandler, ssh):
        self.applicationConfig = applicationConfig
        self.taskHandler = taskHandler
        self.cloudHandler = cloudHandler
        self.ssh = ssh

    def postTask(self, input):
        if(input == None):
            return {'request': 'error', 'content': 'input is missing'}
        elif type(input) is types.DictType:
            return self._registerTask(input)
        elif type(input) is types.ListType:
            return self._registerTasks(input)
        else:
            return {'request': 'error', 'content': 'accepts dict or list of dicts'}

    def _registerTasks(self, input):
        request = 'success'
        results = []
        for i in list(input):
            result = self._startTask(i)
            if(result['status'] != 'queued'):
                request = 'error'
            results.append(result)
        return {'request': request, 'content': results}

    def _registerTask(self, input):
        result = self._startTask(input)
        if(result['status'] != 'queued'):
            return {'request': 'error', 'content': result}

        return {'request': 'success', 'content': result}

    def _startTask(self, input):
        task = self._generateTask(input)
        if(task == None):
            return {'status' : 'error', 'content': 'could not register task'}

        self.taskHandler.registerTask(task)
        t = Thread(target=self._processTasks)
        t.start()
        return {'status':'queued', 'task': task.__dict__}

    def _processTasks(self):
        while(self._processTask()):
            pass

    def _processTask(self):
        task = self.taskHandler.nextTaskForProcessing()

        if(task == None):
            return False

        if(self._executeTask(task)):
            self.taskHandler.releaseTask(task)
        else:
            self.taskHandler.releaseTask(task)
            # maybe enqueue again
            return False

        return True

    def _generateTask(self, input):
        if(not type(input) is types.DictType):
            print 'task must be dict'
            return None
        t = input.get('type')
        if(t == None):
            print 'task must contain parameter type'
            return None
        taskClass = self.tasks.get(t)
        if(taskClass == None):
            print t + ' is not a possible task class'
            return None
        task = taskClass.__init__(input)
        if(not taskClass.check()):
            return None
        return task


    def _executeTask(self, task):
        print 'start task: ' + task.id

        server = self.cloudHandler.retrieveServer()
        if(server == None):
            return False

        sshClient = self.ssh.connect(server.ip)
        if(sshClient == None):
            return False

        localScriptsFolder = self.applicationConfig.LOCAL_SCRIPTS_FOLDER
        remoteBaseFolder = self.applicationConfig.REMOTE_BASE_FOLDER

        files = task.getFiles()
        command = task.getCommand(remoteBaseFolder)

        self.ssh.uploadFiles(sshClient, files, localScriptsFolder, remoteBaseFolder)
        self.ssh.executeCommand(sshClient, command)

        self.ssh.disconnect()

        self.cloudHandler.releaseServer(server)

        print 'end task: ' + task.id
        return True