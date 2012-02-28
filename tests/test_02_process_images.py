from nose.tools import ok_, eq_, raises
from tests import get_fixture

from graf.database import connect, create_database, drop_database
from graf import process_images
from graf.vendor import md5_api, sha1_api

env = 'TEST'

def md5_processor_factory():
  return process_images.DocPicProcessor( "md5", 
                                        md5_api.md5Client() )
def md5b_processor_factory():
  return process_images.DocPicProcessor( "md5b", 
                                        md5_api.md5Client() )
def sha1_processor_factory():
  return process_images.DocPicProcessor( "sha1", 
                                        sha1_api.sha1Client() )
test_services = [
  md5_processor_factory,
  md5b_processor_factory,
  sha1_processor_factory
]

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

      image_name= "test_037233.png"
      image = open(get_fixture(image_name))
      self.db.put_attachment(doc, image.read(), filename="snapshot.png")
  
  
  def tearDown(self):
    #drop_database(env)
    pass
  
  
  def test_01_process_images(self):
    res = self.db.unprocessed_docs_view()
    eq_(len(res), 5)

    process_images.start_image_processor(env, test_services,
                                         loop=False, wait=True)
    
    res = self.db.unprocessed_docs_view()
    eq_(len(res), 0)
    eq_(self.db["doc_0"]['text_result'], "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_0"]['results']["4696be653570ff52ac18be26b001c9e4"], 2 )
    eq_(self.db["doc_0"]['results']["d142c9425f29ca74a659870abbb2d0252348e487"], 1 )
    eq_(self.db["doc_0"]['service_results']['md5'],
        "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_0"]['service_results']['md5b'],
        "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_0"]['service_results']['sha1'],
        "d142c9425f29ca74a659870abbb2d0252348e487")

    eq_(self.db["doc_1"]['text_result'], "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_1"]['results']["4696be653570ff52ac18be26b001c9e4"], 2 )
    eq_(self.db["doc_1"]['results']["d142c9425f29ca74a659870abbb2d0252348e487"], 1 )
    eq_(self.db["doc_1"]['service_results']['md5'],
        "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_1"]['service_results']['md5b'],
        "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_1"]['service_results']['sha1'],
        "d142c9425f29ca74a659870abbb2d0252348e487")

    eq_(self.db["doc_2"]['text_result'], "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_2"]['results']["4696be653570ff52ac18be26b001c9e4"], 2 )
    eq_(self.db["doc_2"]['results']["d142c9425f29ca74a659870abbb2d0252348e487"], 1 )
    eq_(self.db["doc_2"]['service_results']['md5'],
        "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_2"]['service_results']['md5b'],
        "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_2"]['service_results']['sha1'],
        "d142c9425f29ca74a659870abbb2d0252348e487")
    
    eq_(self.db["doc_3"]['text_result'], "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_3"]['results']["4696be653570ff52ac18be26b001c9e4"], 2 )
    eq_(self.db["doc_3"]['results']["d142c9425f29ca74a659870abbb2d0252348e487"], 1 )
    eq_(self.db["doc_3"]['service_results']['md5'],
        "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_3"]['service_results']['md5b'],
        "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_3"]['service_results']['sha1'],
        "d142c9425f29ca74a659870abbb2d0252348e487")

    eq_(self.db["doc_4"]['text_result'], "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_4"]['results']["4696be653570ff52ac18be26b001c9e4"], 2 )
    eq_(self.db["doc_4"]['results']["d142c9425f29ca74a659870abbb2d0252348e487"], 1 )
    eq_(self.db["doc_4"]['service_results']['md5'],
        "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_4"]['service_results']['md5b'],
        "4696be653570ff52ac18be26b001c9e4")
    eq_(self.db["doc_4"]['service_results']['sha1'],
        "d142c9425f29ca74a659870abbb2d0252348e487")
    

  def test_02_exception_handling(self):
    orig_password = process_images.PASSWORD
    process_images.PASSWORD = '-'
    
    # the following call should not spill any unhandled exceptions
    process_images.start_image_processor(env, test_services,
                                         loop=False, wait=True)
    
    process_images.PASSWORD = orig_password
