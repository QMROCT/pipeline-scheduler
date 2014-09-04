#!/bin/bash

#CURL_CACERT="path"
GATEWAY="127.0.0.1:8100"

# get input parameters
while [ $# -gt 1 ]
do
	case $1 in
	-xnatID)
	xnatID="$2"
	shift 2
	;;
	-session)
	session="$2"
	shift 2
	;;
	-subject)
	subject="$2"
	shift 2
	;;
	-project)
	project="$2"
	shift 2
	;;
	-user)
	user="$2"
	shift 2
	;;
	-pwd)
	pwd="$2"
	shift 2
	;;
	-host)
	host="$2"
	shift 2
	;;
	-script)
	script="$2"
	shift 2
	;;
	-type)
	type="$2"
	shift 2
	;;
	*)
	shift 2
	;;
	esac
done

if [ -z ${CURL_CACERT} ] || [ ! -f ${CURL_CACERT} ]; then
	CURL_CACERT="-k"
else
	CURL_CACERT="--cacert ${CURL_CACERT}"
fi

curl ${CURL_CACERT} -X POST -H 'Content-Type: application/json' -d '{"project":"'${project}'","subject":"'${subject}'","session":"'${session}'","host":"'${host}'","user":"'${user}'","pwd":"'${pwd}'","script":"'${script}'","type":"'${type}'"}' "${GATEWAY}/tasks"
