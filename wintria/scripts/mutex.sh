#!/usr/bin/env bash

LOCKFILE=/tmp/test_lock.txt
if [ -e ${LOCKFILE} ] && kill -0 `cat ${LOCKFILE}`; then
    echo "Test already running"
    exit
fi

# make sure the lockfile is removed when we exit and then claim it
trap "rm -f ${LOCKFILE}; exit" INT TERM EXIT
echo $$ > ${LOCKFILE}

# do stuff
echo 'bahaha'
sleep 30

rm -f ${LOCKFILE}
