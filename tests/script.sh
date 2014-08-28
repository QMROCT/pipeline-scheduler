#!/bin/bash

#CURL_CACERT="telekomchainHTW.pem"
XNAT="xnat:8080/xnat"
#GATEWAY="https://qmroctgw.f4.htw-berlin.de/qmroct_pipeline_gateway/"
GATEWAY="gateway:8100"
#SCRIPT="qmroct.sh"
SCRIPT="test.sh"

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

curl ${CURL_CACERT} -X POST -H 'Content-Type: application/json' -d '{"project":"'"${project}"'","subject":"'"${subject}"'","session":"'"${session}"'","host":"'"${XNAT}"'","user":"'"${user}"'","pwd":"'"${pwd}"'","script":"'"${SCRIPT}"'"}' "${GATEWAY}/pipeline"
#curl ${CURL_CACERT} "gateway?&session=${session}&subject=${subject}&project=${project}&user=${user}&pwd=${pwd}&host=${HOST}"
