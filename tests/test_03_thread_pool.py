from nose.tools import ok_, eq_, raises

from graf.thread_pool import ThreadPool

class TestThreadPool(object):

  def test_01_thread_pool(self):
    pool = ThreadPool(3)
  
    request_ids = []
    request_ids.append(pool.schedule_work(eval, '1+2'))
    request_ids.append(pool.schedule_work(eval, '2+3'))
    request_ids.append(pool.schedule_work(eval, '3+4'))
  
    res = pool.join()

    expected = [3, 5, 7]
    while not res.empty():
      request_id, result = res.get()
      expected.remove(result)
    
    eq_(expected, [])
