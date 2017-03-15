import os, sys
sys.path.append(os.path.dirname(__file__) + "/libs")
import flickr_api
from flickr_api.api import flickr

flickr_api.set_keys(api_key = '', api_secret = '')

print flickr.reflection.getMethodInfo(method_name = "flickr.photos.getInfo")
# flickr_api.set_auth_handler(filename)
# user = flickr_api.test.login()
# print user

print "done"
