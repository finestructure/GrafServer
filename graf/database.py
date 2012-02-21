import couchdb
import logging
import config

logger = logging.getLogger('graf.database')


class Server(object):
  
  def __init__(self, url):
    self.server = couchdb.Server(url)

  
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
      logger.debug("Connecting to database '%s'" % dbname)
      return Database(self.server[dbname])
    except couchdb.ResourceNotFound:
      raise DatabaseNotFound(dbname)


class Database(object):

  def __init__(self, db):
    self.db = db

  # view constants
  design_name = '_design/graf'
  version = 1
  unprocessed_docs = 'unprocessed_docs'
  doc_created_at = 'doc_created_at'
  views = {
    unprocessed_docs : {
      'map' : """
        function(doc) {
          if (! doc.processed) {
            emit(doc.created_at, null);
          }
        }
      """
    },
    doc_created_at : {
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


  def unprocessed_docs_view(self):
    return self.db.view(self.design_name + '/_view/' + self.unprocessed_docs)


  def save(self, doc):
    try:
      return self.db.save(doc)
    except couchdb.ResourceConflict, e:
      raise UpdateConflict(e)


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
  
  
  def __delitem__(self, key):
    """
    Dict-like delete routed through to couchdb.Database
    """
    del self.db[key]
  
  
  def __contains__(self, key):
    return key in self.db
  

  def __getattr__(self, name):
    """
    By default route all attributes through to couchdb.Database
    """
    return getattr(self.db, name)


class DatabaseNotFound(Exception):
  pass
  
class DocumentNotFound(Exception):
  pass

class UpdateConflict(couchdb.ResourceConflict):
  pass


def create_database(env, dbname=None):
  url = config.get(env, 'url')
  server = Server(url)
  if dbname is None:
    dbname = config.get(env, 'dbname')
  logger.info('Creating database: %s' % dbname)
  server.create_database(dbname)


def drop_database(env, dbname=None):
  url = config.get(env, 'url')
  server = Server(url)
  if dbname is None:
    dbname = config.get(env, 'dbname')
  logger.info( 'Dropping database: %s' % dbname )
  server.drop_database(dbname)


def recreate_database(env, dbname=None):
  drop_database(env, dbname)
  create_database(env, dbname)


def connect(env, dbname=None):
  if hasattr(env, 'get'):
    # we have a dictionary with connection info
    url = env.get('url')
    debug = env.get('debug')
    if dbname is None:
      dbname = env.get('dbname')
  else:
    url = config.get(env, 'url')
    debug = config.debug(env)
    if dbname is None:
      dbname = config.get(env, 'dbname')
  server = Server(url)
  logger.info('Connecting to: %s'  % url )
  logger.info('Using database: %s' % dbname )
  db = server.connect(dbname)
  db.env = env
  db.check_views()
  return db


def dbinfo(env):
  info = {}
  for key in ['url', 'dbname']:
    info[key] = config.get(env, key)
  info['debug'] = config.debug(env)
  return info
