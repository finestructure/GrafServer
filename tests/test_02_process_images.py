from nose.tools import ok_, eq_, raises

from graf.database import connect, create_database, drop_database
from graf import process_images

env = 'TEST'

class TestProcessImages(object):
  
  def setUp(self):
    # TEMP
    drop_database(env)

    create_database(env)
    self.db = connect(env)
    self.db.check_views()
  
  
  def tearDown(self):
    drop_database(env)
    pass
  
  
  def test_01_process_images(self):
    
    # replace dbc_request with a dummy so we don't get charged each time we test
    def mock_dbc_request(*args):
      print 'mock request'
      return 'fake id', process_images.dummy_request()
    process_images.dbc_request = mock_dbc_request
    
    created_at = '2012-02-20T00:%02d:00Z'
    for i in range(5):
      key = 'doc_%d' % i
      doc = {
        'created_at' : created_at % i,
      }        
      self.db[key] = doc

    res = self.db.unprocessed_docs_view()
    eq_(len(res), 5)

    process_images.start_image_processor(env, loop=False, wait=True)
    
    res = self.db.unprocessed_docs_view()
    eq_(len(res), 0)
