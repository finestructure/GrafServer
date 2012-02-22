import threading
import Queue
import uuid


class Worker(threading.Thread):
  def __init__(self, requests, results, **kwargs):
    threading.Thread.__init__(self, **kwargs)
    self.daemon = True
    self.requests = requests
    self.results = results
    self.start()
  
  def run(self):
    while True:
      request_id, method, args, kwargs = self.requests.get()
      self.results.put( (request_id, method(*args, **kwargs)) )
      self.requests.task_done()


class ThreadPool(object):
  def __init__(self, size, worker_class=Worker):
    self.size = size
    self.requests = Queue.Queue()
    self.results = Queue.Queue()
    for i in range(self.size):
      worker_class(self.requests, self.results)

  def schedule_work(self, method, *args, **kwargs):
    request_id = uuid.uuid1().hex
    self.requests.put( (request_id, method, args, kwargs) )
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

