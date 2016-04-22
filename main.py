#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import urllib
import json
from google.appengine.ext import vendor
vendor.add('lib')
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from flask import Flask
from flask import request

from entity.Profile import Profile
from conf.config import config

app = Flask(__name__)

@app.route('/')
def index():
#  prof = Profile()
#  prof.mid = 'aaa'
#  prof.context = 'context'
#  prof.put()
  return 'hello my line bot'

@app.route('/callback', methods=["POST"])
def linebot():
  args = json.loads(request.get_data().decode('utf-8'))
#  logging.debug('kick from line server,\n %s'%(args['result']))
  queue = taskqueue.Queue('bot-task')

  for msg in args['result']:
#    logging.debug(json.dumps(msg))
    task = taskqueue.Task(url='/_ah/queue/bot-reply', params={'param': json.dumps(msg) }, method="POST")
    queue.add(task)
  return "{}"

@app.route('/_ah/queue/bot-reply', methods=["POST"])
def reply():
  msg = json.loads(request.form.get('param').decode('utf-8'))
  prof = Profile.get_or_insert(msg["content"]["from"], mid=msg["content"]["from"])
  res = dialogue(msg["content"]["text"], prof.context, 'dialog' )
  prof.context = res["context"]
  prof.put()
  kickBot( msg["content"]["from"], msg["eventType"], res["utt"] )
  return "{}"

def dialogue(msg, context, mode):
  url = config.DOCOMO_DIALOGUE_URL + config.DOCOMO_DIALOGUE_API_KEY
  form_fields = {
      "utt": msg,
      "context": context,
      "mode": mode
      }
  result = urlfetch.fetch(
    url=url,
    payload=json.dumps(form_fields,ensure_ascii=False),
    method=urlfetch.POST,
    headers={
                'Content-type':'application/json; charset=UTF-8'
            }
    )
  if result.status_code == 200:
    logging.debug(result.content)
  else:
    logging.debug(result.content)
  return json.loads(result.content)

def kickBot(tgt_id, event_type, msg_data):
  url = config.LINE_URL
  form_fields = {
      "to": [str(tgt_id)],
      "toChannel": 1383378250,
      "eventType": 138311608800106203,
      "content":{
        "contentType":1,
        "toType":1,
        "text":msg_data
        }
      }
  logging.debug(form_fields)
  form_data = urllib.urlencode(form_fields)
  result = urlfetch.fetch(
    url=url,
    payload=json.dumps(form_fields,ensure_ascii=False),
    method=urlfetch.POST,
    headers={
                'Content-type':'application/json; charset=UTF-8',
                'X-Line-ChannelID':config.LINE_CHANNEL_ID,
                'X-Line-ChannelSecret':config.LINE_CHANNEL_SECRET,
                'X-Line-Trusted-User-With-ACL':config.LINE_BOT_MID
            }
    )
  if result.status_code == 200:
    logging.debug(result.content)
  else:
    logging.debug(result.content)
