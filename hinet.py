#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
import urllib
import datetime

#struc_data = [(announce_date, issue_date, p_title, p_url)]
prefix_url = 'http://www.hinet.net/pu/'


def roc2gmt(date):
    year, month, day = date.split('/')
    year = int(year) + 1911
    result = datetime.datetime.strptime(str(year) + month + day, '%Y%m%d').strftime('%a, %d %b %Y %H:%M:%S CST')
    return result


# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self):
        self.struc_data = []
        self.announce_date = ''
        self.issue_date = ''
        self.p_url = ''
        self.p_title = ''
        self.marker = 0
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'span' and attrs[0] == ('class', 'copyright news'):
            self.marker = 1
        elif tag == 'img' and attrs[0] == ('height', '10'):
            self.marker = 2
        elif tag == 'a' and attrs[1] == ('class', 'head51 t'):
            self.marker = 3
            self.p_url = prefix_url + attrs[0][1]

    def handle_endtag(self, tag):
        self.marker = 0

    def handle_data(self, data):
        if self.marker == 1:
            self.announce_date = roc2gmt(data.strip())
        elif self.marker == 2:
            self.issue_date = data.strip()
        elif self.marker == 3:
            self.p_title = data.decode('utf-8').strip()
            self.struc_data.append((self.announce_date, self.issue_date, self.p_url, self.p_title))

if __name__ == '__main__':
    import PyRSS2Gen
    items = []
    parser = MyHTMLParser()
    parser.feed(urllib.urlopen('http://www.hinet.net/pu/notify.htm').read())
    for i in parser.struc_data:
        items.append(PyRSS2Gen.RSSItem(title=i[1] + ' ' + i[3], link=i[2], pubDate=i[0]))

    rss = PyRSS2Gen.RSS2(
        title=u"Hinet系統公告",
        link="",
        description="",
        lastBuildDate=datetime.datetime.utcnow(),
        items=items)

    rss.write_xml(open("hinet.xml", "w"),encoding='utf-8')
