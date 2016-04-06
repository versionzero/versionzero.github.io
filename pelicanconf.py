#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Ben Burnett'
SITENAME = u'versionzero'
SITEURL = 'http://versionzero.org'

PATH = 'content'
ARTICLE_SAVE_AS = 'blog/{date:%Y/%m/%d}/{slug}/index.html'
ARTICLE_URL = ARTICLE_SAVE_AS

TIMEZONE = 'America/Edmonton'
DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
#LINKS = (('Pelican', 'http://getpelican.com/'),
#         ('Python.org', 'http://python.org/'),
#         ('Jinja2', 'http://jinja.pocoo.org/'),
#         ('You can modify those links in your config file', '#'),)

# Social widget
#SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

# Limit the number of articles on each page to something sane.
DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when
# developing.
RELATIVE_URLS = True

# Set the them to our local one, as we will be changing it to suit our
# needs.
THEME = "themes/Flex"

# Articles should be automatically published as a draft.
DEFAULT_METADATA = {
    'status': 'draft',
}
