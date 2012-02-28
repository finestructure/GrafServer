import hashlib
import random
import time

class md5Client():
  def __init__(self):
    pass

  def decode( self, image, timeout=0):
    ret=md5_request(image.read())
    return {"captcha":random.uniform(0, 1000000), "text":ret}


def md5_request(image):
  count = int(random.uniform(1,4))
  time.sleep(count)
  m = hashlib.md5()
  m.update(image)
  return m.hexdigest()

