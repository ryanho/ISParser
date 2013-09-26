#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import hinet
import seednet
import StringIO
import PyRSS2Gen
import urllib
import datetime
#from google.appengine.ext import ndb
from google.appengine.api import memcache

#not use yet
class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'max-age=3600, must-revalidate'
        self.response.write('')


#generate hinet rss
class Hinet(webapp2.RequestHandler):

    def get(self):
        output = memcache.get('hinet_rss')
        if output is not None:
            self.response.headers['Content-Type'] = 'application/xhtml+xml'
            self.response.headers['Cache-Control'] = 'max-age=3600, must-revalidate'
            self.response.write(output)
            return
        items = []
        parser = hinet.MyHTMLParser()
        parser.feed(urllib.urlopen('http://www.hinet.net/pu/notify.htm').read())
        for i in parser.struc_data:
            items.append(PyRSS2Gen.RSSItem(title=i[1] + ' ' + i[3], link=i[2], pubDate=i[0]))

        rss = PyRSS2Gen.RSS2(
            title=u"Hinet系統公告",
            link="http://www.hinet.net/pu/notify.htm",
            description=u"此RSS內容取自Hinet網頁，依照著作權法之合理使用原則節錄部份內容。\
            本RSS僅供參考，Hinet或任何人都不對內容負責",
            lastBuildDate=datetime.datetime.utcnow(),
            items=items)

        output = StringIO.StringIO()
        rss.write_xml(output,encoding='utf-8')

        memcache.set('hinet_rss', output.getvalue(), time=3600)

        self.response.headers['Content-Type'] = 'application/xhtml+xml'
        self.response.headers['Cache-Control'] = 'max-age=3600, must-revalidate'
        self.response.write(output.getvalue())


#generate seednet rss
class Seednet(webapp2.RequestHandler):

    def get(self):
        output = memcache.get('seednet_rss')
        if output is not None:
            self.response.headers['Content-Type'] = 'application/xhtml+xml'
            self.response.headers['Cache-Control'] = 'max-age=3600, must-revalidate'
            self.response.write(output)
            return
        items = []
        parser = seednet.MyHTMLParser()
        parser.feed(urllib.urlopen(
        'https://service.seed.net.tw/register-cgi/service_notice?FUNC=notice_qry_more&Category=02&Start=1').read())
        for i in parser.struc_data:
            items.append(PyRSS2Gen.RSSItem(title=i[3], link=i[2], pubDate=i[0]))

        rss = PyRSS2Gen.RSS2(
            title=u"Seednet系統公告",
            link="https://service.seed.net.tw/register-cgi/service_notice?FUNC=notice_qry_more&Category=02&Start=1",
            description=u"此RSS內容取自Seednet網頁，依照著作權法之合理使用原則節錄部份內容。\
            本RSS僅供參考，Seednet或任何人都不對內容負責",
            lastBuildDate=datetime.datetime.utcnow(),
            items=items)

        output = StringIO.StringIO()
        rss.write_xml(output,encoding='utf-8')

        memcache.set('seednet_rss', output.getvalue(), time=3600)

        self.response.headers['Content-Type'] = 'application/xhtml+xml'
        self.response.headers['Cache-Control'] = 'max-age=3600, must-revalidate'
        self.response.write(output.getvalue())


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/hinet', Hinet),
    ('/seednet', Seednet),
], debug=False)
