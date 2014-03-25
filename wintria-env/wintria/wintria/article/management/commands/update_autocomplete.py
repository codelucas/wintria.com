"""
"""
from django.core.management.base import BaseCommand

from wintria.lib.easycomplete import easycomplete
from wintria.lib.io import convert_to_datum
from wintria.wintria.settings import PROJECT_ROOT

import json
import string
import os

valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

def gen_prefix(string):
    """
    amazon-->am, ama, amaz, amazo
    """
    if len(string) < 2:
        return []
    tot = [string[0]]
    i=0
    for s in string[1:-1]:
        tot.append(tot[i]+s)
        i += 1
    return tot

def valid_filename(string):
    return ''.join(c for c in string if c in valid_chars)

class Command(BaseCommand):
    help = 'Pushes autocomplete results from EasyComplete into static area'

    def handle(self, *args, **options):
        m = easycomplete.get_mapper()
        autocomplete_url = PROJECT_ROOT + 'wintria/wintria/autocomplete_static/autocomplete/'

        for query, results in m.items():
            query = valid_filename(query)
            f = open(autocomplete_url+query+'.json', 'w+')
            datum_txt = json.dumps(convert_to_datum(results, tag_all=True))
            f.write(datum_txt)
            f.close()

if __name__ == '__main__':
    pass
