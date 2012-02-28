from nose.tools import ok_, eq_, raises

from graf.thread_pool import ThreadPool, Worker

class TestThreadPool(object):

  #def test_01_thread_pool(self):
    #pool = ThreadPool(3)
  #
    #request_ids = []
    #request_ids.append(pool.schedule_work('1+2'))
    #request_ids.append(pool.schedule_work('2+3'))
    #request_ids.append(pool.schedule_work('3+4'))
  #
    #res = pool.join()
#
    #expected = [3, 5, 7]
    #while not res.empty():
      #request_id, result = res.get()
      #ok_(result in expected, "%s not in list" % result)
      #expected.remove(result)
    #
    #eq_(expected, [])


  def test_02_custom_worker(self):
    class MyWorker(Worker):
      def __init__(self, requests, results, **kwargs):
        self.my_arg = '1+'
        super(MyWorker, self).__init__(requests, results, **kwargs)
      def run(self):
        while True:
          request_id, method, args, kwargs = self.requests.get()
          print request_id, method, args, kwargs
          self.results.put( (request_id, method(self.my_arg, *args, **kwargs)) )
          self.requests.task_done()
    
    def my_processor_factory():
      return my_processor('1+')

    class my_processor:
      def __init__(self, my_arg):
        self._my_arg=my_arg

      def process(self, arg):
        return eval(self._my_arg + arg)
    
    pool = ThreadPool(3, process_class_factory=my_processor_factory)
  
    request_ids = []
    request_ids.append(pool.schedule_work('1+2'))
    request_ids.append(pool.schedule_work('2+3'))
    request_ids.append(pool.schedule_work('3+4'))
  
    res = pool.join()

    expected = [4, 6, 8]
    while not res.empty():
      request_id, result = res.get()
      ok_(result in expected, "%s not in list" % result)
      expected.remove(result)
    
    eq_(expected, [])
