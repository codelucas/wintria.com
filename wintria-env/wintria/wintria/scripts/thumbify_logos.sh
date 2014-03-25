#!/usr/bin/env bash


LOCKFILE=/tmp/thumbify_logos_lock.txt
if [ -e ${LOCKFILE} ] && kill -0 `cat ${LOCKFILE}`; then
    echo "thumbify_logos.py already running"
    exit
fi

# make sure the lockfile is removed when we exit and then claim it
trap "rm -f ${LOCKFILE}; exit" INT TERM EXIT
echo $$ > ${LOCKFILE}

# do stuff
(cd /home/lucas/www/wintria.com/wintria-env/wintria.com/wintria; /usr/local/bin/python2.7 manage.py thumbify_logos);
(cd /home/lucas/www/wintria.com/wintria-env/wintria.com/wintria; /usr/local/bin/python2.7 manage.py collectstatic --ignore autocomplete --noinput);

rm -f ${LOCKFILE}



