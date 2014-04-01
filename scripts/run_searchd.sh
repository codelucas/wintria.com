#!/bin/bash

# Nodetach because supervisor fails when the guarded process
# daemonizes itself (as searchd normally does).
/usr/local/bin/searchd --config /home/lucas/www/wintria.com/wintria-env/wintria/configs/sphinx.conf --nodetach
