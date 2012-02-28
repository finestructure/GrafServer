import hashlib
import random
import time

class sha1Client():
  def __init__(self):
    pass

  def decode( self, image, timeout=0):
    ret=sha1_request(image.read())
    return {"captcha":random.uniform(0, 1000000), "text":ret}


def sha1_request(image):
  count = int(random.uniform(1,4))
  time.sleep(count)
  m = hashlib.sha1()
  m.update(image)
  return m.hexdigest()

