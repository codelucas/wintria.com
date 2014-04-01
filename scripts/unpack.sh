#!/usr/bin/env bash

LOCKFILE=/tmp/unpack_lock.txt
if [ -e ${LOCKFILE} ] && kill -0 `cat ${LOCKFILE}`; then
    echo "UnpackArticles.py already running"
    exit
fi

# make sure the lockfile is removed when we exit and then claim it
trap "rm -f ${LOCKFILE}; exit" INT TERM EXIT
echo $$ > ${LOCKFILE}

(cd /home/lucas/www/wintria.com/wintria-env/wintria/wintria; \
    /home/lucas/www/wintria.com/wintria-env/bin/python2.7 manage.py unpack_articles);

rm -f ${LOCKFILE}
