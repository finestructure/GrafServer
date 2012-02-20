import couchdb
import logging

logger = logging.getLogger('graf.database')

class Handle(object):
  
  def __init__(self, baseurl):
    self.server = couchdb.Server('http://' + baseurl)

  
  def create_database(self, dbname):
    try:
      logger.debug("Create database '%s'" % dbname)
      self.server.create(dbname)
    except couchdb.PreconditionFailed, e:
      if e[0][0] == u'file_exists':
        pass
      else:
        raise e
  
  
  def drop_database(self, dbname):
    try:
      logger.debug("Drop database '%s'" % dbname)
      self.server.delete(dbname)
    except couchdb.ResourceNotFound:
      pass


  def connect(self, dbname):
    try:
      logger.debug("Connect to database '%s'" % dbname)
      return Database(self.server[dbname])
    except couchdb.ResourceNotFound:
      raise DatabaseNotFound(dbname)




