#!/opt/bin/python3

#-------------------------------------------------------------------------------
# Name:        real-url-proxy-server
# Purpose:     A proxy server to extract real url of DouYu and HuYa live room
#
# Author:      RAiN
#
# Created:     05-03-2020
# Copyright:   (c) RAiN 2020
# Licence:     GPL
#-------------------------------------------------------------------------------

import sys
from abc import ABCMeta, abstractmethod
from http.server import SimpleHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn
import functools
from threading import Timer, Lock
import argparse
from datetime import datetime
from douyu import DouYu
from huya import huya
from bilibili import BiliBili

class RealUrlExtractor:
    __metaclass__ = ABCMeta
    lock = Lock()

    def __init__(self, room, auto_refresh_interval):
        self.room = room
        self.real_url = None
        self.last_valid_real_url = None
        self.auto_refresh_interval = auto_refresh_interval
        self.last_refresh_time = datetime.min
        if self.auto_refresh_interval > 0:
            self.refresh_timer = Timer(self.auto_refresh_interval, self.refresh_real_url)

    def reset_refresh_timer(self, failover):
        if self.auto_refresh_interval > 0:
            self.refresh_timer.cancel()
            if failover:
                refresh_interval = self.auto_refresh_interval / 2
            else:
                refresh_interval = self.auto_refresh_interval
            self.refresh_timer = Timer(refresh_interval, self.refresh_real_url)
            self.refresh_timer.start()

    def refresh_real_url(self):
        RealUrlExtractor.lock.acquire()
        try:
            self._extract_real_url()
        except:
            pass
        RealUrlExtractor.lock.release()

    @abstractmethod
    def _extract_real_url(self):
        failover = True
        if self._is_url_valid(self.real_url):
            self.last_valid_real_url = self.real_url
            failover = False
        elif self.last_valid_real_url is not None:
            self.real_url = self.last_valid_real_url

        self.last_refresh_time = datetime.now()
        self.reset_refresh_timer(failover)
        if failover:
            print('failed to extract real url')
        else:
            print('extracted url: ', end='')
            print(self.real_url)

    @abstractmethod
    def _is_url_valid(self, url):
        return False

    def get_real_url(self, bit_rate):
        if self.real_url is None or bit_rate == 'refresh':
            self._extract_real_url()

class HuYaRealUrlExtractor(RealUrlExtractor):
    def _extract_real_url(self):
        self.real_url = huya(self.room)
        super()._extract_real_url()

    def _is_url_valid(self, url):
        return url is not None and isinstance(url, dict)

    def get_real_url(self, bit_rate):
        super().get_real_url(bit_rate)

        if bit_rate == 'refresh':
            bit_rate = None

        if not self._is_url_valid(self.real_url):
            return None
        if bit_rate is None or len(bit_rate) == 0:
            return self.real_url['BD']
        if bit_rate in self.real_url.keys():
            return self.real_url[bit_rate]
        return None

class DouYuRealUrlExtractor(RealUrlExtractor):
    def _extract_real_url(self):
        try:
            self.real_url = DouYu(self.room).get_real_url()
        except:
            self.real_url = 'None'
        super()._extract_real_url()

    def _is_url_valid(self, url):
        return url is not None and url != 'None'

    def get_real_url(self, bit_rate):
        super().get_real_url(bit_rate)

        if bit_rate == 'refresh':
            bit_rate = None

        if not self._is_url_valid(self.real_url):
            return None
        if bit_rate is None or len(bit_rate) == 0:
            return self.real_url['2000p']
        if bit_rate in self.real_url.keys():
            return self.real_url[bit_rate]

class BilibiliRealUrlExtractor(RealUrlExtractor):
    def _extract_real_url(self):
        try:
            self.real_url = BiliBili(self.room).get_real_url()
        except:
            self.real_url = 'None'
        super()._extract_real_url()

    def _is_url_valid(self, url):
        return url is not None and url != 'None'

    def get_real_url(self, bit_rate):
        super().get_real_url(bit_rate)

        if bit_rate == 'refresh':
            bit_rate = None

        if not self._is_url_valid(self.real_url):
            return None
        if 'hls_url' in self.real_url:
            return self.real_url['hls_url']
        else:
            return self.real_url['flv_url']

class RealUrlRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, processor_maps, auto_refresh_interval, **kwargs):
        self.processor_maps = processor_maps
        self.auto_refresh_interval = auto_refresh_interval
        super().__init__(*args, **kwargs)

    def do_GET(self):
        s = self.path[1:].split('/')
        if len(s) >= 2:
            provider = s[0]
            room = s[1]
            if len(s) > 2:
                bit_rate = s[2]
            else:
                bit_rate = None
            print('provider: %s, room: %s, bit_rate: %s' % (provider, room, bit_rate))

            if provider == 'douyu':
                if provider not in self.processor_maps.keys():
                    self.processor_maps[provider] = {}
                douyu_processor_map = self.processor_maps[provider]

                try:
                    if room not in douyu_processor_map.keys():
                        douyu_processor_map[room] = DouYuRealUrlExtractor(room, self.auto_refresh_interval)

                    real_url = douyu_processor_map[room].get_real_url(bit_rate)
                    if real_url is not None:
                        self.send_response(301)
                        self.send_header('Location', real_url)
                        self.end_headers()
                        return
                except Exception as e:
                    print("Failed to extract douyu real url! Error: %s" % (str(e)))
            elif provider == 'bilibili':
                if provider not in self.processor_maps.keys():
                    self.processor_maps[provider] = {}
                bilibili_processor_map = self.processor_maps[provider]

                try:
                    if room not in bilibili_processor_map.keys():
                        bilibili_processor_map[room] = BilibiliRealUrlExtractor(room, self.auto_refresh_interval)

                    real_url = bilibili_processor_map[room].get_real_url(bit_rate)
                    if real_url is not None:
                        self.send_response(301)
                        self.send_header('Location', real_url)
                        self.end_headers()
                        return
                except Exception as e:
                    print("Failed to extract bilibili real url! Error: %s" % (str(e)))
            elif provider == 'huya':
                if provider not in self.processor_maps.keys():
                    self.processor_maps[provider] = {}
                huya_processor_map = self.processor_maps[provider]

                try:
                    if room not in huya_processor_map.keys():
                        huya_processor_map[room] = HuYaRealUrlExtractor(room, self.auto_refresh_interval)

                    real_url = huya_processor_map[room].get_real_url(bit_rate)
                    if real_url is not None:
                        m3u8_content = '#EXTM3U\n#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1\n' + real_url
                        self.send_response(200)
                        self.send_header('Content-type', "application/vnd.apple.mpegurl")
                        self.send_header("Content-Length", str(len(m3u8_content)))
                        self.end_headers()
                        self.wfile.write(m3u8_content.encode('utf-8'))
                        return
                except Exception as e:
                    print("Failed to extract huya real url! Error: %s" % (str(e)))

        rsp = "Not Found"
        rsp = rsp.encode("gb2312")

        self.send_response(404)
        self.send_header("Content-type", "text/html; charset=gb2312")
        self.send_header("Content-Length", str(len(rsp)))
        self.end_headers()
        self.wfile.write(rsp)

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A proxy server to get real url of live providers.')
    parser.add_argument('-p', '--port', type=int, required=True, help='Binding port of HTTP server.')
    parser.add_argument('-r', '--refresh', type=int, default=7200, help='Auto refresh interval in seconds, 0 means disable auto refresh.')
    args = parser.parse_args()

    processor_maps = {}
    HandlerClass = functools.partial(RealUrlRequestHandler, processor_maps=processor_maps, auto_refresh_interval=args.refresh)
    ServerClass  = ThreadingHTTPServer
    #Protocol     = "HTTP/1.0"

    server_address = ('0.0.0.0', args.port)

    #HandlerClass.protocol_version = Protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print("Serving HTTP on", sa[0], "port", sa[1], "...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print("Server stopped.")
