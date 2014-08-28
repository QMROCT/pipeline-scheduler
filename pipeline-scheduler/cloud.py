__author__ = 'Christoph Jansen, HTW Berlin'

import types, paramiko, traceback, os.path
from Queue import Queue
from thread import allocate_lock
from time import time, sleep

class CloudHandler:

    LOCAL_SCRIPTS_FOLDER = "scripts"

    def __init__(self, applicationHandler):
        self.applicationHandler = applicationHandler

    activeInstances = {}
    queuedInstances = Queue()

    lock = allocate_lock()

    def __init__(self, applicationHandler):
        self.applicationHandler = applicationHandler

    def runTask(self, pipeline):
        print 'start task'

        config = self.applicationHandler.config

        timediff = TimeDiff()
        timediff.instanceStart = time() - pipeline.timestamp

        instance = self._retrieveInstance(pipeline)
        if(instance == None):
            return None

        timediff.instanceUp = time() - pipeline.timestamp

        ssh = self._sshConnect(instance)
        if(ssh == None):
            return None

        localScript = self.LOCAL_SCRIPTS_FOLDER + '/' + pipeline.script
        remoteScript = config.VM_SCRIPTS_FOLDER + '/' + pipeline.script

        sftp = ssh.open_sftp()
        sftp.put(localScript, remoteScript)
        sftp.close()

        params = ' -project ' + pipeline.project + ' -subject ' + pipeline.subject + ' -session ' + pipeline.session + ' -host ' + pipeline.host + ' -user ' + pipeline.user + ' -pwd ' + pipeline.pwd
        command = 'bash ' + remoteScript + params

        timediff.processingStart = time() - pipeline.timestamp

        stdin, stdout, sterr = ssh.exec_command(command)
        channel = stdout.channel
        status = channel.recv_exit_status()

        timediff.processingDone = time() - pipeline.timestamp

        ssh.close()

        self._releaseInstance(instance)

        timediff.instanceDown = time() - pipeline.timestamp
        timediff.writeDataToCSV(config.TIMEDIFF_CSV)

        print 'end task'
        return None

    def deleteInstance(self):
        instances = []
        for k, v in self.activeInstances.items():
            instances.append(v)
        for i in list(self.queuedInstances.queue):
            instances.append(i)
        if(self.applicationHandler.api.deleteAllInstancesExcept(instances)):
            return {'request': 'success', 'content': 'deleted all untracked vm instances'}
        return {'request': 'error', 'content': 'unexpected problem with api connection'}

    def _retrieveInstance(self, pipeline):
        self.lock.acquire()
        if(not self.queuedInstances.empty()):
            instance = self.queuedInstances.get()
            self.activeInstances[instance.id] = instance
            instance.associatedPipeline = pipeline.id
            self.lock.release()
            return instance
        self.lock.release()

        instance = self.applicationHandler.api.createInstance()
        if(instance == None):
            return None

        ssh = self._sshConnect(instance)
        if(ssh == None):
            return None

        ssh.close()

        self.lock.acquire()
        instance.associatedPipeline = pipeline.id
        self.activeInstances[instance.id] = instance
        self.lock.release()
        return instance

    def _sshConnect(self, instance):

        config = self.applicationHandler.config
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ip = instance.ip
        username = config.VM_USER
        keyfile = config.VM_PRIVATEKEY_FILE
        keypass = config.VM_PRIVATEKEY_PASSWORD

        print 'ssh connect ' + str(ip) + ' ...'
        ready = False
        counter = 0

        while not ready:
            if(counter > config.MAX_CONNECTION_RETRIES):
                print 'connection refused'
                return None
            try:
                ssh.connect(ip, username=username, password=keypass, key_filename=keyfile)
                ready = True
            except:
                counter += 1
                #traceback.print_exc()
                sleep(config.CONNECTION_RETRY_INTERVAL)
                #print 'retry ' + str(counter)

        print 'connection successful'

        return ssh

    def _releaseInstance(self, instance):
        instance.timeToLive = instance.timeToLive - 1
        if(instance.timeToLive < 1):
            self.applicationHandler.api.deleteInstance(instance)
            self.lock.acquire
            del self.activeInstances[instance.id]
            self.lock.release
        else:
            self.lock.acquire
            instance.associatedPipeline = None
            self.queuedInstances.put(instance)
            del self.activeInstances[instance.id]
            self.lock.release

    def getInstance(self, input):
        if(input == None):
            return self._listInstances()
        elif type(input) is types.DictType:
            return self._listInstanceByInput(input)
        elif type(input) is types.ListType:
            return self._listInstancesByInput(input)
        else:
            return {'request': 'error', 'content': 'accepts empty input, dict or list of dicts'}

    def _listInstances(self):
        self.lock.acquire()
        active = []
        for k, v in self.activeInstances.items():
            active.append(v.__dict__)
        queued = []
        for i in list(self.queuedInstances.queue):
            queued.append(i.__dict__)
        self.lock.release()
        return {'request': 'success', 'content': {'active': active, 'queued': queued}}

    def _listInstancesByInput(self, input):
        results = []
        for i in input:
            id = i.get('id')
            if id != None:
                result = self._instanceById(id)
                if(result != None):
                    results.append(result)
        if len(results) == 0:
            return {'request': 'error', 'content': 'no id found'}

        return {'request': 'success', 'content': results}

    def _listInstanceByInput(self, input):
        id = input.get('id')
        if id == None:
            return {'request': 'error', 'content': 'requires parameter id'}
        instance = self._instanceByName(id)
        if instance == None:
            return {'request': 'error', 'content': 'id not found'}

        return {'request': 'success', 'content': instance}


    def _instanceById(self, id):
        self.lock.acquire()
        for k, v in self.activeInstances.items():
            if k == id:
                self.lock.release()
                return {'status': 'active', 'instance': v.__dict__}

        for i in list(self.queuedInstances.queue):
            if i.id == id:
                self.lock.release()
                return {'status': 'queued', 'instance': i.__dict__}

        self.lock.release()
        return None

class Instance:

    def __init__(self, id, name, ip, timeToLive, associatedPipeline):
        self.id = id
        self.name = name
        self.ip = ip
        self.timeToLive = timeToLive
        self.associatedPipeline = associatedPipeline
        self.timestamp = time()

class TimeDiff:

    def __init__(self):
        self.instanceStart = None
        self.instanceUp = None
        self.processingStart = None
        self.processingDone = None
        self.instanceDown = None

    def writeDataToCSV(self, filePath):
        if(filePath == None):
            return
        if(not os.path.isfile(filePath)):
            self._initializeCSV(filePath)
        s = '\n' + str(self.instanceStart) + ';' + str(self.instanceUp) + ';' + str(self.processingStart) + ';' + str(self.processingDone) + ';' + str(self.instanceDown)
        with open(filePath, 'a') as f:
            f.write(s)

    def _initializeCSV(self, filePath):
        s = 'instanceStart;instanceUp;processingStart;processingDone;instanceDown'
        with open(filePath, 'w') as f:
            f.write(s)