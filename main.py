#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import hinet
import seednet
import StringIO
import PyRSS2Gen
import urllib
import datetime
import hashlib
#from google.appengine.ext import ndb
from google.appengine.api import memcache

HTTP_DATE_FMT = '%a, %d %b %Y %H:%M:%S %Z'

def check_date_fmt(date):
    date = date.strip().split(' ')
    if len(date) == 5:
        HTTP_DATE_FMT = '%a, %d %b %Y %H:%M:%S'
    elif len(date) == 6:
        HTTP_DATE_FMT = '%a, %d %b %Y %H:%M:%S %Z'
    return HTTP_DATE_FMT

#not use yet
class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Cache-Control'] = 'max-age=3600, must-revalidate'
        self.response.write('')


#generate hinet rss
class Hinet(webapp2.RequestHandler):

    def output_content(self, content, serve=True):
        if serve:
            self.response.out.write(content)
        else:
            self.response.set_status(304)

    def set_headers(self):
        self.response.headers['Content-Type'] = 'application/xhtml+xml'
        self.response.headers['Cache-Control'] = 'public, max-age=3600, must-revalidate'

    def get_cache_data(self, rss):
        output = memcache.get(rss)
        mtime = memcache.get('h_mtime')
        etag = memcache.get('h_etag')
        if mtime is None:
            mtime = datetime.datetime.utcnow().strftime(HTTP_DATE_FMT) + 'GMT'
        self.response.headers['Last-Modified'] = mtime
        return output, mtime, etag

    def get(self):
        serve = True
        output, mtime, etag = self.get_cache_data('hinet_rss')
        if 'If-Modified-Since' in self.request.headers:
            IFMOD_DATE_FMT = check_date_fmt(self.request.headers['If-Modified-Since'])
            last_seen = datetime.datetime.strptime(self.request.headers['If-Modified-Since'], IFMOD_DATE_FMT)
            last_modified = datetime.datetime.strptime(mtime, HTTP_DATE_FMT)
            if last_seen >= last_modified:
                serve = False
        if 'If-None-Match' in self.request.headers:
            etags = [x.strip('" ') for x in self.request.headers['If-None-Match'].split(',')]
            if etag in etags:
                serve = False
        if output is not None:
            self.set_headers()
            self.response.headers['ETag'] = '"%s"' % etag
            self.output_content(output, serve)
            return
        items = []
        parser = hinet.MyHTMLParser()
        parser.feed(urllib.urlopen('http://search.hinet.net/getNotify?callback=jsonpCallback&type=0&sort=0&mobile=1').read())
        for i in parser.struc_data:
            items.append(PyRSS2Gen.RSSItem(title=i[1] + ' ' +i[3], link=i[2], pubDate=i[0]))

        rss = PyRSS2Gen.RSS2(
            title=u"Hinet系統公告",
            link="http://www.hinet.net/pu/notify.htm",
            description=u"此RSS內容取自Hinet網頁，依照著作權法之合理使用原則節錄部份內容。\
            本RSS僅供參考，Hinet或任何人都不對內容負責",
            lastBuildDate=mtime,
            items=items)

        output = StringIO.StringIO()
        rss.write_xml(output,encoding='utf-8')

        etag = hashlib.sha1(output.getvalue()).hexdigest()

        memcache.set('hinet_rss', output.getvalue(), time=3600)
        memcache.set('h_mtime', mtime, time=3600)
        memcache.set('h_etag', etag, time=3600)

        self.set_headers()
        self.response.headers['ETag'] = '"%s"' % (etag,)
        self.output_content(output.getvalue(), serve)


#generate seednet rss
class Seednet(webapp2.RequestHandler):

    def output_content(self, content, serve=True):
        if serve:
            self.response.out.write(content)
        else:
            self.response.set_status(304)

    def set_headers(self):
        self.response.headers['Content-Type'] = 'application/xhtml+xml'
        self.response.headers['Cache-Control'] = 'public, max-age=3600, must-revalidate'

    def get_cache_data(self, rss):
        output = memcache.get('seednet_rss')
        mtime = memcache.get('s_mtime')
        etag = memcache.get('s_etag')
        if mtime is None:
            mtime = datetime.datetime.utcnow().strftime(HTTP_DATE_FMT) + 'GMT'
        self.response.headers['Last-Modified'] = mtime
        return output, mtime, etag

    def get(self):
        serve = True
        output, mtime, etag = self.get_cache_data('seednet_rss')
        if 'If-Modified-Since' in self.request.headers:
            IFMOD_DATE_FMT = check_date_fmt(self.request.headers['If-Modified-Since'])
            last_seen = datetime.datetime.strptime(self.request.headers['If-Modified-Since'], IFMOD_DATE_FMT)
            last_modified = datetime.datetime.strptime(mtime, HTTP_DATE_FMT)
            if last_seen >= last_modified:
                serve = False
        if 'If-None-Match' in self.request.headers:
            etags = [x.strip('" ') for x in self.request.headers['If-None-Match'].split(',')]
            if etag in etags:
                serve = False
        if output is not None:
            self.set_headers()
            self.response.headers['ETag'] = '"%s"' % etag
            self.output_content(output, serve)
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
            lastBuildDate=mtime,
            items=items)

        output = StringIO.StringIO()
        rss.write_xml(output,encoding='utf-8')

        etag = hashlib.sha1(output.getvalue()).hexdigest()

        memcache.set('seednet_rss', output.getvalue(), time=3600)
        memcache.set('s_mtime', mtime, time=3600)
        memcache.set('s_etag', etag, time=3600)

        self.set_headers()
        self.response.headers['ETag'] = '"%s"' % (etag,)
        self.output_content(output.getvalue(), serve)


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/hinet', Hinet),
    ('/seednet', Seednet),
], debug=False)
