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


### TODO

- [ ] `config.yaml` parameter documentation
- [ ] scheduler web-api documentation
