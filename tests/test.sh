#!/bin/bash

bash /vagrant/pipeline-scheduler/tests/script.sh -session "SampleSession" -subject "SampleSubject" -project "SampleProject" -xnatID "SampleID" -host "http://xnat:8080/xnat/" -user "admin" -pwd "admin" -script "test.sh" -type "xnat"
