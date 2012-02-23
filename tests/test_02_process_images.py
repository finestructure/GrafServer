from nose.tools import ok_, eq_, raises

from graf.database import connect, create_database, drop_database
from graf import process_images

env = 'TEST'

class TestProcessImages(object):
  
  def setUp(self):
    try:
      drop_database(env)
    except:
      pass
    create_database(env)
    self.db = connect(env)
    self.db.check_views()
    created_at = '2012-02-20T00:%02d:00Z'
    for i in range(5):
      key = 'doc_%d' % i
      doc = {
        'created_at' : created_at % i,
      }        
      self.db[key] = doc
  
  
  def tearDown(self):
    drop_database(env)
    pass
  
  
  def test_01_process_images(self):
    res = self.db.unprocessed_docs_view()
    eq_(len(res), 5)

    process_images.start_image_processor(env, loop=False, wait=True, test_mode=True)
    
    res = self.db.unprocessed_docs_view()
    eq_(len(res), 0)


  def test_02_exception_handling(self):
    orig_password = process_images.PASSWORD
    process_images.PASSWORD = '-'
    
    # the following call should not spill any unhandled exceptions
    process_images.start_image_processor(env, loop=False, wait=True)
    
    process_images.PASSWORD = orig_password