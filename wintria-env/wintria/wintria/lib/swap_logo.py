import sys
import cStringIO
import urllib2

from img_utils import prepare_image
from PIL import Image
from wintria.wintria.settings import PROJECT_ROOT

thumbnail_size = 100, 100


dest_thumb_url = PROJECT_ROOT + 'wintria/wintria/logo_static/logo_thumbs/'
dest_gen_url = PROJECT_ROOT + 'wintria/wintria/logo_static/logobank/'

if __name__ == '__main__':
    new_url, domain = sys.argv[1], sys.argv[2]
    upload_gen = dest_gen_url+domain+'.png'
    upload_thumb = dest_thumb_url+domain+'.png'

    _file = cStringIO.StringIO(urllib2.urlopen(new_url, timeout=4).read())

    img = Image.open(_file)
    img.save(dest_gen_url)


    new_img = prepare_image(img)
    new_img.save(upload_thumb)
