__author__ = 'Christoph Jansen, HTW Berlin'

import yaml, sys, api, os, subprocess, math
from pipeline import PipelineHandler
from cloud import CloudHandler
from os.path import expanduser

class ApplicationHandler:

    def __init__(self):
        home = expanduser("~")
        self.CONFIG_PATH = home + '/.pipeline-scheduler/config.yaml'

        self.config = self.loadConfig()
        if(self.config == None):
            print 'error: could not read file ' + self.CONFIG_PATH
            sys.exit(1)
        if(not self.config.selfCheck):
            print 'error: config is incomplete'
            sys.exit(1)

        api = self.loadApi(self.config.API)
        if(api == None):
            print 'error: could not load api ' + self.config.API
            sys.exit(1)

        if(not api.selfCheck()):
            print 'error: api connection failed'
            sys.exit(1)

        self.api = api
        self.pipelineHandler = PipelineHandler(self)
        self.cloudHandler = CloudHandler(self)
        # delete all remaining instances
        self.cloudHandler.deleteInstance()

    def putConfig(self):
        config = self.loadConfig()
        if(config == None):
            return {'request': 'error', 'content': 'could not read file ' + self.CONFIG_PATH  + ', keeping old config'}
        if(not config.selfCheck):
            return {'request': 'error', 'content': 'config is incomplete, keeping old config'}
        api = self.loadApi(config.API)
        if(api == None):
            return {'request': 'error', 'content': 'could not load api ' + self.config.API + ', keeping old config'}
        if(not api.selfCheck()):
            return {'request': 'error', 'content': 'api connection failed, keeping old config'}
        self.config = config
        self.api = api
        return {'request': 'success', 'content': self.config.__dict__}

    def getConfig(self):
        return {'request': 'success', 'content': self.config.__dict__}

    def loadConfig(self):
        config = {}
        try:
            stream = open(self.CONFIG_PATH, 'r')
            doc = yaml.load(stream)
            stream.close()
        except:
            return None

        for k, v in doc.items():
            config[k] = v
        return Configuration(config)

    def loadApi(self, name):
        credentials = self.loadAuthentication()
        if(credentials == None):
            return None

        if(name.lower() == 'nova'):
            return api.Nova(self, credentials)

        return None

    def loadAuthentication(self):
        try:
            command = ['bash', '-c', 'source ' + self.config.OS_OPENRC_FILE + ' && env']

            proc = subprocess.Popen(command, stdout = subprocess.PIPE)

            for line in proc.stdout:
              (key, _, value) = line.partition("=")
              os.environ[key] = value

            proc.communicate()
        except:
            return None

        OS_AUTH_URL = os.environ.get('OS_AUTH_URL')
        OS_USERNAME = os.environ.get('OS_USERNAME')
        OS_PASSWORD = os.environ.get('OS_PASSWORD')
        OS_TENANT_NAME = os.environ.get('OS_TENANT_NAME')
        COMPUTE_API_VERSION = os.environ.get('COMPUTE_API_VERSION')

        if(OS_AUTH_URL == None or OS_USERNAME == None or OS_PASSWORD == None or OS_TENANT_NAME == None or COMPUTE_API_VERSION == None):
            return None


        COMPUTE_API_VERSION = float(COMPUTE_API_VERSION)
        if(COMPUTE_API_VERSION == math.floor(COMPUTE_API_VERSION)):
            COMPUTE_API_VERSION = int(COMPUTE_API_VERSION)
        COMPUTE_API_VERSION = str(COMPUTE_API_VERSION)

        credentials = {'username': OS_USERNAME, 'api_key':OS_PASSWORD, 'auth_url': OS_AUTH_URL, 'project_id': OS_TENANT_NAME, 'version': COMPUTE_API_VERSION}

        for k, v in credentials.items():
            if(v[-1:] == '\n'):
                credentials[k] = v[:-1]

        return credentials


class Configuration:

    def __init__(self, config):
        self.MAX_ACTIVE_PIPELINES = config.get('MAX_ACTIVE_PIPELINES')
        self.MAX_CONNECTION_RETRIES = config.get('MAX_CONNECTION_RETRIES')
        self.CONNECTION_RETRY_INTERVAL = config.get('CONNECTION_RETRY_INTERVAL')
        self.VM_INSTANCE_TTL = config.get('VM_INSTANCE_TTL')
        self.VM_IMAGE_ID = config.get('VM_IMAGE_ID')
        self.VM_KEYPAIR_NAME = config.get('VM_KEYPAIR_NAME')
        self.VM_PRIVATEKEY_FILE = config.get('VM_PRIVATEKEY_FILE')
        self.VM_PRIVATEKEY_PASSWORD = config.get('VM_PRIVATEKEY_PASSWORD')
        self.VM_FLAVOR = config.get('VM_FLAVOR')
        self.VM_USER = config.get('VM_USER')
        self.VM_SCRIPTS_FOLDER = config.get('VM_SCRIPTS_FOLDER')
        self.VM_NETWORK_ID = config.get('VM_NETWORK_ID')
        self.API = config.get('API')
        self.OS_SECURITY_GROUP = config.get('OS_SECURITY_GROUP')
        self.OS_USE_FLOATING_IP = config.get('OS_USE_FLOATING_IP')
        self.OS_IP_POOL = config.get('OS_IP_POOL')
        self.OS_OPENRC_FILE = config.get('OS_OPENRC_FILE')
        self.LOCAL_SCRIPTS_FOLDER = config.get('LOCAL_SCRIPTS_FOLDER')
        self.TIMEDIFF_CSV = config.get('TIMEDIFF_CSV')
        self.HOST = config.get('HOST')
        self.PORT = config.get('PORT')

    def selfCheck(self):
        if(self.OS_USE_FLOATING_IP == None or self.LOCAL_SCRIPTS_FOLDER == None or self.CONNECTION_RETRY_INTERVAL == None or self.MAX_CONNECTION_RETRIES == None or self.VM_SCRIPTS_FOLDER == None or self.OS_SECURITY_GROUP == None or self.VM_USER == None or self.MAX_ACTIVE_PIPELINES == None or self.VM_INSTANCE_TTL == None or self.VM_IMAGE_ID == None or self.VM_FLAVOR == None or self.API == None or self.OS_OPENRC_FILE == None or self.HOST == None or self.PORT == None):
            return False

        return True