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


class Database(object):

  def __init__(self, db):
    self.db = db

  design_name = '_design/graf'
  version = 10
  views = {
    'unprocessed_docs': {
      'map' : """
        function(doc) {
          if (! doc.processed) {
            emit(doc._id, null);
          }
        }
      """
    },
    'doc_created_at' : {
      'map' : """
        function(doc) {
          if (doc.created_at) {
            emit(doc.created_at, [doc._id, doc.source_device, doc.version]);
          }
        }
      """
    },
  }

  def check_views(self, recreate=False):
    if recreate:
      # delete previous version of views
      try:
        del self.db[self.design_name]
      except couchdb.ResourceNotFound:
        pass
    design = self.db.get(self.design_name)
    if design is None:
      # create view
      design = {
        'views' : self.views,
        'version' : self.version
      }
      self.db[self.design_name] = design
    elif design['version'] < self.version:
      # update view
      design['views'] = self.views
      design['version'] = self.version
      self.db[self.design_name] = design



  def __getitem__(self, key):
    """
    Dict-like accessor routed through to couchdb.Database
    """
    try:
      return self.db[key]
    except couchdb.ResourceNotFound:
      raise DocumentNotFound(key)
  

  def __setitem__(self, key, value):
    """
    Dict-like accessor routed through to couchdb.Database
    """
    self.db[key] = value
  

  def __getattr__(self, name):
    """
    By default route all attributes through to couchdb.Database
    """
    return getattr(self.db, name)




