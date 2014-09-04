#!/bin/bash

NUM_OF_TESTS=20
GATEWAY="127.0.0.1:8100"

session="SampleSession"
subject="SampleSubject"
project="SampleProject"
user="admin"
pwd="admin"
host="xnat:8080/xnat"
script="test.sh"
type="xnat"

if [ -z ${CURL_CACERT} ] || [ ! -f ${CURL_CACERT} ]; then
	CURL_CACERT="-k"
else
	CURL_CACERT="--cacert ${CURL_CACERT}"
fi

p='{"project":"'${project}'","subject":"'${subject}'","session":"'${session}'","host":"'${host}'","user":"'${user}'","pwd":"'${pwd}'","script":"'${script}'","type":"'${type}'"}'
list=[
for i in $(seq 1 1 ${NUM_OF_TESTS}); do
	list=${list}${p}
	if [ ${i} -ne ${NUM_OF_TESTS} ]; then
		list=${list},
	fi
done
list=${list}]


curl ${CURL_CACERT} -X POST -H 'Content-Type: application/json' -d  ''$list'' "${GATEWAY}/tasks"
