## Pipeline Scheduler

[Flask](http://flask.pocoo.org/) server to schedule and process [XNAT](http://www.xnat.org/) pipelines with [OpenStack](http://www.openstack.org/).


### Installation

```bash
mkdir ~/.pipeline-scheduler
cp config.yaml.template ~/.pipeline-scheduler/config.yaml
# edit ~/.pipeline-scheduler/config.yaml
```

### Python Dependencies
* [Flask](http://flask.pocoo.org/)
* [Paramiko](http://www.paramiko.org/)
* [PyYAML](http://pyyaml.org/)
* [NovaClient](https://github.com/openstack/python-novaclient/)


### Server Start

```bash
python pipeline-scheduler
```


### Parameter Documentation: config.yaml

TODO

### Pipeline-Scheduler Web-API Documentation

Pipeline-Scheduler is controlled by sending requests to its Web-API. This Documentation describes the meaning of the URL paths and the supported HTTP functions. The Web-API accepts well formatted JSON objects, usually a Dictionary or a List of Dictionaries, and returns JSON objects. For the API functions cURL commands (Bash) are given as reference.



### Not yet implemented

* Advanced error handling
* Logging
* Seperate config files for different cloud APIs
* Source code documentation
* More Web-API functions
* OpenStack HEAT support
