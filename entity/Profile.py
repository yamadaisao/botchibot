#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

class Profile(ndb.Model) :
  mid = ndb.StringProperty(indexed=True)
  context = ndb.StringProperty(indexed=False)
  char = ndb.StringProperty(indexed=False)
  date = ndb.DateTimeProperty(auto_now_add=True)
