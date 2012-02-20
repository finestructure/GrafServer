import os
import ConfigParser

serverdir = os.environ['SERVERDIR']
_config = ConfigParser.ConfigParser()
_config.read(os.path.join(serverdir, 'graf', 'environments.cfg'))


def get(env, key):
  return _config.get(env, key)


def debug(env):
  try:
    return _config.getboolean(env, 'debug')
  except ConfigParser.NoOptionError:
    return False
