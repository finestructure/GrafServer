import database
import time
import logging
from optparse import OptionParser
import thread_pool
from graf.vendor import pypsum, deathbycaptcha, bypass_api, md5_api
import random

logger = logging.getLogger('graf.process_images')

POOL_SIZE = 8
TIMEOUT = 60
USERNAME = 'abstracture'
PASSWORD = 'i8Kn37rD8v'

bypass_key = '893950469f6dc3f434611b9ffe51acf9'


class DocPicProcessor:
  def __init__(self, service_name, client):
    self.service_name = service_name
    self.client = client

  def process( self, db, doc_id ):
    logger.info("Processing '%s' using '%s'" % (doc_id, self.service_name))
    doc=db[doc_id]
    try:
      # record processing state
      doc['state'] = 'processing'
      db.save(doc)
    except database.UpdateConflict, e:
      # document has already being processed
      logger.info("Document '%s' is already being processed" % doc.id)
      #return
    
    start = time.time()
    request_id, text_result = do_request(self.client, db, doc)
    elapsed = time.time() - start

    logger.info("           '%s' using '%s' => %s (%.1fs)" , 
                doc.id,
                self.service_name, 
                text_result,
                elapsed)
    conflict_count = 0
    while True:
      # reload document, to get changes by other threads
      doc=db[doc_id]
      doc['text_result'] = str(text_result)
      if not doc.has_key('service_results'):
        doc['service_results'] = {}
      doc['service_results'][self.service_name]=text_result
      if not doc.has_key('results'):
        doc['results'] = {}
      if not doc['results'].has_key(text_result):
        doc['results'][text_result] = 0
      doc['results'][text_result] += 1

      doc['request_id'] = request_id
      doc['processed'] = True
      doc['processing_time'] = elapsed
      if text_result is None or text_result == '':
        doc['state'] = 'timeout'
      else:
        doc['state'] = 'idle'

      try:
        db.save(doc)
        break
      except database.UpdateConflict, e:
        # document has already been processed
        logger.info("Update conflict saving text result document '%s' using '%s'", 
                    doc.id, self.service_name)
        conflict_count+=1
        if conflict_count > 3:
          logger.info("Update conflict breaking from loop  doc '%s' using '%s'", 
                      doc.id, self.service_name)
          break
        pass

def dbc_processor_factory():
  return DocPicProcessor( "DBC", 
                         deathbycaptcha.SocketClient(USERNAME, PASSWORD ) )

def pbc_processor_factory():
  return DocPicProcessor( "PBC",
                         bypass_api.bypassClient(bypass_key) )

def md5_processor_factory():
  return DocPicProcessor( "md5", 
                         md5_api.md5Client() )

def do_request(client, db, doc_id):
  """
  Sends image to the DBC server for decoding. Returns the request id (captcha id)
  and the text result or nil if there was no result or a timeout.
  """
  image = db.get_image(doc_id)
  captcha = client.decode(image, timeout=TIMEOUT)
  if captcha:
    # The CAPTCHA was solved; captcha["captcha"] item holds its
    # numeric ID, and captcha["text"] item its text.
    return (captcha["captcha"], captcha["text"])
  else:
    return (None, None)

class Request(object):
  def __init__(self, request_id):
    self.started_at = time.time()
  def has_timed_out(self):
    return time.time() - self.started_at > TIMEOUT

services=[ dbc_processor_factory,
           pbc_processor_factory,
         ]
test_services=[ 
  md5_processor_factory 
]

def start_image_processor(env, services, loop=True, wait=False ):
  db = database.connect(env)
  # generate array of ( pool, requests ) tupels, with a thread pool and
  # a dictionary with for this pool currently open requests
  pool_requests = []
  for service_processor_factory in services:
    pool_requests.append( ( thread_pool.ThreadPool( POOL_SIZE,
                                                 process_class_factory= service_processor_factory ),
                       {} ) )
  
  while True:
    try:
      for row in db.unprocessed_docs_view():
        for pool, requests in pool_requests:
          if row.id in requests and not requests[row.id].has_timed_out():
            continue
          request_id = pool.schedule_work(db, row.id)
          requests[row.id] = Request(request_id)
    except Exception, e:
      logger.exception("Exception in while processing view: '%s'", e)
    
    if not loop:
      break
    else:
      time.sleep(0.5)

  if wait:
    for pool, requests in pool_requests:
      pool.join()


if __name__ == '__main__':
  logging.getLogger("graf").addHandler(logging.StreamHandler())
  logging.getLogger("graf").setLevel(logging.INFO)
  usage = ("usage: %prog [options]")
  parser = OptionParser(usage=usage)
  parser.add_option('-e', '--env', dest='env', default='DEV',
                    help='database environment (DEV, UAT, PRD,...)')
  parser.add_option('-l', '--loglevel', dest='loglevel',
                    default='info',
                    help='set loglevel INFO, WARNING, DEBUG')
  parser.add_option('-t', '--test', dest='test',
                    action='store_true', default=False,
                    help='switch on test mode (use dummy request for decoding)')
  (options, args) = parser.parse_args()

  options.loglevel = options.loglevel.upper()
  if options.loglevel=='WARNING':
    logging.getLogger("graf").setLevel(logging.WARNING)
  elif options.loglevel=='DEBUG':
    logging.getLogger("graf").setLevel(logging.DEBUG)
  test_mode = options.test

  msg = 'Starting image processor'
  use_services=services
  if test_mode:
    msg += ' in TEST mode'
    use_services=test_services
  logger.info(msg)
  start_image_processor(options.env, use_services)
  
