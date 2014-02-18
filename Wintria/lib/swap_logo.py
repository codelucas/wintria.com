import sys
from PIL import Image
import cStringIO
import urllib2
thumbnail_size = 100, 100
from img_utils import prepare_image

dest_thumb_url = '/home/wintrialucas/webapps/windjango/wintria/wintria/logo_static/logo_thumbs/'
dest_gen_url = '/home/wintrialucas/webapps/windjango/wintria/wintria/logo_static/logobank/'

if __name__ == '__main__':
    new_url, domain = sys.argv[1], sys.argv[2]
    upload_gen = dest_gen_url+domain+'.png'
    upload_thumb = dest_thumb_url+domain+'.png'

    _file = cStringIO.StringIO(urllib2.urlopen(new_url, timeout=4).read())

    img = Image.open(_file)
    img.save(dest_gen_url)


    new_img = prepare_image(img)
    new_img.save(upload_thumb)
