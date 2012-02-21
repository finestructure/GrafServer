import database
import time
import logging
from optparse import OptionParser
import pypsum
import random

logger = logging.getLogger('graf.process_images')


def process_doc(doc):
  logger.info("Processing '%s'" % doc.id)
  count = int(random.uniform(1,4))
  text = pypsum.get_lipsum(howmany=count, what='words', start_with_lipsum='0')
  text = text[0]
  text = ' '.join(text.split()[:count]) # service always returns at least 5 words
  logger.info("           '%s' => %s" % (doc.id, text))
  doc['text_result'] = text
  doc['processed'] = True
  return doc


def process_images(db):
  for row in db.unprocessed_docs_view():
    doc = db[row.id]
    doc = process_doc(doc)
    db.save(doc)


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
  db = database.connect(options.env)
  while True:
    process_images(db)
    time.sleep(0.5)
  