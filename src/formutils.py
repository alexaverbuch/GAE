import re
  
username_re = re.compile('^[a-zA-Z0-9_-]{3,20}$')
password_re = re.compile('^.{3,20}$')
email_re = re.compile('^[\S]+@[\S]+\.[\S]+$')

def check_username(username, error="Invalid username"):
  if username_re.match(username):
    return None
  else:
    return error

def check_password(password, error="Invalid password"):
  if password_re.match(password):
    return None
  else:
    return error

def check_email(email, error="Invalid email"):
  if email_re.match(email):
    return None
  else:
    return error
