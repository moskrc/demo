# coding: utf-8
import BaseHTTPServer
import shutil
import urllib2
import SocketServer
from urlparse import urlparse
import bs4
import re
import StringIO
import gzip

PORT = 1234

PATTERN = re.compile(ur"\b(\w{3})\b", re.U)


def repl(soup_obj):
    match_contents = soup_obj.findAll(text=PATTERN)
    for match_el in match_contents:
        if match_el.parent.name not in ['a', 'code', 'script', 'img']:
            splitted_text = re.split(PATTERN, match_el)
            text = u' '.join([u'%s™' % x if len(x.strip()) == 3 else x for x in splitted_text])
            match_el.replace_with(text)
    return soup_obj


class Proxy(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        o = urlparse(self.path)
        self.path = 'http://habrahabr.ru' + o.path
        response = urllib2.urlopen(self.path)

        self.send_response(response.code, response.msg)
        content_type = response.info().get('content-type')

        if 'text/html' in content_type:
            if response.info().get('Content-Encoding') == 'gzip':
                compressed_data = response.read()
                compressed_stream = StringIO.StringIO(compressed_data)
                data = gzip.GzipFile(fileobj=compressed_stream).read()
            else:
                data = response.read()

            self.send_header('content-type', content_type)

            soup = bs4.BeautifulSoup(data, 'html5lib')
            matches = soup.findAll('div', {'class': 'content html_format'})
            for m in matches:
                m.replaceWith(repl(m))

            self.end_headers()

            self.wfile.write(soup.encode('utf-8', formatter='html'))
        else:
            for x in response.headers:
                self.send_header(x, response.headers[x])
            self.end_headers()
            shutil.copyfileobj(response, self.wfile)


if __name__ == '__main__':
    SocketServer.ForkingTCPServer(('', PORT), Proxy).serve_forever()
