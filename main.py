#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import urllib
import json
import random
from datetime import datetime, date, time

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
  return 'hello my line bot'

@app.route('/callback', methods=["POST"])
def linebot():
  """ LINEのコールパック """
  args = json.loads(request.get_data().decode('utf-8'))
#  logging.debug('kick from line server,\n %s'%(args['result']))
  queue = taskqueue.Queue('bot-task')

  for msg in args['result']:
    task = taskqueue.Task(url='/_ah/queue/bot-reply', params={'param': json.dumps(msg) }, method="POST")
    queue.add(task)
  return "{}"

@app.route('/_ah/queue/bot-reply', methods=["POST"])
def reply():
  msg = json.loads(request.form.get('param').decode('utf-8'))
  logging.debug(json.dumps(msg))
  prof = Profile.get_or_insert(msg["content"]["from"], mid=msg["content"]["from"])

  # 時間がたったらコンテキストを忘れる
  diff = datetime.now() - prof.date
  if diff.microseconds > 72000000 :
      prof.context = ""
      # キャラも適当に変える
      prof.char = changeChar(random.randint(1, 3))
      logging.debug("context is clear")
  # キャラ変更コマンド
  prof.char = charCommand(msg, prof.char)

  res = dialogue(msg["content"]["text"], prof.context, 'dialog', prof.char )
  prof.context = res["context"]
  prof.put()
  sendLine(msg["content"]["from"], msg["eventType"], res["utt"])
  return "{}"

def charCommand(msg, defchar) :
  char = ""
  # キャラのコマンド
  if msg["content"]["text"].find(u"普通") >= 0:
      char = ""
  if msg["content"]["text"].find(u"関西") >= 0:
      char = "20"
  if msg["content"]["text"].find(u"赤ちゃん") >= 0:
      char = "30"
  if defchar is None:
      char = changeChar(random.randint(1, 3))
  return char

def changeChar(n):
    """ キャラ変更の辞書 """
    switch = {
        1: "",
        2: "20",
        3: "30"
    }
    return switch.get(n) or ''

def dialogue(msg, context, mode, t):
  url = config.DOCOMO_DIALOGUE_URL + config.DOCOMO_DIALOGUE_API_KEY
  form_fields = {
      "utt": msg,
      "context": context,
      "mode": mode,
      "t": t
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
    logging.warn(result.content)
  return json.loads(result.content)

def sendLine(tgt_id, event_type, msg_data):
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
    logging.warn(result.content)
