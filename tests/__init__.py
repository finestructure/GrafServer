import os

def get_fixture(fname):
  return os.path.join(os.environ["PYTHONPATH"], "tests", "fixtures", fname)
