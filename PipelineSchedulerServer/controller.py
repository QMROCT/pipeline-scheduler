__author__ = 'Christoph Jansen, HTW Berlin'

from helper import loadConfigurationFile
from task import TaskHandler
from process import ProcessHandler
from cloud import CloudHandler
from connectors.nova import Nova
from ssh import SSH
import sys


class ApplicationController:

    connectors = {'nova': Nova}

    def __init__(self):
        applicationConfig = self.ApplicationConfiguration()
        if(not applicationConfig.check()):
            sys.exit(1)

        connectorClass = self.connectors.get(applicationConfig.CONNECTOR)
        if(connectorClass == None):
            print applicationConfig.CONNECTOR + ' is not a possible connector class'
            sys.exit(1)

        connector = connectorClass(applicationConfig)
        if(not connector.check()):
            sys.exit(1)

        ssh = SSH()
        if(not ssh.check()):
            sys.exit(1)

        self.applicationConfig = applicationConfig
        self.taskHandler = TaskHandler(applicationConfig=applicationConfig)
        self.cloudHandler = CloudHandler(applicationConfig=applicationConfig, connector=connector)
        self.processHandler = ProcessHandler(applicationConfig=applicationConfig, taskHandler=self.taskHandler, cloudHandler=self.cloudHandler, ssh=ssh)

        # remove existing virtual servers
        self.cloudHandler.deleteServersUntracked()

    def getConfig(self):
        return {'request': 'success', 'content': [self.applicationConfig.__dict__, self.processHandler.ssh.sshConfig.__dict__, self.cloudHandler.connector.getConfig()]}

    def putConfig(self):
        if(self._update()):
            return self.getConfig()
        else:
            return {'request': 'error', 'content': 'could not update config'}

    def _update(self):
        applicationConfig = self.ApplicationConfiguration()
        if(not self.applicationConfig.check()):
            return False

        connectorClass = self.connectors.get(applicationConfig.CONNECTOR)
        if(connectorClass == None):
            return False

        connector = connectorClass.__init__(applicationConfig=applicationConfig)
        if(not connector.check()):
            return False

        ssh = SSH()
        if(not ssh.check()):
            return False

        self.applicationConfig = applicationConfig
        self.taskHandler.applicationConfig = applicationConfig
        self.cloudHandler.applicationConfig = applicationConfig
        self.cloudHandler.connector = connector
        self.processHandler.applicationConfig = applicationConfig
        self.processHandler.ssh = ssh

        return True


    class ApplicationConfiguration:
        def __init__(self):
            parameters = loadConfigurationFile('application')
            self.MAX_ACTIVE_TASKS = parameters.get('MAX_ACTIVE_TASKS', 1)
            self.VIRTUAL_SERVER_TTL = parameters.get('VIRTUAL_SERVER_TTL', 1)
            self.CONNECTOR = parameters.get('CONNECTOR', 'nova')
            self.LOCAL_SCRIPTS_FOLDER = parameters.get('LOCAL_SCRIPTS_FOLDER')
            self.REMOTE_BASE_FOLDER = parameters.get('REMOTE_BASE_FOLDER')
            self.TIMETEST_CSV_FILE = parameters.get('TIMETEST_CSV_FILE')
            self.HOST = parameters.get('HOST')
            self.PORT = parameters.get('PORT')

        def check(self):
            message = 'missing parameter in application.yaml: '
            if(self.LOCAL_SCRIPTS_FOLDER == None):
                print message + 'LOCAL_SCRIPTS_FOLDER'
                return False
            if(self.REMOTE_BASE_FOLDER == None):
                print message + 'IMAGE_BASE_FOLDER'
                return False
            if(self.HOST == None):
                print message + 'HOST'
                return False
            if(self.PORT == None):
                print message + 'PORT'
                return False
            return True