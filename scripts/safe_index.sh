#!/usr/bin/env bash

# An old script I used to index Sphinx in intervals to prevent
# too much disk IO usage when on Webfaction servers.
# Now i'm on DigitalOcean this isn't as big of a deal.

/home/lucas/bin/indexer Article_article --rotate --config /home/lucas/www/wintria.com/wintria-env/wintria.com/wintria/misc/sphinx.conf &
PIDs=$!
while kill -0 $PIDs 2>/dev/null; do TIDs="$(ps --no-headers -o tid -Lp $PIDs)"; kill -s SIGSTOP $TIDs; sleep 9; kill -s SIGCONT $TIDs; sleep 2; done;
