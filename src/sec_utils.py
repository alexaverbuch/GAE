import hmac
import random
import string
import hashlib

SECRET = "~"
SEPARATOR = "|"
SALT_LEN = 5

# Security General
def hash_str(s):
  return hmac.new(SECRET, s, hashlib.sha256).hexdigest()
def make_salt():
    return "".join(random.choice(string.letters) for _x in xrange(SALT_LEN))
def make_salted_hash(val, salt=None):
  if not salt:
    salt = make_salt()
  return "%s%s%s" % (hash_str(val + salt), SEPARATOR, salt)

# Secure Values
def make_secure_val(val):
  return "%s%s%s" % (val, SEPARATOR, hash_str(val))
def extract_secure_val(secure_val):
  secure_val_tokens = secure_val.split(SEPARATOR)
  # [value, hash]
  if secure_val_tokens.__len__() == 2: 
    val = secure_val_tokens[0]
    return val if secure_val == make_secure_val(val) else None
  else:
    return None
  
# Secure Passwords
def make_pw_hash(name, pw, salt=None):
  return make_salted_hash(name + pw, salt)
def check_pw_hash(name, pw, salted_hash):
  salt = salted_hash.split(SEPARATOR)[1]
  return salted_hash == make_pw_hash(name, pw, salt)

#user = 'spez'
#password = 'hunter2'
#login_hash = make_pw_hash(user, password)
#print "user = %s" % user
#print "password = %s" % password
#print "login_hash = %s" % login_hash
#print "check_pw_hash(spez,hunter2,login_hash) = %s" % check_pw_hash('spez', 'hunter2', login_hash)
#print 
#
#value = "3"
#secure_value = make_secure_val(value)
#print "value = %s" % value
#print "secure_value = %s" % secure_value
#print "(value == extract_secure_val(secure_value)) = %s" % (value == extract_secure_val(secure_value))
