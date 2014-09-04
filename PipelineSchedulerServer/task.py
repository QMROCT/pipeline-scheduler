__author__ = 'Christoph Jansen, HTW Berlin'

import types
from thread import allocate_lock
from Queue import Queue

class TaskHandler:

    lock = allocate_lock()
    queuedTasks = Queue()
    activeTasks = {}

    def __init__(self, applicationConfig):
        self.applicationConfig = applicationConfig

    def registerTask(self, task):
        self.lock.acquire()
        self.queuedTasks.put(task)
        self.lock.release()

    def nextTaskForProcessing(self):
        self.lock.acquire()
        if (len(self.activeTasks) >= self.applicationConfig.MAX_ACTIVE_TASKS or self.queuedTasks.empty()):
            self.lock.release()
            return None
        task = self.queuedTasks.get()
        self.activeTasks[task.id] = task
        self.lock.release()
        return task

    def releaseTask(self, task):
        self.lock.acquire()
        del self.activeTasks[task.id]
        self.lock.release()

    def getTasks(self, input):
        if(input == None):
            return self._listTasks()
        elif type(input) is types.ListType:
            return self._listTasksByIDs(input)
        else:
            return {'request': 'error', 'content': 'accepts empty input or list of IDs'}

    def _listTasks(self):
        self.lock.acquire()
        active = []
        for k, v in self.activeTasks.items():
            active.append(v.__dict__())
        queued = []
        for i in list(self.queuedTasks.queue):
            queued.append(i.__dict__())
        self.lock.release()
        return {'request': 'success', 'content': {'active': active, 'queued': queued}}

    def _listTasksByIDs(self, input):
        results = []
        for id in input:
            result = self._taskByID(id)
            if(result != None):
                results.append(result)

        return {'request': 'success', 'content': results}

    def _taskById(self, id):
        self.lock.acquire()
        for k, v in self.activeTasks.items():
            if k == id:
                self.lock.release()
                return {'status': 'active', 'pipeline': v.__dict__()}

        for i in list(self.queuedTasks.queue):
            if i.id == id:
                self.lock.release()
                return {'status': 'queued', 'pipeline': i.__dict__()}

        self.lock.release()
        return None