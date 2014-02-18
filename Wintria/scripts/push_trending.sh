#!/usr/bin/env bash

LOCKFILE=/tmp/push_trending.txt
if [ -e ${LOCKFILE} ] && kill -0 `cat ${LOCKFILE}`; then
    echo "Push trending already running"
    exit
fi

# make sure the lockfile is removed when we exit and then claim it
trap "rm -f ${LOCKFILE}; exit" INT TERM EXIT
echo $$ > ${LOCKFILE}

# do stuff
(cd /home/wintrialucas/webapps/windjango/Wintria; /usr/local/bin/python2.7 manage.py push_trending);

# manually copy static file over, as autocomplete dir is way to large
cp /home/wintrialucas/webapps/windjango/Wintria/Wintria/autocomplete_static/autocomplete/prefetch.json /home/wintrialucas/webapps/windevstatic/autocomplete/prefetch.json

rm -f ${LOCKFILE}


