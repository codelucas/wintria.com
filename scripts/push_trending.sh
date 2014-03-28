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
(cd /home/lucas/www/wintria.com/wintria-env/wintria.com/wintria; /usr/local/bin/python2.7 manage.py push_trending);

# manually copy static file over, as autocomplete dir is way to large
cp /home/lucas/www/wintria.com/wintria-env/wintria.com/wintria/wintria/autocomplete_static/autocomplete/prefetch.json /home/lucas/www/wintria.com/wintria-env/wintria.com/wintria/wintria/templates/static/autocomplete/prefetch.json

rm -f ${LOCKFILE}
