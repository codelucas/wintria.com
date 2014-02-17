import boto
from boto.s3.key import Key

AMAZON_ACCESS_KEY = 'AKIAIGZC2YWV6POF743Q'
AMAZON_ACCESS_SECRET = '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'
AMAZON_S3_ARTICLE_BUCKET = 'wintria-article-images'
# ENDPOINT = '//wintria-article-images.s3-us-west-2.amazonaws.com/[KEY GOES HERE]'

# refer to:
# http://www.laurentluce.com/posts/upload-and-download-files-tofrom-amazon-s3-using-pythondjango/

def upload_img(abs_fn, key, bucket=AMAZON_S3_ARTICLE_BUCKET):
    try:
        # connect to the bucket
        conn = boto.connect_s3(AMAZON_ACCESS_KEY,
                               AMAZON_ACCESS_SECRET)
        bucket = conn.get_bucket(bucket)
        # go through each version of the file
        # url = 'http://cnn.com/2321432/2013/13324/the_new_article_of_the_day#123124%'
        # key = str(int(hashlib.md5(url).hexdigest(), 16))
        # abs_fn = 'kitty_1.JPG'
        # create a key to keep track of our file in the storage
        k = Key(bucket)
        k.key = key
        k.set_contents_from_filename(abs_fn)
        # we need to make it public so it can be accessed publicly
        # using a URL like http://s3.amazonaws.com/bucket_name/key
        k.make_public()
        # remove the file from the web server
        # os.remove(abs_fn)
        # print 'all done! access via', ENDPOINT.replace('[KEY GOES HERE]', key)

        return 'https://%s.s3-us-west-2.amazonaws.com/%s' % (bucket, key)
    except Exception, e:
        print('s3 err %s %s %s' % (str(e), key, abs_fn))
        return None


if __name__ == '__main__':
    upload_img('/path/too/test/img', 'key.png')
