import json
import datetime
  
def datetime_to_str(a_datetime):
  return datetime.datetime.strftime(a_datetime, "%a %b %d %H:%M:%S %Y")
  
def post_to_dict(post):
  post_dict = {}
  post_dict["content"] = post.content
  post_dict["subject"] = post.subject
  post_dict["created"] = datetime_to_str(post.created)
  post_dict["last_modified"] = datetime_to_str(post.last_modified)
  return post_dict

def post_to_json(post):
  # {"content": "content here", "created": "Thu Apr 12 03:29:21 2012", "last_modified": "Thu Apr 12 03:29:21 2012", "subject": "subject here"}    
  post_dict = post_to_dict(post)
  return json.dumps(post_dict)

def posts_to_json(posts):
  # [{"content": "content here", "created": "Thu Apr 12 03:29:21 2012", "last_modified": "Thu Apr 12 03:29:21 2012", "subject": "subject here"}]    
  posts_dictlist = filter(None, (post_to_dict(post) for post in posts))
  return json.dumps(posts_dictlist)
