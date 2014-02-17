import math
import Image
import ImageFile
import urllib2
import StringIO
import struct
import reseek_file

thumbnail_size = 100, 100

def prepare_image(image):
    image = square_image(image)
    image.thumbnail(thumbnail_size, Image.ANTIALIAS)
    return image

def image_entropy(img):
    """calculate the entropy of an image"""
    hist = img.histogram()
    hist_size = sum(hist)
    hist = [float(h) / hist_size for h in hist]
    return -sum([p * math.log(p, 2) for p in hist if p != 0])

def square_image(img):
    """if the image is taller than it is wide, square it off. determine
    which pieces to cut off based on the entropy pieces."""
    x,y = img.size
    while y > x:
        #slice 10px at a time until square
        slice_height = min(y - x, 10)

        bottom = img.crop((0, y - slice_height, x, y))
        top = img.crop((0, 0, x, slice_height))

        #remove the slice with the least entropy
        if image_entropy(bottom) < image_entropy(top):
            img = img.crop((0, 0, x, y - slice_height))
        else:
            img = img.crop((0, slice_height, x, y))

        x,y = img.size

    return img

def is_bad_url(url):
    img_response = get_response(url)
    if img_response is None: # is 404
        return True
    try:
        image_type, wi, he = get_img_info(img_response)
        if verify_img_dims(wi, he):
            return False # it's valid
        return True
    except Exception, e:
        print 'Failed while extracting article dimensions', str(e)
        pass # To risky to fail on this now, will change in future
    return False

def get_response(url):
    ''' returns datastream to url if true to save time'''
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req, timeout=4)
    except urllib2.URLError,e:  # 404
        #if e.reason == 'Not Found':
        #    return None
        return None
    except Exception, e:        # Malformed
        return None
    else:                       # 200
        return response

def verify_img_dims(wi, hi):
    min_wi, min_he = 70, 40
    max_wi, max_he = 1500, 900
    return (wi>= min_wi and hi>=min_he and wi<=max_wi and hi<=max_he)


def get_img_info(datastream):
    datastream = reseek_file.ReseekFile(datastream)
    data = str(datastream.read(30))

    data = str(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs
    if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
          and (data[12:16] == 'IHDR')):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # handle JPEGs
    elif (size >= 2) and data.startswith('\377\330'):
        content_type = 'image/jpeg'
        datastream.seek(0)
        datastream.read(2)
        b = datastream.read(1)
        try:
            while (b and ord(b) != 0xDA):
                while (ord(b) != 0xFF): b = datastream.read(1)
                while (ord(b) == 0xFF): b = datastream.read(1)
                if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                    datastream.read(3)
                    h, w = struct.unpack(">HH", datastream.read(4))
                    break
                else:
                    datastream.read(int(struct.unpack(">H", datastream.read(2))[0])-2)
                b = datastream.read(1)
            width = int(w)
            height = int(h)
        except struct.error:
            pass
        except ValueError:
            pass

    return content_type, width, height


if __name__=='__main__':
    img_data = urllib2.urlopen("http://wintrialucas.webfactional.com/static/logobank/www.nytimes.com.png")
    image_type,width,height = get_img_info(img_data)
    print image_type, width, height
