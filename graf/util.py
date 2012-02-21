import sys
from optparse import OptionParser
import database

def delete_all_docs(env):
  db = database.connect(env)
  for row in db.view('_all_docs'):
    if not row.id.startswith('_'):
      print 'Deleting', row.id
      del db[row.id]

def usage():
  print ''

if __name__ == '__main__':
  usage = "usage: %prog [options] command"
  parser = OptionParser(usage=usage)
  parser.add_option('-e', '--env', dest='env', default='DEV',
                    help='database environment (DEV, UAT, PRD,...)')
  (options, args) = parser.parse_args()
  if len(args) != 1:
    parser.print_usage()
    sys.exit(1)
  
  command = args[0]
  
  if command.lower() == 'delete':
    reply = raw_input('Delete all docs in %s? [y/N] ' % options.env)
    if reply.lower() == 'y':
      delete_all_docs(options.env)
    else:
      print 'aborted'
  else:
    print 'unknown command:', command
  