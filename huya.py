# 获取虎牙直播的真实流媒体地址。
# 虎牙"一起看"频道的直播间可能会卡顿
import requests
import re
import base64
import urllib.parse
import hashlib
import time
import json
import html

class huya:
    def __init__(self, rid, uid = 0):
        self.room_id = rid
        self.user_id = uid
        self.clear_live_url_info()
        self.update_live_url_info()

    def decode_live_url_info(self, srcAntiCode):
        srcAntiCode = html.unescape(srcAntiCode)
        c = srcAntiCode.split('&')
        c = [i for i in c if i != '']
        n = {i.split('=')[0]: i.split('=')[1] for i in c}
        fm = urllib.parse.unquote(n['fm'])
        u = base64.b64decode(fm).decode('utf-8')
        self.hash_prefix = u.split('_')[0]
        self.ctype = n.get('ctype', '')
        self.txyp = n.get('txyp', '')
        self.fs = n.get('fs', '')

    def clear_live_url_info(self):
        self.hash_prefix = None
        self.base_url = None
        self.hls_url = None
        self.stream_name = None
        self.ctype = None
        self.txyp = None
        self.fs = None
        self.t = None

    def update_live_url_info(self):
        try:
            room_url = 'https://www.huya.com/' + str(self.room_id)
            header = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
            }
            response = requests.get(url=room_url, headers=header, timeout=30).text
            liveDataBase64 = re.findall(r'"stream": "([\s\S]*?)"', response)[0]
            if liveDataBase64 != 'null':
                liveData = json.loads(str(base64.b64decode(liveDataBase64), 'utf-8'))
                streamInfoList = liveData['data'][0]['gameStreamInfoList']
                streamInfo = streamInfoList[-1]
                self.stream_name = streamInfo['sStreamName']
                self.base_url = streamInfo['sHlsUrl']
                self.hls_url = streamInfo['sHlsUrl'] + '/' + self.stream_name + '.' + streamInfo['sHlsUrlSuffix']
                sHlsAntiCode = streamInfo['sHlsAntiCode']
                self.decode_live_url_info(sHlsAntiCode)
            else:
                self.clear_live_url_info()
        except:
            self.clear_live_url_info()

    def get_real_url(self, ratio = None):
        if self.hls_url is not None:
            seqid = str(int(time.time() * 1e3 + self.user_id))
            hash0 = hashlib.md5((seqid + '|' + self.ctype + '|100').encode('utf-8')).hexdigest()
            wsTime = hex(int(time.time()) + 24 * 60 * 60).replace('0x', '')
            hash1 = hashlib.md5('_'.join([self.hash_prefix, str(self.user_id), self.stream_name, hash0, wsTime]).encode('utf-8')).hexdigest()
            if ratio is None:
                url = "{}?wsSecret={}&wsTime={}&seqid={}&ctype={}&ver=1&txyp={}&fs={}&u={}&t=100&sv=2106101611".format(
                    self.hls_url, hash1, wsTime, seqid, self.ctype, self.txyp, self.fs, self.user_id)
            else:
                url = "{}?wsSecret={}&wsTime={}&seqid={}&ctype={}&ver=1&txyp={}&fs={}&ratio={}&u={}&t=100&sv=2106101611".format(
                    self.hls_url, hash1, wsTime, seqid, self.ctype, self.txyp, self.fs, ratio, self.user_id)
            return url
        return None


if __name__ == '__main__':
    rid = input('输入虎牙直播间号：\n')
    real_url = huya(rid, 1234567890).get_real_url()
    if real_url is not None:
        print(real_url)
    else:
        print('未开播或直播间不存在')
