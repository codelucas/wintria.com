#!/usr/bin/env bash


/home/lucas/bin/indexer Article_article --rotate --config /home/lucas/www/wintria.com/wintria-env/wintria.com/wintria/misc/sphinx.conf &
PIDs=$!
while kill -0 $PIDs 2>/dev/null; do TIDs="$(ps --no-headers -o tid -Lp $PIDs)"; kill -s SIGSTOP $TIDs; sleep 9; kill -s SIGCONT $TIDs; sleep 2; done;
