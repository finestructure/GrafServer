import database
import time
import logging
from optparse import OptionParser
import thread_pool
from graf.vendor import pypsum, deathbycaptcha
import random

logger = logging.getLogger('graf.process_images')

POOL_SIZE = 8


class DbcWorker(thread_pool.Worker):
  
  def __init__(self, requests, results, **kwargs):
    self.client = deathbycaptcha.SocketClient('abstracture', 'i8Kn37rD8v')
    super(DbcWorker, self).__init__(requests, results, **kwargs)

  def run(self):
    while True:
      request_id, method, args, kwargs = self.requests.get()
      self.results.put( (request_id, method(self.client, *args, **kwargs)) )
      self.requests.task_done()


def dbc_request(client, db, doc):
  """
  Sends image to the DBC server for decoding. Returns the request id (captcha id)
  and the text result or nil if there was no result or a timeout.
  """
  image = db.get_image(doc)
  captcha = client.decode(image, timeout=60)
  if captcha:
    # The CAPTCHA was solved; captcha["captcha"] item holds its
    # numeric ID, and captcha["text"] item its text.
    return (captcha["captcha"], captcha["text"])
  else:
    return (None, None)


def dummy_request():
  count = int(random.uniform(1,4))
  time.sleep(count)
  text = pypsum.get_lipsum(howmany=count, what='words', start_with_lipsum='0')
  text = text[0]
  text = ' '.join(text.split()[:count]) # service always returns at least 5 words
  return text


def process_doc(client, db, doc):
  logger.info("Processing '%s'" % doc.id)
  request_id, text_result = dbc_request(client, db, doc)
  logger.info("           '%s' => %s" % (doc.id, text_result))
  doc['text_result'] = text_result
  doc['request_id'] = request_id
  doc['processed'] = True
  try:
    db.save(doc)
  except database.UpdateConflict, e:
    # document has already been processed
    logger.info("Document '%s' is already being processed" % doc.id)
    pass


class Request(object):
  def __init__(self, request_id):
    self.started_at = time.time()
  def has_timed_out(self):
    return time.time() - self.started_at > 30


def start_image_processor(env, loop=True, wait=False):
  db = database.connect(env)
  pool = thread_pool.ThreadPool(POOL_SIZE, worker_class=DbcWorker)
  requests = {}
  
  while True:
    for row in db.unprocessed_docs_view():
      
      if row.id in requests and not requests[row.id].has_timed_out():
        continue
      
      try:
        doc = db[row.id]
        request_id = pool.schedule_work(process_doc, db, doc)
        requests[row.id] = Request(request_id)
        
      except Exception, e:
        logger.warn("Skipped '%s' due to exception '%s'", (row.id, e))
    
    if not loop:
      break
    else:
      time.sleep(0.5)

  if wait:
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
  (options, args) = parser.parse_args()

  options.loglevel = options.loglevel.upper()
  if options.loglevel=='WARNING':
    logging.getLogger("graf").setLevel(logging.WARNING)
  elif options.loglevel=='DEBUG':
    logging.getLogger("graf").setLevel(logging.DEBUG)

  logger.info('Starting image processor')
  start_image_processor(options.env)
  