# Refer to the following link for help:
# http://docs.gunicorn.org/en/latest/settings.html
command = '/home/lucas/www/wintria.com/wintria-env/bin/gunicorn'
pythonpath = '/home/lucas/www/wintria.com/wintria-env/wintria'
bind = '127.0.0.1:8050'
workers = 1
user = 'lucas'
accesslog = '/home/lucas/logs/wintria.com/gunicorn-access.log'
errorlog = '/home/lucas/logs/wintria.com/gunicorn-error.log'
