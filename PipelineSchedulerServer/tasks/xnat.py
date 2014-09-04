__author__ = 'Christoph Jansen, HTW Berlin'#

import types
from uuid import uuid4
from time import time
from abstract import ATask

class XNATPipeline(ATask):

    def __init__(self, parameters):
        self.project = parameters.get('project')
        self.subject = parameters.get('subject')
        self.session = parameters.get('session')
        self.host = parameters.get('host')
        self.user = parameters.get('user')
        self.pwd = parameters.get('pwd')
        self.files = parameters.get('files')
        self.script = parameters.get('script')
        self.id = str(uuid4())
        self.timestamp = time()

    def check(self):
        if(self.project == None or self.subject == None or self.session == None or self.host == None or self.user == None or self.pwd == None or self.script == None):
            print 'missing parameter in XNATPipeline'
            return False
        return True

    def getFiles(self):
        result = [self.script]
        if(self.files != None and type(self.files) is types.ListType and not self.files.empty()):
            result += self.files
        return result

    def getCommand(self, remoteBaseFolder):
        return 'bash ' + remoteBaseFolder + '/' + self.script + ' -project ' + self.project + ' -subject ' + self.subject + ' -session ' + self.session + ' -host ' + self.host + ' -user ' + self.user + ' -pwd ' + self.pwd

    def __dict__(self):
        return {'project': self.project, 'subject': self.subject, 'session': self.session, 'host': self.host, 'user': self.user, 'pwd': '***', 'id': self.id, 'timestamp': self.timestamp}