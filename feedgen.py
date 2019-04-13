#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import certifi
import urllib3
import lxml.html
import re
import pytz
import operator
import feedgenerator

from datetime import datetime, timedelta, timezone


class Feeds:
    def __init__(self, id, header, ptext, pdate, link, image):
        self.id = id
        self.header = header
        self.ptext = ptext
        self.pdate = pdate
        self.link = link
        self.image = image


class GetPage(object):
    def getPage(self, url):
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',  # Force certificate check.
            ca_certs=certifi.where(),  # Path to the Certifi bundle.
        )
        data = ''
        try:
            data = http.request('GET', url, timeout=10,
                                headers={
                                    'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
                                ).data
            codeType = chardet.detect(data)
            data = data.decode(codeType['encoding'])
        except:
            pass
        return data


ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]|[\x00-\x1f\x7f-\x9f]|[\uffff]')
def illegal_char_remover(data):
    if isinstance(data, str):
        return ILLEGAL_CHARACTERS_RE.sub("", data)
    else:
        return data

args = sys.argv
feeds = []
baseurl = 'https://www.trendswatcher.net'
regexpNS = 'http://exslt.org/regular-expressions'
f = 0

def to_dict(name):
    month_dict = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
                  "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    return month_dict[name]

def conv_date(str):
    check_string = re.match(r'[\d|\.|,| ]+', str)
    if check_string is None:
      r = re.match(r'^([a-zA-Z0-9]+)[,|\.| ]+(\d+)[\.|,| ]+(\d+)', str)
      if r is None:
        return None
      if r.lastindex == 3:
        return [r.group(3), to_dict(r.group(1)[:3]), r.group(2)]
    else:
      r = re.match(r'^(\d+)[\.|,| ]+(\d+)[\.|,| ]+(\d+)', str)
      return [r.group(3), r.group(2), r.group(1)]

### HEADLINE
if args[0] == 'debug':
    print('debug: headline')
    r = open('contents/headline.html')
    dom = lxml.html.fromstring(r.read())
else:
    ro = GetPage()
    r = ro.getPage(baseurl)
    dom = lxml.html.fromstring(r)

l = list()
n = 0

for ptn in ['^cc-m-textwithimage-\d+$', '^cc-m-\d+$']:
    o = dom.xpath('//*[re:test(@id,ptn)]/p[2]/span', namespaces={'re': regexpNS})
    for p in o:
        for q in p.xpath('//@id'):
            if re.match(ptn, q):
                l.append(q)
                n = n + 1
        break

timeline = dom.xpath('//li[@class="jmd-nav__list-item-1"]/a')[0].get("href")

for k in l:
    flg = 0
    if len(dom.xpath('//*[@id="' + k + '"]/p')) > 4:
        continue
    for j in [4, 3]:
        if flg == 0:
            s = dom.xpath('//*[@id="' + k + '"]/p[' + str(j) + ']/a')
            for i in s:
                if i.get('href') is not None:
                    feeds.append(Feeds('', '', '', '', '', ''))
                    try:
                        feeds[f].header = i.get('title')
                    except:
                        print('error:header ' + k)
                    feeds[f].link = baseurl + i.get('href')
                    flg = 1
    if flg == 1:
        for i in dom.xpath('//*[@id="' + k + '"]/p[1]/span'):
            feeds[f].ptext = i.text_content().replace('\n', '')
            feeds[f].id = k
        for i in dom.xpath('//*[@id="' + k + '"]/p/span/span'):
            feeds[f].pdate = i.text_content()
        for i in dom.xpath('//*[@id="' + k + '"]/p/strong/span'):
            feeds[f].pdate = i.text_content()
        dlist = conv_date(feeds[f].pdate)
        if dlist is None:
            feeds[f].pdate = blist
        else:
            feeds[f].pdate = dlist
            blist = dlist
        if '-textwithimage-' in k:
            rk = re.sub('cc-m-textwithimage-(\d+)', r'cc-m-textwithimage-image-\1', k)
            for i in dom.xpath('//img[@id="' + rk + '"]/@src'):
                feeds[f].image = i
        f = f + 1

### TIMELINE

if args[0] == 'debug':
    print('debug: headline')
    r = open('contents/timeline.html')
    dom = lxml.html.fromstring(r.read())
else:
    ro = GetPage()
    r = ro.getPage(baseurl + timeline)
    dom = lxml.html.fromstring(r)

l = list()
pattern = r'^cc-m-\d+$'

n = 0
o = dom.xpath('//*[re:test(@id,"^cc-m-[0-9]+$")]/p[2]/span', namespaces={'re': regexpNS})

for p in o:
    for q in p.xpath('//@id'):
        if re.match(pattern, q):
            l.append(q)
            n = n + 1
    break

l = list(set(l))
l.sort()

for k in l:
    if len(dom.xpath('//*[@id="' + k + '"]/p')) > 4:
        continue
    s = dom.xpath('//*[@id="' + k + '"]/p[2]/span')
    for i in s:
        if i is None:
            continue
        else:
            feeds.append(Feeds('', '', '', '', '', ''))
            g = 0
            for l in range(len(s)):
                feeds[f].ptext = feeds[f].ptext + s[g].text_content().replace('\n', '')
                g = g + 1
            feeds[f].id = k
            for i in dom.xpath('//*[@id="' + k + '"]/p[1]//a'):
                feeds[f].header = i.get("title")
                feeds[f].link = baseurl + i.get("href")
            for i in dom.xpath('//*[@id="' + k + '"]/p/strong/span'):
                feeds[f].pdate = i.text_content()
            if feeds[f].pdate == "":
                for i in dom.xpath('//*[@id="' + k + '"]/p/span/span'):
                    feeds[f].pdate = i.text_content()
            dlist = conv_date(feeds[f].pdate)
            if dlist is None:
                feeds[f].pdate = blist
            else:
                feeds[f].pdate = dlist
                blist = dlist
            f = f + 1
        break

feeds.sort(key=operator.attrgetter('pdate'), reverse=True)

JST = timezone(timedelta(hours=+9), 'JST')

fe = feedgenerator.Atom1Feed(
    title='TrendsWatcher RSS Feed',
    link=baseurl,
    feed_url='/rss/test.xml',
    description='TrendsWatcher RSS Feed',
    author_name='TrendsWatcher',
    pubdate=datetime.now(JST),
    language='jp')

for s in feeds:
    enc = None
    if s.image:
        enc = feedgenerator.Enclosure(url=s.image, length='0', mime_type='image/jpeg')

    fe.add_item(
        title=s.header,
        link=s.link,
        description=s.ptext,
        author_name='TrendsWatcher',
        enclosure=enc,
        pubdate=datetime(int(s.pdate[0]), int(s.pdate[1]), int(s.pdate[2]), tzinfo=timezone(timedelta(hours=9)))
    )

fe.content_type = 'application/atom+xml'
fp = open('atom.xml', 'w')
fe.write(fp, 'utf-8')
fp.close()

