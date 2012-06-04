from google.appengine.ext import db

class WikiPage(db.Model):
  title = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  version = db.IntegerProperty(required=True)
  username = db.StringProperty(required=True)

class WikiUser(db.Model):
  username = db.StringProperty(required=True)
  password = db.StringProperty(required=True)
  email = db.EmailProperty(required=False)
  created = db.DateTimeProperty(auto_now_add=True)
