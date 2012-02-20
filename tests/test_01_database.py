from nose.tools import ok_, eq_, raises
import couchdb

from graf import config
from graf.database import Handle, Database

env = 'TEST'

class TestConnection(object):

  def setUp(self):
    url = config.get(env, 'url')
    tech, baseurl = url.split('://')
    self.handle = Handle(baseurl)
    self.server = couchdb.Server('http://'+baseurl)
  
  
  def test_01_create_database(self):
    dbname = config.get(env, 'dbname')
    self.handle.create_database(dbname)
    ok_(self.server[dbname])
  
  
  def test_02_drop_database(self):
    dbname = config.get(env, 'dbname')
    self.handle.create_database(dbname)
    self.handle.drop_database(dbname)
    @raises(couchdb.ResourceNotFound)
    def check():
      self.server[dbname]
    check()
    
    
  def test_03_check_views(self):
    # setup
    dbname = config.get(env, 'dbname')
    self.handle.create_database(dbname)
    db = self.handle.connect(dbname)
    db.check_views()
    # test
    design = db.get('_design/graf')
    ok_(design)
    ok_(design['views'])
    eq_(Database.version, design['version'])
    # cleanup
    self.handle.drop_database(dbname)


