import os
import ConfigParser

server_dir = os.environ['SERVERDIR']
_config = ConfigParser.ConfigParser()
_config.read(os.path.join(server_dir, 'graf', 'environments.cfg'))


def get(env, key):
  return _config.get(env, key)

def username(env):
  try:
    return _config.get(env, 'username')
  except ConfigParser.NoOptionError:
    return False

def password(env):
  try:
    return _config.get(env, 'password')
  except ConfigParser.NoOptionError:
    return False

def debug(env):
  try:
    return _config.getboolean(env, 'debug')
  except ConfigParser.NoOptionError:
    return False

