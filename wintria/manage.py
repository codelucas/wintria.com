#!/usr/bin/env python
import os
import sys

path = '/home/lucas/www/wintria.com/wintria-env/wintria'
if path not in sys.path:
    sys.path.insert(0, path)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wintria.wintria.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
