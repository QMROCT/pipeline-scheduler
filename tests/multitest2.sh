#!/bin/bash

NUM_OF_TESTS=4

XNAT="xnat:8080/xnat"
GATEWAY="gateway:8100"
SCRIPT="test.sh"

session="ncrc_S01323"
subject="XNAT_S00013"
project="test"
user="admin"
pwd="admin"

if [ -z ${CURL_CACERT} ] || [ ! -f ${CURL_CACERT} ]; then
	CURL_CACERT="-k"
else
	CURL_CACERT="--cacert ${CURL_CACERT}"
fi

p='{"project":"'${project}'","subject":"'${subject}'","session":"'${session}'","host":"'${XNAT}'","user":"'${user}'","pwd":"'${pwd}'","script":"'${SCRIPT}'"}'
list=[
for i in $(seq 1 1 ${NUM_OF_TESTS}); do
	list=${list}${p}
	if [ ${i} -ne ${NUM_OF_TESTS} ]; then
		list=${list},
	fi
done
list=${list}]


curl ${CURL_CACERT} -X POST -H 'Content-Type: application/json' -d  ''$list'' "${GATEWAY}/pipeline"
