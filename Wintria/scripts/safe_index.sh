#!/usr/bin/env bash


/home/wintrialucas/bin/indexer Article_article --rotate --config /home/wintrialucas/webapps/windjango/Wintria/misc/sphinx.conf &
PIDs=$!
while kill -0 $PIDs 2>/dev/null; do TIDs="$(ps --no-headers -o tid -Lp $PIDs)"; kill -s SIGSTOP $TIDs; sleep 9; kill -s SIGCONT $TIDs; sleep 2; done;
