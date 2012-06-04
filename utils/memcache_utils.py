from google.appengine.api import memcache

# key = memcache key
# fun_set = fun(old_val) = for cas to memcache
# fun_add = fun() = for initial add to memcache
def cas(key, fun_set, fun_add=None, max_tries=5):
  """returns new val if successful, otherwise None"""
  client = memcache.Client()
  for _i in range(max_tries):
    val = client.gets(key)
    if val:
      val = fun_set(val)
      if client.cas(key, val):
        return val
    elif fun_add:
      val = fun_add()
      if client.add(key, val):
        return val
    else:
      raise Exception("Uninitialized Value - no fun_add given")
  return None
    
# key = memcache key
# fun_miss = fun() = retrieve data from database
# update = force retrieve data from database
def get(key, fun_miss, update=False):
  """returns val, from DB or Memcache"""
  client = memcache.Client()
  val = client.get(key)
  if (val is None) or update:    
    val = fun_miss()
    client.set(key, val)
  return val

# key = memcache key
# fun_miss = fun() = retrieve data from database
# update = force retrieve data from database
def get_cas(key, fun_miss, update=False):
  """returns val, from DB or Memcache, if successful, otherwise None"""
  fun_set = lambda val: fun_miss()
  fun_add = lambda: fun_miss()
  client = memcache.Client()
  val = client.gets(key)  
  if (val is None) or update:    
    val = cas(key, fun_set, fun_add)
  return val

def flush():
  client = memcache.Client()
  client.flush_all()
