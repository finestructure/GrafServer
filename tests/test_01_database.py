from nose.tools import ok_, eq_, raises
import couchdb

from graf import config
from graf.database import Handle

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
