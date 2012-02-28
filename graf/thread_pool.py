import threading
import logging
import Queue
import uuid

logger = logging.getLogger('graf.thread_pool')

class Worker(threading.Thread):
  def __init__(self, process_class, requests, results, **kwargs):
    self.process_class = process_class
    threading.Thread.__init__(self, **kwargs)
    self.daemon = True
    self.requests = requests
    self.results = results
    self.start()
  
  def run(self):
    while True:
      request_id, args, kwargs = self.requests.get()
      try:
        self.results.put( (request_id,
                           self.process_class.process(*args, **kwargs) ) )
      except Exception, e:
        logger.exception('Exception in PicWorker: %s' % e)
      self.requests.task_done()


class ThreadPool(object):
  def __init__(self, size, worker_class=Worker, 
               process_class_factory = None ):
    self.size = size
    self.requests = Queue.Queue()
    self.results = Queue.Queue()
    for i in range(self.size):
      worker_class(process_class_factory(), self.requests, self.results)

  def schedule_work(self, *args, **kwargs):
    request_id = uuid.uuid1().hex
    self.requests.put( (request_id, args, kwargs) )
    return request_id

  def join(self):
    self.requests.join()
    return self.results


if __name__ == '__main__':
  import time
  def slow_eval(expr):
    print 'executing:', expr
    time.sleep(1)
    return eval(expr)
  
  pool = ThreadPool(3)
  
  request_ids = []
  request_ids.append(pool.schedule_work(slow_eval, '1+2'))
  request_ids.append(pool.schedule_work(slow_eval, '2+3'))
  request_ids.append(pool.schedule_work(slow_eval, '3+4'))
  
  res = pool.join()

  while not res.empty():
    request_id, result = res.get()
    print request_id, '=>', result

