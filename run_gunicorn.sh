#!/bin/bash

# cd /home/lucas/www/wintria.com/wintria-env;
# source bin/activate;

# the following exec is very important for gunicorn!
# without it supervisord won't work because the "exec" 
# has the effect of keeping gunicorn in the same process ID, 
# rather than forking off a new one, and then doing exec.

# Normally, when you type "gunicorn" in your shell, the 
# shell first creates a new process with fork, and 
# then in the new process, runs exec.
exec /home/lucas/www/wintria.com/wintria-env/bin/gunicorn -c /home/lucas/www/wintria.com/wintria-env/wintria/configs/gunicorn_config.py wintria.wsgi;
