from nose.tools import ok_, eq_, raises
import couchdb

from graf import config
from graf.database import Server, Database, create_database, connect, \
  drop_database

env = 'TEST'

class TestConnection(object):

  def setUp(self):
    url = config.get(env, 'url')
    self.server = Server(url)
    self.couchdb_server = couchdb.Server(url)
  
  
  def test_01_create_database(self):
    dbname = config.get(env, 'dbname')
    self.server.create_database(dbname)
    ok_(self.couchdb_server[dbname])
  
  
  def test_02_drop_database(self):
    dbname = config.get(env, 'dbname')
    self.server.create_database(dbname)
    self.server.drop_database(dbname)
    @raises(couchdb.ResourceNotFound)
    def check():
      self.couchdb_server[dbname]
    check()
    
    
  def test_03_check_views(self):
    # setup
    dbname = config.get(env, 'dbname')
    self.server.create_database(dbname)
    db = self.server.connect(dbname)
    db.check_views()
    # test
    design = db.get(db.design_name)
    ok_(design)
    ok_(design['views'])
    eq_(Database.version, design['version'])
    # cleanup
    self.server.drop_database(dbname)


class TestDatabase(object):
  
  
  def setUp(self):
    try:
      drop_database(env)
    except:
      pass
    create_database(env)
    self.db = connect(env)
    self.db.check_views()
  
  
  def tearDown(self):
    drop_database(env)
    pass


  def test_01_view_unprocessed_docs(self):
    created_at = '2012-02-20T00:%02d:00Z'
    for i in range(10):
      key = 'doc_%d' % i
      doc = {
        'created_at' : created_at % i,
      }
      if i % 2 == 0:
        doc['processed'] = True
        
      self.db[key] = doc
    
    res = self.db.unprocessed_docs_view()
    eq_(len(res), 5)
    
    subset = res['2012-02-20T00:01:00Z':'2012-02-20T00:05:00Z']
    eq_(len(subset), 3)
    eq_(subset.rows[0].key, '2012-02-20T00:01:00Z')
    eq_(subset.rows[1].key, '2012-02-20T00:03:00Z')
    eq_(subset.rows[2].key, '2012-02-20T00:05:00Z')


  def test_02_delitem_contains(self):
    self.db['test'] = {'key':'value'}
    ok_('test' in self.db)
    ok_('foo' not in self.db)
    del self.db['test']
    ok_('test' not in self.db)


  def test_03_save_get_image(self):
    image = self.db.get_image('doc_1')
    ok_(image is None)
    
    path = config.server_dir + '/tests/fixtures/test_037233.png'
    image = open(path)
    key = 'doc_1'
    self.db[key] = {}
    doc = self.db[key]
    self.db.save_image(doc, image)

    image = self.db.get_image('doc_1')
    ok_(image)
    image = self.db.get_image(doc)
    ok_(image)
    
